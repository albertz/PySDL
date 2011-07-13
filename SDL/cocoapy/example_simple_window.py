# Simple example of using ctypes with Cocoa to create an NSWindow.

import sys
sys.path.append("..")

from cocoapy import *

def create_window():
    print 'creating window'
    window = send_message('NSWindow', 'alloc')
    frame = NSMakeRect(100, 100, 300, 300)
    window = send_message(window, 'initWithContentRect:styleMask:backing:defer:',
                          frame,
                          NSTitledWindowMask | NSClosableWindowMask | NSMiniaturizableWindowMask | NSResizableWindowMask,
                          NSBackingStoreBuffered,
                          0)
    send_message(window, 'setTitle:', get_NSString("My Awesome Window"))
    send_message(window, 'makeKeyAndOrderFront:', None)
    return window

def create_autorelease_pool():
    pool = send_message('NSAutoreleasePool', 'alloc')
    pool = send_message(pool, 'init')
    return pool

def application_run():
    app = send_message('NSApplication', 'sharedApplication')
    create_autorelease_pool()
    create_window()
    send_message(app, 'run')  # never returns

######################################################################

if __name__ == '__main__':
    application_run()

