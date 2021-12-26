"""tbmp - A data structure for terminal-based bitmaps.
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

This module has no dependencies and fits in a single .py file, so it can
be installed through pip or just copied to a tbmp.py file for importing.
"""


# TODO - make this module thread safe?

import array, sys, os, random, shutil

"""The Pillow module isn't required nor automatically installed when
tbmp is installed. But the png() function and importing bitmap image
files to __init__() are features that depend on Pillow."""
PILLOW_INSTALLED = True  # Set to True if Pillow is installed.
try:
    from PIL import Image, ImageDraw, ImageColor
except ImportError:
    PILLOW_INSTALLED = False

__version__ = '0.1.0'

# Constants for the block characters used to represent pixels:
TOP_BLOCK    = chr(9600)
BOTTOM_BLOCK = chr(9604)
FULL_BLOCK   = chr(9608)

# Constants for line characters for the framed() method:
UP_DOWN_CHAR    = chr(9474)
LEFT_RIGHT_CHAR = chr(9472)
DOWN_RIGHT_CHAR = chr(9484)
DOWN_LEFT_CHAR  = chr(9488)
UP_RIGHT_CHAR   = chr(9492)
UP_LEFT_CHAR    = chr(9496)


def size():
    """Returns the size (as a (width, height) tuple) of terminal bitmap
    appropriate given size of the terminal window.

    Defaults to 79, 44.

    The width is reduced by 1 because on Windows, the Command
    Prompt automatically adds newlines when something is printed in the
    rightmost column.

    The height is reduced by 2 because to make space for an interactive
    shell >>> prompt."""
    w, h = shutil.get_terminal_size()  # Returns 80 x 24 by default.
    w -= 1
    h -= 2
    h *= 2 # Text characters can each represent two pixels, so double the height.
    return w, h


class TBMPException(Exception):
    """Exceptions raised by the tbmp module raise TBMPException or a
    subclass of TBMPException. If the tbmp module ever raises an exception
    that isn't TBMPException or a subclass, it is likely a bug in tbmp."""
    pass


class TBMP:
    def __init__(self, width=None, height=None, data=None, default=False, silence=False): # TODO - come up with better name than "silence"
        """Create a new terminal bitmap object. The default size is 80x24
        since that's historically the default size of terminals.

        Args:
            width (int): The width of the bitmap in pixels. If None, it is
                the width of the terminal window, minus one (or 79). The
                minus one is to account for automatic newlines that Windows'
                Command Prompt adds. Defaults to None.
            height (int): The height of the bitmap in pixels. If None, it is
                twice the height of the terminal window minus 2 so that
                it doesn't take up the full window (or 48). Defaults to
                None.
            data (iterable, TBMP): If this is an iterable, it's the pixels to set to the opposite of
                the `default` argument. Defaults to None, where all the pixels
                are set to the `default` argument. If this is an iterable, the
                values should be a tuple of (x, y) integer coordinates.
                This can also be a string of block characters, such as the output of a different
                TBMP object. Or it can be a string of an two-color image file to load data from.
            default (bool): The Boolean value all the pixels in the bitmap
                start as. Defaults to False.
            silence (bool): If True, setting out of bounds pixels doesn't
                raise an exception; it simply does nothing. If False, it
                raises a TBMPException.
        """

        # TODO - should bitmap be able to be a multiline string of the block characters?
        if data is not None and isinstance(data, TBMP):
            # Copy the `data` terminal bitmap to this terminal bitmap:
            if width is not None or height is not None:
                raise TBMPException('When passing a TBMP object for the data parameter, width and height arguments must be left out.')
            self._width = data._width
            self._height = data._height
            self._silence = data._silence
            self._bitmap = data._bitmap[:]
            return
        elif data is not None and isinstance(data, str):
            # Create the bitmap from a multiline string of box characters in the data parameter:
            if len(data) == 0:
                raise TBMPException('If data is a string, it cannot be a blank string.')
            lines = data.split('\n')
            self._width = max([len(line) for line in lines])
            self._height = len(lines) * 2  # Each line of text represents two rows in the bitmap.
        else:
            # Create a blank bitmap based on the width and height parameters:
            self._width, self._height = shutil.get_terminal_size()
            self._width -= 1  # Account for Windows' Command Prompt adding a newline when something is printed in the rightmost column.
            self._height -= 2  # By reducing the height by 2, the prompt in the interactive shell on the bottom line won't hide the top line when this bitmap is printed.
            self._height *= 2  # Note that terminals display two terminal bitmap "pixels" per text character.

            if width is not None:
                if not isinstance(width, int) or width < 1:
                    raise TBMPException('width arg must be an int greater than 0')
                self._width = width
            if height is not None:
                if not isinstance(height, int) or height < 1:
                    raise TBMPException('height arg must be an int greater than 0')
                self._height = height

        if self._width == 0:
            raise TBMPException('width argument cannot be 0')
        if self._height == 0:
            raise TBMPException('height argument cannot be 0')

        self._silence = silence

        if default:
            # Start with the bitmap completely full.
            self.fill()
        else:
            # Start with the bitmap completely empty.
            self.clear()

        if data is not None:
            if isinstance(data, str):
                for i, line in enumerate(lines):
                    for x, char in enumerate(line):
                        if char == ' ':
                            self[x, i * 2] = False
                            self[x, i * 2 + 1] = False
                        elif char == TOP_BLOCK:
                            self[x, i * 2] = True
                            self[x, i * 2 + 1] = False
                        elif char == BOTTOM_BLOCK:
                            self[x, i * 2] = False
                            self[x, i * 2 + 1] = True
                        elif char == FULL_BLOCK:
                            self[x, i * 2] = True
                            self[x, i * 2 + 1] = True
            else:
                # Prepopulate the bitmap for the pixels specified in the `data` iterable:
                for x, y in data:
                    self[x, y] = not default


    def applyFunc(self, funcStr):
        """Apply a lambda function to every pixel in the terminal bitmap.
        This lambda function takes two int arguments (x and y) and returns
        an int or bool. If the return value is True, the pixel at those
        x and y coordinates is set, and if False the pixel is cleared.

        Args:
           funcStr (str, callable): TODO
        """
        if isinstance(funcStr, str):
            # A vague attempt at mitigating malicious input since func is passed to eval(). Don't rely on this for security.
            if ';' in funcStr or 'import' in funcStr or 'open' in funcStr:
                raise Exception('funcStr argument as a string must only have a lambda funciton')

            if not funcStr.strip().replace(' ', '').lower().startswith('lambdax,y:'):
                funcStr = 'lambda x, y:' + funcStr
            func = eval(funcStr)

        for x in range(self._width):
            for y in range(self._height):
                try:
                    self[x, y] = func(x, y)
                except:
                    self[x, y] = False



    def png(self, fg='white', bg='black', fgAlpha=255, bgAlpha=255):
        if not PILLOW_INSTALLED:
            raise Exception('The png() function requires the Pillow module to be installed.')

        fg = ImageColor.getcolor(fg, 'RGB')
        if fgAlpha < 255:
            # Set the transparency of the foreground color:
            fg = (fg[0], fg[1], fg[2], fgAlpha)

        bg = ImageColor.getcolor(bg, 'RGB')
        if bgAlpha < 255:
            # Set the transparency of the foreground color:
            bg = (bg[0], bg[1], bg[2], bgAlpha)

        if fgAlpha < 255 or bgAlpha < 255:
            colorMode = 'RGBA'
        else:
            colorMode = 'RGB'
        im = Image.new(colorMode, (self._width, self._height), bg)

        draw = ImageDraw.Draw(im)
        pixels = []
        for x in range(self._width):
            for y in range(self._height):
                if self[x, y]:
                    pixels.append((x, y))

                    # Make calls to draw.point() with 10k pixel chunks
                    # to keep memory usage from getting too high:
                    if len(pixels) > 10000:
                        draw.point(pixels, fill=fg)
                        pixels.clear()
        draw.point(pixels, fill=fg)
        return im



    def clear(self):
        # Make the bitmap completely empty.
        numBytesNeeded = (self._width * self._height) // 8
        if (self._width * self._height) % 8 > 0:
            numBytesNeeded += 1
        # It's faster to replace the array. in _bitmap than set all the values to 0:
        self._bitmap = array.array('B', b'\x00' * numBytesNeeded)


    def fill(self):
        # Make the bitmap completely full.
        numBytesNeeded = (self._width * self._height) // 8
        if (self._width * self._height) % 8 > 0:
            numBytesNeeded += 1
        # It's faster to replace the array. in _bitmap than set all the values to 255:
        self._bitmap = array.array('B', b'\xFF' * numBytesNeeded)


    def randomize(self, weight=0.50):
        """Set the pixels in the terminal bitmap randomly. The weight
        determines how many pixels are True. A weight of 1.0 means they'll
        all be True, a weight of 0.0 means they'll all be False, and 0.5
        means that they are randomly half True and half False.

        Note that due to how the code is written, using a weight of 0.5
        is currently about 20x faster than a non-0.5 weight."""
        numBytesNeeded = (self._width * self._height) // 8
        if (self._width * self._height) % 8 > 0:
            numBytesNeeded += 1

        if weight == 0.50:
            self._bitmap = array.array('B', random.randbytes(numBytesNeeded))
        else:
            # Use the weighted percentage of `weight` to set the pixels:
            for i in range(numBytesNeeded):
                # Create a byte to set the array.array byte to in _bitmap:
                oneByte = 0
                for j in range(8):
                    if random.random() < weight:
                        oneByte += 1
                    if j != 7:
                        # Don't shift on the last bit.
                        oneByte = oneByte << 1
                self._bitmap[i] = oneByte


    def invert(self):
        for x in range(self._width):
            for y in range(self._height):
                self[x, y] = not self[x, y]


    def toggle(self, x, y):
        """Toggle the pixel at the x, y coordinates: True becomes False and
        False becomes True."""
        self[x, y] = not self[x, y]


    def flipHorizontal(self):
        """Flip all the pixels in the terminal bitmap horizontally.

        If we flip this bitmap horizontally:
        ████
        ████
            ▀▄
              ▀▄
                ▀▄

        ...it will look like this:
              ████
              ████
            ▄▀
          ▄▀
        ▄▀
        """
        for x in range(self._width // 2):
            for y in range(self._height):
                self[x, y], self[self._width - x - 1, y] = self[self._width - x - 1, y], self[x, y]


    def flipVertical(self):
        """Flip all the pixels in the terminal bitmap vertically.

        If we flip this bitmap vertically:
        ████
        ████
            ▀▄
              ▀▄
                ▀▄
        ...it will look like this:
                ▄▀
              ▄▀
            ▄▀
        ████
        ████
        """
        for x in range(self._width):
            for y in range(self._height // 2):
                self[x, y], self[x, self._height - y - 1] = self[x, self._height - y - 1], self[x, y]


    def mirrorLeftToRight(self):
        """Takes the pixels on the left half of the terminal bitmap and
        copies them to the right half to make a symmetrical bitmap. The
        pixels on the right half will be overwritten."""
        for x in range(self._width // 2):
            for y in range(self._height):
                self[self._width - x - 1, y] = self[x, y]


    def mirrorRightToLeft(self):
        """Takes the pixels on the right half of the terminal bitmap and
        copies them to the left half to make a symmetrical bitmap. The
        pixels on the left half will be overwritten."""
        for x in range(self._width // 2):
            for y in range(self._height):
                self[x, y] = self[self._width - x - 1, y]


    def mirrorTopToBottom(self):
        """Takes the pixels on the top half of the terminal bitmap and
        copies them to the bottom half to make a symmetrical bitmap. The
        pixels on the bottom half will be overwritten."""
        for x in range(self._width):
            for y in range(self._height // 2):
                self[x, self._height - y - 1] = self[x, y]


    def mirrorBottomToTop(self):
        """Takes the pixels on the bottom half of the terminal bitmap and
        copies them to the top half to make a symmetrical bitmap. The
        pixels on the top half will be overwritten."""
        for x in range(self._width):
            for y in range(self._height // 2):
                self[x, y] = self[x, self._height - y - 1]


    def shift(self, xOffset, yOffset):
        if xOffset > 0:
            # Shifting the bitmap to the right:
            for y in range(self._height):
                for ix in range(self._width - xOffset):
                    self[self._width - 1 - ix, y] = self[self._width - 1 - ix - xOffset, y]
            # Blank out the left side of the bitmap:
            for y in range(self._height):
                for ix in range(xOffset):
                    self[ix, y] = False
        if xOffset < 0:
            xOffset = -xOffset
            # Shifting the bitmap to the left:
            for y in range(self._height):
                for ix in range(self._width - xOffset):
                    self[ix, y] = self[ix + xOffset, y]
            # Blank out the right side of the bitmap:
            for y in range(self._height):
                for ix in range(xOffset):
                    self[self._width - 1 - ix, y] = False
        if yOffset > 0:
            # Shifting the bitmap down:
            for x in range(self._width):
                for iy in range(self._height - yOffset):
                    self[x, self._height - 1 - iy] = self[x, self._height - 1 - iy - yOffset]
            # Blank out the top side of the bitmap:
            for x in range(self._width):
                for iy in range(yOffset):
                    self[x, iy] = False
        if yOffset < 0:
            yOffset = -yOffset
            # Shifting the bitmap up:
            for x in range(self._width):
                for iy in range(self._height - yOffset):
                    self[x, iy] = self[x, iy + yOffset]
            # Blank out the bottom side of the bitmap:
            for x in range(self._width):
                for iy in range(yOffset):
                    self[x, self._height - 1 - iy] = False


    def copy(self, left=0, top=0, width=None, height=None):
        """TODO"""

        # Parameter validaton:
        if not isinstance(left, int):
            raise TBMPException('left argument must be an int')
        if not isinstance(top, int):
            raise TBMPException('top argument must be an int')

        # If the width or height are None, let them default to the size of this bitmap:
        if width is None:
            width = self._width
        if height is None:
            height = self._height

        # More parameter validation.
        if not isinstance(width, int) or not width > 0:
            raise TBMPException('width argument must be None or a nonzero positive int')
        if not isinstance(height, int) or not height > 0:
            raise TBMPException('height argument must be None or a nonzero positive int')

        # If silence mode isn't enabled to suppress errors, then
        # left/top/width/height values that go beyond the borders of the
        # bitmap should raise an exception.
        if not self._silence:
            if left >= self._width:
                raise TBMPException('left argument is beyond the right edge of the bitmap; it must be less than the bitmap\'s width (or enable silence mode)')
            if left < 0:
                raise TBMPException('left argument is beyond the left edge of the bitmap; it must be greater than 0 (or enable silence mode)')
            if top >= self._height:
                raise TBMPException('top argument is beyond the bottom edge of the bitmap; it must be less than the bitmap\'s height (or enable silence mode)')
            if top < 0:
                raise TBMPException('left argument is beyond the left edge of the bitmap; it must be greater than 0 (or enable silence mode)')
            if left + width > self._width:
                raise TBMPException('The area to copy goes beyond the right edge of the bitmap; you must decrease the left or width argument (or enable silence mode)')
            if top + height > self._height:
                raise TBMPException('The area to copy goes beyond the bottom edge of the bitmap; you must decrease the right or height argument (or enable silence mode)')

        newCopy = TBMP(width, height)

        for srcx in range(max(left, 0), min(left + width, self._width)):
            for srcy in range(max(top, 0), min(top + height, self._height)):
                newCopy[srcx - left, srcy - top] = self[srcx, srcy]
        return newCopy


    def paste(self, termBitmapObj, left=0, top=0):

        # Parameter validaton:
        if not isinstance(left, int):
            raise TBMPException('left argument must be an int')
        if not isinstance(top, int):
            raise TBMPException('top argument must be an int')

        # If silence mode isn't enabled to suppress errors, then
        # left/top/width/height values that go beyond the borders of the
        # bitmap should raise an exception.
        if not termBitmapObj._silence:
            if left >= self._width:
                raise TBMPException('left argument is beyond the right edge of the bitmap; it must be less than the bitmap\'s width (or enable silence mode)')
            if left < 0:
                raise TBMPException('left argument is beyond the left edge of the bitmap; it must be greater than 0 (or enable silence mode)')
            if top >= self._height:
                raise TBMPException('top argument is beyond the bottom edge of the bitmap; it must be less than the bitmap\'s height (or enable silence mode)')
            if top < 0:
                raise TBMPException('left argument is beyond the left edge of the bitmap; it must be greater than 0 (or enable silence mode)')
            if left + self._width > termBitmapObj._width:
                raise TBMPException('The area to copy goes beyond the right edge of the bitmap; you must decrease the left or width argument (or enable silence mode)')
            if top + self._height > termBitmapObj._height:
                raise TBMPException('The area to copy goes beyond the bottom edge of the bitmap; you must decrease the right or height argument (or enable silence mode)')

        for x in range(self._width):
            if x + left < 0 or x + left > termBitmapObj._width:
                continue  # The x position is out of bounds, so skip it.
            for y in range(self._height):
                if y + top < 0 or y + top > termBitmapObj._height:
                    continue  # The y position is out of bounds, so skip it.
                termBitmapObj[x + left, y + top] = self[x, y]


    @property
    def width(self):
        return self._width


    @property
    def height(self):
        return self._height


    @property
    def size(self):
        return (self._width, self._height)


    @property
    def silence(self):
        return self._silence


    @silence.setter
    def silence(self, value):
        self._silence = bool(value)


    def __getitem__(self, key):
        x, y = key
        arrayIndex = (y * self._width + x)
        byteIndex = arrayIndex // 8
        bitIndex = arrayIndex % 8

        return (self._bitmap[byteIndex] >> bitIndex) % 2


    def __setitem__(self, key, value): # TODO - note, value must be bool. Any other int besides 0 or 1 will cause bugs.
        x, y = key
        if x < 0 or y < 0 or x >= self._width or y >= self._height:
            if self._silence:
                return  # Do nothing, just return.
            else:
                raise TBMPException('x, y coordinates ' + str(x) + ', ' + str(y) + ' are out of bounds for this ' + str(self._width) + 'x' + str(self._height) + ' terminal bitmap.')

        arrayIndex = (y * self._width + x)
        byteIndex = arrayIndex // 8
        bitIndex = arrayIndex % 8

        bitValue = (self._bitmap[byteIndex] >> bitIndex) % 2  # TODO - can I & 1 this instead of % 2?

        if value and not bitValue:
            # Set the False bit to True:
            self._bitmap[byteIndex] += (2 ** bitIndex)
        elif not value and bitValue:
            # Clear the True bit to False:
            self._bitmap[byteIndex] -= (2 ** bitIndex)


    def __delitem__(self, key):
        x, y = key
        arrayIndex = (y * self._width + x)
        byteIndex = arrayIndex // 8
        bitIndex = arrayIndex % 8

        bitValue = (self._bitmap[byteIndex] >> bitIndex) % 2

        if bitValue:
            # Clear the True bit to False:
            self._bitmap[byteIndex] -= (2 ** bitIndex)


    def __str__(self):
        result = []
        for y in range(0, self._height, 2):
            for x in range(self._width):
                if self[x, y]:
                    topHalf = True
                else:
                    topHalf = False

                if y + 1 == self._height or not self[x, y + 1]:
                    bottomHalf = False
                else:
                    bottomHalf = True

                if topHalf and bottomHalf:
                    result.append(FULL_BLOCK)
                elif topHalf and not bottomHalf:
                    result.append(TOP_BLOCK)
                elif not topHalf and bottomHalf:
                    result.append(BOTTOM_BLOCK)
                else:
                    result.append(' ')
            result.append('\n')
        result.pop()  # Remove the \n from the last row.
        return ''.join(result)


    @property
    def framed(self):
        result = []

        # Add the top part of the frame:
        result.append(DOWN_RIGHT_CHAR)
        result.append(LEFT_RIGHT_CHAR * self._width)
        result.append(DOWN_LEFT_CHAR)
        result.append('\n')

        # Add the bitmap: (This is copy/pasted from __str__())
        for y in range(0, self._height, 2):
            result.append(UP_DOWN_CHAR)
            for x in range(self._width):
                if self[x, y]:
                    topHalf = True
                else:
                    topHalf = False

                if y + 1 == self._height or not self[x, y + 1]:
                    bottomHalf = False
                else:
                    bottomHalf = True

                if topHalf and bottomHalf:
                    result.append(FULL_BLOCK)
                elif topHalf and not bottomHalf:
                    result.append(TOP_BLOCK)
                elif not topHalf and bottomHalf:
                    result.append(BOTTOM_BLOCK)
                else:
                    result.append(' ')
            result.append(UP_DOWN_CHAR)
            result.append('\n')

        # Add the top part of the frame:
        result.append(UP_RIGHT_CHAR)
        result.append(LEFT_RIGHT_CHAR * self._width)
        result.append(UP_LEFT_CHAR)
        return ''.join(result)


    def __iter__(self):
        return TBMP_iterator(self)


class TBMP_iterator:
    def __init__(self, parentTBMP):
        self._parentTBMP = parentTBMP
        self._x = 0
        self._y = 0

    def __next__(self):
        if self._y == self._parentTBMP._height:
            raise StopIteration
        bitToReturn = self._parentTBMP[self._x, self._y]
        self._x += 1

        if self._x == self._parentTBMP._width:
            self._x = 0
            self._y += 1

        return bitToReturn




b = TBMP(data="""          ▄▄█▀▀▄▄▄
       ▄▀▀   █▄▀▀ █
   ▄▄▀▀    ▄▀▀█    █
  ▀█▀▀▄▄▄▀▀    █    ▀▄
   ▀▄   ▀▄      █    ▀▄
    ▀▄   ▀▄    ▄▄▀▀▀▀▄█▄
      █   ▀▄▄▄▀    ▄▄▀▀
       █ ▄▄▀▄   ▄▄▀
        ▀▀▀▀█▄▀▀""")

class InfTBMP:
    # a limitless tbmp that lets you also have negative coordinates.
    pass