#!/usr/bin/python
# -*- coding: utf-8 -*-

import better_exchook
better_exchook.install()

import sys, os
from ctypes import *	
from soundutils import *
import fluidsynth
sdl = None

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

def init_SDL_dll():
	sdl.SDL_Init.argtypes = (c_uint32,)
	sdl.SDL_Init.restype = c_int
	
	sdl.SDL_SetVideoMode.restype = c_SDLSurface_p # screen
	sdl.SDL_SetVideoMode.argtypes = (c_int, c_int, c_int, c_uint32) # width,height,bpp,flags
	
	sdl.SDL_PollEvent.argtypes = (POINTER(c_SDLEvent),)
	sdl.SDL_WaitEvent.argtypes = (POINTER(c_SDLEvent),)

	sdl.SDL_GetTicks.restype = c_uint32
	sdl.SDL_GetTicks.argtypes = ()
	
	sdl.SDL_Quit.restype = None

def sdl_main_loop():
	ev = c_SDLEvent()	
	oldtime = sdl.SDL_GetTicks()

	gain = 1.0
	notevel = 50

	fs = fluidsynth.Synth(gain=gain)

	# create a symlink or just copy such a file there
	sfid = fs.sfload("midisoundfont.sf2")
	fs.program_select(0, sfid, 0, 0)
	
	debug = False
	quit = False
	while not quit:
		while sdl.SDL_PollEvent(pointer(ev)) == 1:
			if ev.type == SDLEventTypes.SDL_QUIT: quit = True
			elif ev.type in [SDLEventTypes.SDL_KEYDOWN, SDLEventTypes.SDL_KEYUP]:
				down = ev.key.state != 0
				sym = ev.key.keysym.sym
				if sym <= 127: sym = chr(sym)			
				if debug: print "SDL keyboard event:", down, repr(sym), '"' + unichr(ev.key.keysym.unicode).encode("utf-8") + '"'
				
				if down and sym == '\x1b': quit = True # ESC
				if down and sym == 160L: debug = not debug
				
				keys = list(
					"asdfghjkl;'\\" +
					"qwertzuiop[]" +
					"1234567890-=")
				if sym in keys:
					note = keys.index(sym) + 52
					print "note", note, "on" if down else "off"
					if down: fs.noteon(0, note, notevel)
					else: fs.noteoff(0, note)
		
		newtime = sdl.SDL_GetTicks()
		len = newtime - oldtime
		oldtime = newtime
		
		# FluidSynth assumes an output rate of 44100 Hz.
		# The return value will be a Numpy array of samples.
		len = 44100 * len / 1000
		if len > 0:
			#print "playing", len, "samples"
			data = fs.get_mono_samples(len)
			play(data)

	fs.delete()


def app_main():
	init_SDL_dll()
	print "loaded SDL"
	
	sdl.SDL_Init(0xFFFF) # init everything
	sdl.SDL_SetVideoMode(640,480,0,0)
	sdl.SDL_EnableUNICODE(1)
	print "initialized SDL"

	sdl_main_loop()
	sdl.SDL_Quit()
	print "quit"

if sys.platform == "darwin":

	sdl = cdll.LoadLibrary("/Library/Frameworks/SDL.framework/SDL")

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
	app_main()
	
