import sys, os
from ctypes import *
sdl = None

def init_SDL_dll(dll, headerdir, explicit=True):
	global sdl
	sdl = cdll.LoadLibrary(dll)
	
	if not explicit:
		from pyclibrary import CParser, CLibrary
		from glob import glob
		headers = CParser(glob(headerdir + "/*.h"))
		
		lib = CLibrary(sdl, headers)
		sdl = lib # this provides the same interface, so we can do this
		
		for t in headers.defs["types"]:
			globals()[t] = sdl("types", t)
	
	else:

		global SDLEventTypes
		global c_SDLSurface_p, c_SDLKey, c_SDLMod
		global c_SDLEvent
		
		c_SDLSurface_p = c_void_p # this suffice for us
		
		c_SDLKey = c_uint32
		c_SDLMod = c_uint32
		
		class c_SDLkeysym(Structure):
			_fields_ = [
				("scancode", c_uint8),
				("sym", c_SDLKey),
				("mod", c_SDLMod),
				("unicode", c_uint16)
				]
		
		class c_SDLKeyboardEvent(Structure):
			_fields_ = [
				("type", c_uint8),
				("which", c_uint8), # which keyboard device
				("state", c_uint8), # 1 - down, 0 - up
				("keysym", c_SDLkeysym)
				]
		
		class c_SDLDummyEvent(Structure):
			_fields_ = [
				("type", c_uint8),
				("data", c_uint8*20) # just some space filler so that we are big enough
				]
		
		class c_SDLEvent(Union):
			_fields_ = [
				("type", c_uint8),
				("key", c_SDLKeyboardEvent),
				("dummy", c_SDLDummyEvent)
				]
		
		class SDLEventTypes:
			# just the ones we need for now
			SDL_KEYDOWN = 2
			SDL_KEYUP = 3
			SDL_QUIT = 12
	
		sdl.SDL_Init.argtypes = (c_uint32,)
		sdl.SDL_Init.restype = c_int
		
		sdl.SDL_SetVideoMode.restype = c_SDLSurface_p # screen
		sdl.SDL_SetVideoMode.argtypes = (c_int, c_int, c_int, c_uint32) # width,height,bpp,flags
		
		sdl.SDL_PollEvent.argtypes = (POINTER(c_SDLEvent),)
		sdl.SDL_WaitEvent.argtypes = (POINTER(c_SDLEvent),)
	
		sdl.SDL_GetTicks.restype = c_uint32
		sdl.SDL_GetTicks.argtypes = ()
		
		sdl.SDL_Delay.restype = None
		sdl.SDL_Delay.argtypes = (c_uint32,)
		
		sdl.SDL_Quit.restype = None
		
	
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
