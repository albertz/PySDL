import sys, os
import cparser, cparser.caching
from ctypes import *
sdl = None
sdl_image = None

# keep a reference to this module so that it's not garbage collected
orig_module = sys.modules[__name__]

from types import ModuleType
class ModuleWrapper(ModuleType):
	def __getattr__(self, attrib):
		global sdl
		try: return getattr(orig_module, attrib)
		except AttributeError: pass
		if sdl is not None:
			try: return getattr(sdl, attrib)
			except AttributeError: pass
		if sdl_image is not None:
			try: return getattr(sdl_image, attrib)
			except AttributeError: pass
		raise AttributeError, "attrib " + attrib + " not found in module " + __name__
		
# setup the new module and patch it into the dict of loaded modules
new_module = sys.modules[__name__] = ModuleWrapper(__name__)

sdlHeaderDir = None
CParserFunc = cparser.caching.parse
# If we don't want to use caching:
#CParserFunc = cparser.parse

def init_SDL_dll(dll, headerdir):
	global sdlHeaderDir
	sdlHeaderDir = headerdir

	dll = cdll.LoadLibrary(dll)
	parsedState = CParserFunc(headerdir + "/SDL.h")
	
	global sdl
	sdl = parsedState.getCWrapper(dll)

def init_SDLImage_dll(dll, headerdir):
	dll = cdll.LoadLibrary(dll)
	state = cparser.State()
	state.autoSetupSystemMacros()
	
	def findIncludeFullFilename(filename, local):
		import os.path
		if os.path.isabs(filename): return filename
		fn = sdlHeaderDir + "/" + filename
		if os.path.exists(fn): return fn
		return headerdir + "/" + filename
	state.findIncludeFullFilename = findIncludeFullFilename
	
	parsedState = CParserFunc(headerdir + "/SDL_image.h", state)
	
	global sdl_image
	sdl_image = parsedState.getCWrapper(dll)
	
def start(app_main):
	global sdl
	
	if sys.platform == "darwin":	
		init_SDL_dll("/Library/Frameworks/SDL.framework/SDL", "/Library/Frameworks/SDL.framework/Headers")
		init_SDLImage_dll("/Library/Frameworks/SDL_image.framework/SDL_image", "/Library/Frameworks/SDL_image.framework/Headers")
	
		from AppKit import NSApp, NSApplication, NSNotificationCenter, NSApplicationDidFinishLaunchingNotification
		from Foundation import NSAutoreleasePool, NSObject
		pool = NSAutoreleasePool.alloc().init()
		
		class MyApplicationActivator(NSObject):
		
			def activateNow_(self, aNotification):
				NSApp().activateIgnoringOtherApps_(True)
				try:
					app_main()
				except:
					sys.excepthook(*sys.exc_info())
				os._exit(0)
				
		activator = MyApplicationActivator.alloc().init()
		NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
			activator,
			'activateNow:',
			NSApplicationDidFinishLaunchingNotification,
			None,
		)
		
		NSApplication.sharedApplication()
		NSApp().run()
		
		del pool
	
	else:
		init_SDL_dll("SDL", "/usr/include/SDL")
		init_SDL_dll("SDL_image", "/usr/include/SDL_image")
		app_main()
