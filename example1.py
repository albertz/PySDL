#!/usr/bin/python
# -*- coding: utf-8 -*-

import better_exchook
better_exchook.install()

import SDL

debug = True
quit = False

def handle_event(ev):
	global debug, quit
	
	if ev.type == SDL.SDLEventTypes.SDL_QUIT: quit = True
	elif ev.type in [SDL.SDLEventTypes.SDL_KEYDOWN, SDL.SDLEventTypes.SDL_KEYUP]:
		down = ev.key.state != 0
		sym = ev.key.keysym.sym
		if sym <= 127: sym = chr(sym)			
		if debug: print "SDL keyboard event:", down, repr(sym), '"' + unichr(ev.key.keysym.unicode).encode("utf-8") + '"'
		
		if down and sym == '\x1b': quit = True # ESC
		if down and sym == 160L: debug = not debug


def main_loop():
	ev = SDL.c_SDLEvent()	
	oldtime = SDL.sdl.SDL_GetTicks()
	
	maxfps = 100
	
	global quit
	while not quit:
		while SDL.sdl.SDL_PollEvent(SDL.pointer(ev)) == 1:
			handle_event(ev)
			
		newtime = SDL.sdl.SDL_GetTicks()
		dt = newtime - oldtime
		oldtime = newtime
		
		waittime = 1000 / maxfps - dt
		if waittime > 0:
			SDL.sdl.SDL_Delay(waittime)


def app_main():
	print "loaded SDL"
	
	SDL.sdl.SDL_Init(0xFFFF) # init everything
	SDL.sdl.SDL_SetVideoMode(640,480,0,0)
	SDL.sdl.SDL_EnableUNICODE(1)
	print "initialized SDL"

	main_loop()
	
	SDL.sdl.SDL_Quit()
	print "quit"

	
SDL.start(app_main)
