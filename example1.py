#!/usr/bin/python
# -*- coding: utf-8 -*-

import better_exchook
better_exchook.install()

import SDL

debug = True
quit = False

def handle_event(ev):
	global debug, quit
	
	if ev.type == SDL.SDL_EventType.SDL_QUIT: quit = True
	elif ev.type in [SDL.SDL_EventType.SDL_KEYDOWN, SDL.SDL_EventType.SDL_KEYUP]:
		down = ev.key.state != 0
		sym = ev.key.keysym.sym
		if debug: print "SDL keyboard event:", down, repr(sym), '"' + unichr(ev.key.keysym.unicode).encode("utf-8") + '"'
		
		if down and sym == SDL.SDLKey.SDLK_ESCAPE: quit = True
		if down and sym == SDL.SDLKey.SDLK_WORLD_0: debug = not debug


def main_loop():
	ev = SDL.SDL_Event()	
	oldtime = SDL.SDL_GetTicks()
	
	maxfps = 100
	
	global quit
	while not quit:
		while SDL.SDL_PollEvent(SDL.pointer(ev)) == 1:
			handle_event(ev)
			
		newtime = SDL.SDL_GetTicks()
		dt = newtime - oldtime
		oldtime = newtime
		
		waittime = 1000 / maxfps - dt
		if waittime > 0:
			SDL.SDL_Delay(waittime)


def app_main():
	print "loaded SDL"
	
	SDL.SDL_Init(0xFFFF) # init everything
	SDL.SDL_SetVideoMode(640,480,0,0)
	SDL.SDL_EnableUNICODE(1)
	print "initialized SDL"

	main_loop()
	
	SDL.SDL_Quit()
	print "quit"


if __name__ == '__main__':
	print "parsing SDL headers and loading SDL ..."
	SDL.start(app_main)
