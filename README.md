PySDL
=====

Similar projects first:
-----------------------

* The equally named [PySDL on SourceForge](http://sourceforge.net/projects/pysdl). Last update was from 2000. Implemented in C.
* [Pygame](http://www.pygame.org/). Actively developed. Implemented in C. Is not a straight-forward 1:1 binding to SDL but has a different API.

How does this **PySDL** differ?
-------------------------------

* Purely implemented in Python.
* Straight-forward 1:1 binding to SDL.

How is it implemented?
----------------------

It uses [PyCParser](https://github.com/albertz/PyCParser) to automatically parse the SDL headers and to generate a ctypes interface to the library.

