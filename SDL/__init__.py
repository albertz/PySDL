import sys, os
import cparser
from ctypes import *
sdl = None

# keep a reference to this module so that it's not garbage collected
orig_module = sys.modules[__name__]

from types import ModuleType
class ModuleWrapper(ModuleType):
	def __getattr__(self, attrib):
		global sdl
		try: return getattr(orig_module, attrib)
		except AttributeError: pass
		if sdl is not None:
			return getattr(sdl, attrib)
		raise AttributeError, "attrib " + attrib + " not found in module " + __name__
		
# setup the new module and patch it into the dict of loaded modules
new_module = sys.modules[__name__] = ModuleWrapper(__name__)

def init_SDL_dll(dll, headerdir, explicit=True):	
	dll = cdll.LoadLibrary(dll)
	parsedState = cparser.parse(headerdir + "/SDL.h")
	
	global sdl
	sdl = parsedState.getCWrapper(dll)
	
def start(app_main):
	global sdl
	
	if sys.platform == "darwin":	
		init_SDL_dll("/Library/Frameworks/SDL.framework/SDL", "/Library/Frameworks/SDL.framework/Headers")
	
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
		app_main()
