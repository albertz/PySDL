import sys, os
import cparser, cparser.caching, cparser.cwrapper
from ctypes import *
wrapper = cparser.cwrapper.CWrapper()

# keep a reference to this module so that it's not garbage collected
orig_module = sys.modules[__name__]

from types import ModuleType
class ModuleWrapper(ModuleType):
	def __getattr__(self, attrib):
		global wrapper
		try: return getattr(orig_module, attrib)
		except AttributeError: pass
		try: return getattr(wrapper.wrapped, attrib)
		except AttributeError: pass
		raise AttributeError, "attrib " + attrib + " not found in module " + __name__ + " nor in wrapper " + str(wrapper)
	def __dir__(self):
		global wrapper
		return dir(orig_module) + list(wrapper.wrapped.__class__.__dict__)

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
	
	global wrapper
	wrapper.register(parsedState, dll)

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

	global wrapper
	wrapper.register(parsedState, dll)

def get_lib_binheader(name, alt_header_pathname=None):
	import os.path
	for prefix in ("/usr/local","/usr"):
		for binpostfix in ("-1.3.so.0","-1.3.so","-1.2.so",".so"):
			bin = prefix + "/lib/lib" + name + binpostfix
			if os.path.exists(bin):
				def findHeaders(name):
					for headerpostfix in ("","1.3","-1.3","1.2","-1.2"):
						header = prefix + "/include/" + name + headerpostfix
						if os.path.exists(header): return header
					return None
				header = findHeaders(name)
				if header is None and alt_header_pathname is not None:
					header = findHeaders(alt_header_pathname)
				if header is None:
					print "Warning: found", bin, "but no matching headers"
					continue
				return bin, header
	print "Error: didn't found libary", name
	# return dummy
	return "/usr/lib/lib" + name + ".so", "/usr/include/" + name
	
def start(app_main = None):
	global sdl
	
	if sys.platform == "darwin":	
		init_SDL_dll("/Library/Frameworks/SDL.framework/SDL", "/Library/Frameworks/SDL.framework/Headers")
		init_SDLImage_dll("/Library/Frameworks/SDL_image.framework/SDL_image", "/Library/Frameworks/SDL_image.framework/Headers")
	
		using_cocoapy = False
		try:
			from AppKit import NSApp, NSApplication, NSNotificationCenter, NSApplicationDidFinishLaunchingNotification
			from Foundation import NSAutoreleasePool, NSObject
		except ImportError:
			using_cocoapy = True
			import cocoapy as cp
			
		if not using_cocoapy:
			pool = NSAutoreleasePool.alloc().init()
	
			class MyApplicationActivator(NSObject):
	
				def activateNow_(self, aNotification):
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
			NSApp().activateIgnoringOtherApps_(True)
			NSApp().finishLaunching()
			NSApp().updateWindows()
			if app_main is not None:
				NSApp().run()
				del pool
		else:
			import cocoapy as cp
			init_SDL_dll("/Library/Frameworks/SDL.framework/SDL", "/Library/Frameworks/SDL.framework/Headers")
			init_SDLImage_dll("/Library/Frameworks/SDL_image.framework/SDL_image", "/Library/Frameworks/SDL_image.framework/Headers")
			print 'Done loading SDL'

			pool = cp.send_message('NSAutoreleasePool', 'alloc')
			pool = cp.send_message(pool, 'init')

			class MyApplicationActivator_Impl(object):
				MyApplicationActivator = cp.ObjCSubclass('NSObject', 'MyApplicationActivator')

				@MyApplicationActivator.method('@')
				def init(self):
					self = cp.ObjCInstance(cp.send_super(self, 'init'))
					return self

				@MyApplicationActivator.method('v@')
				def activateNow(self, aNotification):
					try:
						app_main()
					except:
						sys.excepthook(*sys.exc_info())
					os._exit(0)

			MyApplicationActivator = cp.ObjCClass('MyApplicationActivator')
			activator = MyApplicationActivator.alloc().init()
			center = cp.send_message('NSNotificationCenter', 'defaultCenter')
			cp.send_message(center, 'addObserver:selector:name:object:',
				activator,
				cp.get_selector("activateNow"),
				cp.get_NSString("NSApplicationDidFinishLaunchingNotification"),
				None)

			app = cp.send_message('NSApplication', 'sharedApplication')
			cp.send_message('NSApp', 'finishLaunching')
			cp.send_message('NSApp', 'updateWindows')
			cp.send_message('NSApp', 'activateIgnoringOtherApps', True)
			if app_main is not None:
				cp.send_message(app, 'run')			
	else:
		init_SDL_dll(*get_lib_binheader("SDL"))
		init_SDLImage_dll(*get_lib_binheader("SDL_image","SDL"))
		if app_main is not None:
			app_main()
