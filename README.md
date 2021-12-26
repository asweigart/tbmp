tbmp - A data structure for terminal-based bitmaps.
======

By Al Sweigart al@inventwithpython.com

A Python module for displaying bitmaps in the terminal as strings of block
characters. Text characters are twice as tall as they are wide, so each
text character can represent two pixels. This module uses the block
characters 9600, 9604, 9608, and the space character to represent pixels.

Since they are still text characters, the "pixels" can be copy/pasted just
like any other text. This also makes it easy to display them in terminal
windows or IDEs or web apps. The simplicity makes this module flexible
for displaying graphics in a terminal window.

This module is intended to be used to teach programming concepts such as
nested for loops, simple 2D graphics, cellular automata such as Conway's
Game of Life, and other concepts.

The applyFunc() method especially can be used for generating algorithmic
art.

The demo folder has example programs that use terminal bitmaps. They
include Conway's Game of Life, a Mona Lisa render from a large hexadecimal
number, and a rotating cube animation.

This module has no dependencies and fits in a single .py file, so it can
be installed through pip or just copied to a tbmp.py file for importing.
Copy the singleFileVersion/tbmp.py file to the folder your Python script
is in to import tbmp without installing it via pip.

Installation
------------

To install with pip, run:

    pip install tbmp

Quickstart Guide
----------------

    >>> from tbmp import *
    >>> b = TBMP(10, 10)  # Create a 10x10 bitmap.
    >>> b.width, b.height, b.size
    (10, 10, (10, 10))
    >>> for i in range(10):
    ...   b[i, i] = True
    ...   b[b.width - 1 - i, i] = True
    ...
    >>> print(b)
    ▀▄      ▄▀
      ▀▄  ▄▀
        ██
      ▄▀  ▀▄
    ▄▀      ▀▄
    >>> print(b.framed)
    ┌──────────┐
    │▀▄      ▄▀│
    │  ▀▄  ▄▀  │
    │    ██    │
    │  ▄▀  ▀▄  │
    │▄▀      ▀▄│
    └──────────┘
    >>> b.invert()
    >>> print(b)
    ▄▀██████▀▄
    ██▄▀██▀▄██
    ████  ████
    ██▀▄██▄▀██
    ▀▄██████▄▀
    >>> b.shift(4, 1)
    >>> print(b)
         ▄▄▄▄▄
        █▄▀███
        ███▄▀▀
        ███▀▄▄
        █▀▄███
    >>> b.randomize()  # Set pixels randomly
    >>> print(b)
    ▄█▀█▄ ▄█▀▀
     ▀▄█  ▄ ▄▀
    ▄ █▀█▀▄ ▀▄
    ▀▄█▀▀  █▀▄
    █▀▀██▄▄ ▀
    >>> b.randomize(0.90)  # Set 90% of pixels on, at random.
    >>> print(b)
    █▄█████▄██
    ▀██▀██████
    ██▄███████
    ▄███████▄█
    █▄██▄█████
    >>> b.randomize(0.25)  # Set 25% of pixels on, at random.
    >>> print(b)
    ▄ ▄▄ █  ▄
    ▀▄▄▄  ▀
           ▀▄▄
     ▄  ▀▄  ▀
     ▄  ▀  ▀
    >>> b.image().save('myBitmap.png')
    >>> b.image().show()  # Have Pillow show a preview of the image.

The `applyFunc()` function is useful for creating algorithmic art. You give it a lambda function (or string of a lambda function) that takes an x and y integer arguments and if the expression is zero, the pixel at those coordinates is black and if nonzero the pixel is white:

    >>> b2 = TBMP()  # Create a bitmap slightly smaller than the terminal window.
    >>> b2.applyFunc('(x ^ y) % 5')
    >>> print(b2)
    ▄▀██▀▄████▄▀██▀▄████▄▀██▀▄████▄▀██▀▄████▄▀██▀▄████▄▀██▀▄████▄▀██▀▄████▄▀██▀▄███
    ██▄▀██▀▄▄▀██▀▄████████▄▀██▀▄▄▀██▀▄████████▄▀██▀▄▄▀██▀▄████████▄▀██▀▄▄▀██▀▄█████
    ▀▄██▄▀████▀▄██▄▀▄▀████████▄▀▀▄████████▀▄▀▄██▄▀████▀▄██▄▀▄▀████████▄▀▀▄████████▀
    ██▀▄██▄▀▀▄██▄▀████▄▀████▄▀████▀▄████▀▄████▀▄██▄▀▀▄██▄▀████▄▀████▄▀████▀▄████▀▄█
    ██▄▀██▀▄▄▀██▀▄██▀▄████▄▀████▄▀██▄▀██▀▄████▀▄████████▄▀████▄▀██▀▄██▀▄████▀▄████▄
    ▄▀██▀▄████▄▀██▀▄██▀▄▄▀████████▄▀██▄▀██▀▄▀▄████████████▄▀▄▀██▀▄██▀▄████████▀▄▄▀█
    ██▀▄██▄▀▀▄██▄▀████▄▀▀▄██▄▀██████▀▄██▄▀████████▀▄▄▀████████▀▄██▄▀██████▀▄██▄▀▀▄█
    ▀▄██▄▀████▀▄██▄▀▄▀████▀▄██▄▀██████▀▄██▄▀████▀▄████▄▀████▀▄██▄▀██████▀▄██▄▀████▀
    ████▄▀██▀▄████▄▀▄▀██▀▄████▄▀██▀▄██▄▀██▀▄████▄▀████▀▄████▄▀██▀▄██▄▀██▀▄████▄▀██▀
    ██████▄▀██▀▄▄▀████▄▀██▀▄▄▀██▀▄██▄▀██▀▄████████▄▀▀▄████████▄▀██▀▄██▄▀██▀▄▄▀██▀▄█
    ▄▀████████▄▀▀▄██▀▄██▄▀████▀▄██▄▀██▀▄██▄▀▄▀████████████▀▄▀▄██▄▀██▀▄██▄▀████▀▄██▄
    ██▄▀████▄▀████▀▄██▀▄██▄▀▀▄██▄▀██▀▄██▄▀████▄▀████████▀▄████▀▄██▄▀██▀▄██▄▀▀▄██▄▀█
    ▀▄████▄▀████▄▀████▄▀██▀▄▄▀██▀▄██████▄▀████▄▀██▀▄▄▀██▀▄████▀▄██████▄▀██▀▄▄▀██▀▄█
    ██▀▄▄▀████████▄▀▄▀██▀▄████▄▀██▀▄██████▄▀▄▀██▀▄████▄▀██▀▄▀▄██████▄▀██▀▄████▄▀██▀
    ██▄▀▀▄██▄▀████████▀▄██▄▀▀▄██▄▀██▄▀████████▀▄██▄▀▀▄██▄▀████████▀▄██▀▄██▄▀▀▄██▄▀█
    ▄▀████▀▄██▄▀████▀▄██▄▀████▀▄██▄▀██▄▀████▀▄██▄▀████▀▄██▄▀████▀▄██▀▄██▄▀████▀▄██▄
    ██▀▄████▄▀██▀▄████▄▀██▀▄████▄▀██▄▀██▀▄████▄▀██▀▄████▄▀██▀▄████▄▀████▄▀██▀▄████▄
    ▀▄████████▄▀██▀▄▄▀██▀▄████████▄▀██▄▀██▀▄▄▀██▀▄████████▄▀██▀▄▄▀████████▄▀██▀▄▄▀█
    ██████▀▄▀▄██▄▀████▀▄██▄▀▄▀██████▀▄██▄▀████▀▄██▄▀▄▀████████▄▀▀▄██▄▀████████▄▀▀▄█
    ████▀▄████▀▄██▄▀▀▄██▄▀████▄▀██████▀▄██▄▀▀▄██▄▀████▄▀████▄▀████▀▄██▄▀████▄▀████▀
    ▄▀██▀▄████▀▄████████▄▀████▄▀██▀▄██▄▀██▀▄▄▀██▀▄██▀▄████▄▀████▄▀██▀▄████▄▀████▄▀█
    ██▄▀██▀▄▀▄████████████▄▀▄▀██▀▄██▄▀██▀▄████▄▀██▀▄██▀▄▄▀████████▄▀██▀▄▄▀████████▄

The `tbpm` module also comes with a `cube()` and `monaLisa()` function that return premade TBMP objects:

    >>> print(cube())
           ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
         ▄▀█           ▄▀█
      ▄▀▀  █        ▄▀▀  ▀▄
    ▄█▄▄▄▄▄▄█▄▄▄▄▄▄▀      █
    █       █     █       █
    █       █     ▀▄      █
     █      ▀▄     █      ▀▄
     █       █     █       █
     █      ▄▀▀▀▀▀▀█▀▀▀▀▀▀█▀
     ▀▄  ▄▄▀       ▀▄  ▄▄▀
      █▄▀           █▄▀
      ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
    >>> print(monaLisa())
    ▀▄▀ █ ▀▀▄▀ ▀▄▀▀▄▀ ▀▄▀ ▀▄▀▄▀▀▄ ▄▀▄▀ ▄ █ █ ▀▄▀ ▀▄▀ ▀ ▄▀▄▀ ▀ █ ▀▄▀ █ █
    ▄ █ ▄▀▄ ▀▄▀▄ ▀  ▀▀  ▀▀▄▄ ▄ ▄  ▀▄ ▀▀▄ ▀▄ █ ▄▀▄ ▀ █ ▀▄  █ █ ▄▀▄ █  █▄
    ▄▄▀ ▄▄▀▄▀ ▄▄▀▀▀▄▀▄▀ █ ▄ ▀▄▄▀ █ ▀▄▀▄ █ ▄ ▄▀ █ ▀▀▄ ▀▄▀▀ ▄ █ ▄▀ ▄▄▀▄▄▄▀
    ▄▄▀▄▄ ▄ █  █ █▄ █ █ ▄▀▄█ ▄ █ █ █▄ █ █▄▀▄ █ ▄▀▀▄▀█ ▄▀▀▄▀▄ █ █▄ █ ▄ █
     ▀▄▀▄█ █ █▀ █ ▄▀▄▀▄▀▄▀ ▄▀▄▀▄▀ ▀       ▀▄▀▄▀▄▀▄▄ ▀▄▄▀▄▄▀▄▀▄▀▄▀▄▄▀▄▀█
    █ █▄ █▄ █ ▀█ █ █ █ █▄▀█ █ ▀▀   ▀▄         ▀▄▀▄▀▀▄ █▄▄ █ █ █ █ █ █ █▄
    ▄▀ █▀ █▄▀█▀▄▀▄▀▄█▀▄▄▀▄▀█▄▀ ▄▄█▀▄▄ ▀        ▀▄▄█▀▄▀▄▄▀█ █▄▀▄█ █▄▀▀▀▄▄
    ▀█ ▀█ █ █ ██▄▀█ █▀▄▀██ █  █▄███▄██ ▀▄        ▄█▄▀▄▄█ █▀▄▀█▄ █ █▀█▄█
    ▀▄█▀█▀▄█▀█▄▄▀█▄▀█▄▀█ █▀  ▀▄█▄▀██▄▀█▄ ▄        ▄▀▀▄ █▄▀▀▄█▀▀█▀▄█▄▀▄█▀
    ▄▄ ▀█▄ ▄▀▄▀█ ██ ██ ██ ▀  █▄███▄███▄█ █        ▀ ▀▄▄ ▀▀█ ██ ██ █▄▀▄▀▀
      ▀  ▄ ▀▄▀ ▀▄ ▀▀▄▀█▀█▀   ▀  ▀▄▀  ▄ ▀  ▀        ▀▄  ▄▀ ▄▀▄██ ██▄▄▀▄▀▄
      ▀▄  ▀▄  ▀▄  ▀ █▄▀▀▄▀   █ █ ██ ▄█▄ █▄▀         ▄ ▄ ▄ ▄ █▄▀█▄ █ █ █
     ▄ ▄ ▀ ▀ ▀   ▀ ▀  ▄ ▄ ▄  ██▀█▄▄▀▄█▄█▄█ ▀       ▄ ▄ ▄     █▀▄▀█ █ ▀▄▀
     ▄   ▀  ▀  ▀▄ ▄           ██ ██ ▄▀█▄▄              ▀ ▀▀▀ █ ▀ ▀▄ ▀ ▀
        ▄ ▀ ▀▄ ▀    ▀  ▄    ▀ ▀▄█▄  ▀▀█ ▄ ▄ ▄      ▄   ▄   ▀   ▀ ▀  ▀  ▀
     ▄   ▄    ▄ ▄   ▀   ▀     ▀▄▄▀█  █ ▀▄    ▀      ▀   ▄   ▀ ▀▄ ▀  ▀▄
       ▄    ▀     ▄  ▀ ▄ ▄      ▀█▄▀▄▀▀              ▀ ▀  ▄  ▀     ▄  ▄
       ▄    ▀  ▀  ▄   ▄ ▄  ▄      ▀                   ▀ ▄  ▀  ▀ ▀ ▄ ▄ ▄
          ▀  ▀  ▀   ▀▄ ▀▄          ▀▄ ▀ ▄  ▀     ▄   ▄  ▄     ▄  ▄   ▄
     ▄     ▀▄ ▄ ▀ ▀▄ ▀  ▀▄    ▄    █ █  █ █ ▀▄        ▀   ▀ ▀ ▄▀▄ ▀▄  ▀
       ▀ ▄ ▀ ▄  ▄     ▀          ▄▄█▄█▀▄▄█ █▄          ▄  ▀  ▄ █  ▀  ▄ ▀
    ▄     ▀▄   ▄ ▀     ▀  ▄    ██▄█▄█▀█▄▀██▄▀  ▀ ▀        ▀█▄▀▄▄ ▀▄  ▀▄
      ▀ ▄   ▄▀▄  ▀  ▄        ▄▀█▄█▄█▀██▀██▄█▀▄      ▄    ▀   ▀▄ ▀ ▄▀▄
     ▀   ▀   ▀▄▀ ▀  ▄ ▀    ▄▄▄▀██▀██▀███▄▀█▄▀  ▀     █     ▀ ▄ ▀▀▀▄ ██▄
      ▀ ▄ ▀    ▀ ▀▄▄      ▄▄▀█▀█▀██▀███▀███▄▀▄ ▄▀▀▀▀  ▀          ▀ ▄ ▄▄▀
     ▄   ▀▄ ▀ █▄▄          ▀▀██▀████▄███▄██ █    ▀                    ▀▄
       ▄ ▀ ▀ ▀ ▄       ▄   ▀ ▄ ▀▄▀▀▀█▀█▀█ ▀  ▄     ▄   ▄       ▀ ▀ ▀ ▄
    ▀   █  ▀▄  █ ▀      ▀▄     ▄ ▀ ▄  ▄  ▄               ▀        ▄  ▀
          ▀  ▀    ▀          ▄   ▄  ▀  ▄        ▄  ▄ ▄         ▄     ▄
    ▀   ▀▄ ▀▄▄       ▄        ▀                      ▄  ▀▄       ▀ ▄
      ▀▄▀▄▀▄ ▀▀    ▀              ▀  ▀     ▀       ▀                 ▀
    ▀    ▄  ▀  ▄       ▀   ▄  ▄      ▄                         ▀   ▀  ▀
    ▄  ▀   ▄      ▄     ▄        ▀             ▀                    ▄
       ▄           ▀             ▄     ▄                  ▀  ▄       ▄
    ▄         ▀                          ▄      ▀    ▀
     ▀    ▀    ▄ ▄   ▄   ▀   ▀    ▀                              ▀    ▀
    ▄       ▀  ▄   ▀    ▄ ▄                         ▄       ▄
     ▀  ▄   ▀▄  ▀  ▀ ▄▄▄▀██▀█▄▀▄ ▄        ▀           ▀       ▄
                 ▀    ▄▀█ █▀▄█▄█▀▄▀▄                               ▀
                  ▀     ▀▄ ▀ █ ▀█ █▀██▄     ▄         ▄      ▄
     ▄                ▄ ▄ ▀▄▀▄▀▀▄▀▄▄ ▀ ▀▄▀ ▀  ▀ ▀ ▀ ▀             ▀
         ▄          ▄ ▄ ▀█   ▀ █▄  ▀█▄   ▀ ▀▄   ▄      ▄
       ▀        ▀   ▄ ▄▀ █▀▀ ▀   ▀▄▄  ▀▄     ▄      ▄             ▀   ▀
            ▀         ▀▄ ▀▀▀  ▀    ▀    ▀▄                 ▀
                     ▀ ▄▀    ▄  ▄   ▄
                         ▄                                       ▀
                ▄
                                            ▀
        ▀           ▀             ▀                                ▀
                            ▀


Contribute
----------

If you'd like to contribute to tbmp, check out https://github.com/asweigart/tbmp
