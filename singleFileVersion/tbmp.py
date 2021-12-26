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
tbmp is installed. But the image() function and importing bitmap image
files to __init__() are features that depend on Pillow."""
PILLOW_INSTALLED = True  # Set to True if Pillow is installed.
try:
    from PIL import Image, ImageDraw, ImageColor
except ImportError:
    PILLOW_INSTALLED = False

__version__ = '0.1.1'

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

# Global variable for the silence setting. If True, exceptions caused
# by out of bounds errors are suppressed.
SILENCE = False

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



def cube():
    """Returns a new TBMP object containing a drawing of a cube. This is
    useful for test bitmaps."""

    return TBMP(width=24, height=24, data=int('0x1fffc03000c050014190064208082408102fffe02808202808202808202408102408101404101404101404101407fff4081024100842600982800a03000c03fff80000000', 16))


def monaLisa():
    """Returns a new TBMP object containing a drawing of the Mona Lisa. This
    is useful for test bitmaps."""

    return TBMP(width=68, height=100, data=int('0x1000000000000000000000000800000004001001000000000000000000000000100000000000000000000000100000000000000000000000000000002000000200000000000000000000000112080000000000000001200000000000200008000000080001084e40100000010208c025000044000000422e81008000081103182500200000000a18a300000000000010d29400020400154aa2d40000000204010752200000000000003da904000000000000af5400000800000005ad820000040000002b6e021000004004005f09102001010000005008010000000000000810000000000000022800420000000422000420000000200000000100002100000000400202000008200000080004000000000800010000000000104081000000800200000080000000020480082048800000000080101000000000000000a820000808240008654080220000000203200201000000400009120802900822000000000000001000042400400000248820091020020000020102891200088215120808080a800005fe88002a080000017ff6001c4240000216eff800520680000af76ac0c01082004f17fff0028447420200dedb81040033882096ffc042a221440102f6fa0105100922001bfac00220444d8000edf8400881222c029775808204020a0801bbe00012208484000a680040088094000252842085024494401528012508022412201100120000000000084800912405401000000094400801484000040000900480400001602840080020a0006b00201002081000125800142212501020a64110000000088154380802109288000071501094004200001d6c00500252ae800066c0009204aa0a803f7654000aab60000aa9e00a2a055b5500376a13088854d0000526a2d4444af749000220151120536908048523eca842db46002ffe1b6ab3d5b71402bba5b6d186e99a402ddc2b6ed6d5f698006ea6db3bd756aee013fcb55d525d369400b74bb6d5bc6dad7001b9adaac93aab2c80462d3575ad555d2801015aa96d55544d4008d6aad2556ab66a800a9552b4695491540552a96aa55aa54ab5aad5695b44a59b254a8a5290476544895526528cb38891a6a12a91571446554915488ac00a55249454926403325245242844a95288911255552aaa28d556ad5', 16))


class TBMPException(Exception):
    """Exceptions raised by the tbmp module raise TBMPException or a
    subclass of TBMPException. If the tbmp module ever raises an exception
    that isn't TBMPException or a subclass, it is likely a bug in tbmp."""
    pass


class TBMP:
    def __init__(self, width=None, height=None, data=None, default=False):
        """Create a new terminal bitmap object. If the width and height
        aren't specified, the size is set to slightly smaller than the
        terminal window by default. The data parameter can prepopulate
        the bitmap's pixels. Terminal bitmap objects are static in size
        and cannot be resized.

        Args:
            width (int): The width of the bitmap in pixels. If None, it is
                the width of the terminal window, minus one (or 79). The
                minus one is to account for automatic newlines that Windows'
                Command Prompt adds. Defaults to None.
            height (int): The height of the bitmap in pixels. If None, it is
                twice the height of the terminal window minus 2 times 2 so
                that it doesn't take up the full window (or 44). Defaults to
                None.
            data (iterable, TBMP): This is data to prepopulate the bitmap's
                pixels. It can take several forms:

                    None - All of the pixels are set to the `default` bool
                    argument.

                    str - Either a multiline string of the block characters
                    that terminal bitmap objects render as. (Raises an
                    exception if the string contains non-block characters.)
                    Or it can be the string of a two-color image file to
                    load data from (requires Pillow to be installed).

                    TBMP - Copies the bitmap from another TBMP object.

                    int - Loads the pixels from an int representation of the
                    bitmap. (Pass a TBMP object to int() to get this.)

                    iterable - An iterable of (x, y) integer coordinates of
                    the pixels to set to the `default` argument.

            default (bool): The Boolean value all the pixels in the bitmap
                start as. Defaults to False.
        """

        # If data is an int, the width and height arguments are required:
        if data is not None and isinstance(data, int) and (width is None or height is None):
            raise TBMPException('If the data argument is an int, then width and height arguments are required.')

        # Create the bitmap by copying another TBMP object:
        if data is not None and isinstance(data, TBMP):
            if width is not None or height is not None:
                raise TBMPException('When passing a TBMP object for the data parameter, width and height arguments must be left out.')
            self._width = data._width
            self._height = data._height
            self._bitmap = data._bitmap[:]
            return


        if data is not None and isinstance(data, str):
            # Create the bitmap from a black and white image file:
            if os.path.exists(data):
                if not PILLOW_INSTALLED:
                    raise TBMPException('Pillow is required to be installed to create TBMP objects from an image file.')
                img = Image.open(data)
                self._width, self._height = img.size

                # Create the backend data structure:
                if default:
                    # Start with the bitmap completely full.
                    self.fill()
                else:
                    # Start with the bitmap completely empty.
                    self.clear()

                # Read in the pixel data from the image:
                for x in range(self._width):
                    for y in range(self._height):
                        imgPixel = img.getpixel((x, y))

                        if imgPixel[0:3] == (0, 0, 0):
                            self[x, y] = default
                        elif imgPixel[0:3] == (255, 255, 255):
                            self[x, y] = not default
                        else:
                            raise TBMPException('Only black and white images can be used to load bitmap data from. The ' + data + ' image file contains a pixel with color ' + str(imgPixel))
                return

            # Create the bitmap from a multiline string of box characters in the data parameter:
            if len(data) == 0:
                raise TBMPException('If data is a string, it cannot be a blank string.')
            lines = data.split('\n')
            self._width = max([len(line) for line in lines])
            self._height = len(lines) * 2  # Each line of text represents two rows in the bitmap.
            return

        # The `data` argument was not specified. Create a blank bitmap
        # based on the width and height parameters:
        if width is None or height is None:
            # Set the width and/or height based on the terminal size:
            self._width, self._height = shutil.get_terminal_size()
            self._width -= 1  # Account for Windows' Command Prompt adding a newline when something is printed in the rightmost column.
            self._height -= 2  # By reducing the height by 2, the prompt in the interactive shell on the bottom line won't hide the top line when this bitmap is printed.
            self._height *= 2  # Note that terminals display two terminal bitmap "pixels" per text character.
        if width is not None:
            self._width = width
        if height is not None:
            self._height = height

        if not isinstance(self._width, int) or self._width < 1:
            raise TBMPException('width arg must be an int greater than 0')
        if not isinstance(self._height, int) or self._height < 1:
            raise TBMPException('height arg must be an int greater than 0')

        if default:
            # Start with the bitmap completely full.
            self.fill()
        else:
            # Start with the bitmap completely empty.
            self.clear()

        if data is not None:
            # Create the bitmap
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
            elif isinstance(data, int):
                data = bin(data)[2:].rjust(self._width * self._height, '0')  # Trim the '0b' at the start.
                i = 0
                for y in range(self._height):
                    for x in range(self._width):
                        self[x, y] = data[len(data) - 1 - i] == '1'
                        i += 1

                        # TODO add silence check there?
                        if i > len(data):
                            return
            else:
                # Prepopulate the bitmap for the pixels specified in the `data` iterable:
                for x, y in data:
                    self[x, y] = not default


    def applyFunc(self, funcStr):
        """Apply a lambda function to every pixel in the terminal bitmap.
        This lambda function takes two int arguments (x and y) and returns
        an int or bool. If the return value is True, the pixel at those
        x and y coordinates is set, and if False the pixel is cleared.

        Some examples are:
            tbmpObj.applyFunc('(x ^ y) % 5')
            tbmpObj.applyFunc('(x & y) & (x ^ y) % 19')
            tbmpObj.applyFunc('(x % y) % 4')
            tbmpObj.applyFunc('(x & y)')

        If the function raises an Exception (for zero divides, for example)
        the pixel at that xy coordinate is simply set to False.

        Args:
            funcStr (str, callable): Either a string of the lambda function
                code (which may or may not begin with "lambda x, y:") or
                a callable function that takes two int arguments for the
                x and y coordinates.
        """
        if isinstance(funcStr, str):
            # A vague attempt at mitigating malicious input since func is passed to eval(). Don't rely on this for security.
            if ';' in funcStr or 'import' in funcStr or 'open' in funcStr:
                raise Exception('funcStr argument as a string must only have a lambda function')

            if not funcStr.strip().replace(' ', '').lower().startswith('lambdax,y:'):
                funcStr = 'lambda x, y:' + funcStr
            func = eval(funcStr)

        for x in range(self._width):
            for y in range(self._height):
                try:
                    self[x, y] = func(x, y)
                except:
                    self[x, y] = False



    def image(self, fg='white', bg='black', fgAlpha=255, bgAlpha=255):
        """Returns a Pillow Image object of the bitmap. Requires the Pillow
        module to be installed.

        Args:
            fg (str) - The color of the set pixels in the foreground.
                Can either be a web safe color name or an RGB or RGBA tuple
                of ints from 0 to 255. For example (255, 0, 0) is the tuple
                for red. The alpha channel in this tuple is ignored; use
                fgAlpha instead. Defaults to 'white'.
            bg (str) - The color of the clear pixels in the background.
                Can either be a web safe color name or an RGB or RGBA tuple
                of ints from 0 to 255. For example (255, 0, 0) is the tuple
                for red. The alpha channel in this tuple is ignored; use
                bgAlpha instead. Defaults to 'black'.
            fgAlpha (int) - The opacity of the foreground color, which ranges
                from 0 (completely transparent) to 255 (completely opaque.)
                Defaults to 255.
            bgAlpha (int) - The opacity of the background color, which ranges
                from 0 (completely transparent) to 255 (completely opaque.)
                Defaults to 255.
        """
        if not PILLOW_INSTALLED:
            raise Exception('The image() function requires the Pillow module to be installed.')

        fg = ImageColor.getcolor(fg, 'RGB')
        if fgAlpha < 255:
            # Set the transparency of the foreground color:
            fg = (fg[0], fg[1], fg[2], fgAlpha)

        bg = ImageColor.getcolor(bg, 'RGB')
        if bgAlpha < 255:
            # Set the transparency of the foreground color:
            bg = (bg[0], bg[1], bg[2], bgAlpha)

        # Set the color mode to include the alpha channel if there's any transparency:
        if fgAlpha < 255 or bgAlpha < 255:
            colorMode = 'RGBA'
        else:
            colorMode = 'RGB'

        # Create the blank image object:
        img = Image.new(colorMode, (self._width, self._height), bg)

        # Copy the pixels of the terminal bitmap to this image object:
        draw = ImageDraw.Draw(img)
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

        return img

    def _getNumBytesNeeded(self):
        """Return the number of bytes needed to store this bitmap, based on
        1 bit per pixel and the width and height of the bitmap."""
        numBytesNeeded = (self._width * self._height) // 8
        if (self._width * self._height) % 8 > 0:
            numBytesNeeded += 1
        return numBytesNeeded

    def clear(self):
        """Make the bitmap completely empty."""

        numBytesNeeded = self._getNumBytesNeeded()
        # It's faster to replace the array. in _bitmap than set all the values to 0:
        self._bitmap = array.array('B', b'\x00' * numBytesNeeded)


    def fill(self):
        """Make the bitmap completely full."""
        numBytesNeeded = self._getNumBytesNeeded()
        # It's faster to replace the array. in _bitmap than set all the values to 255:
        self._bitmap = array.array('B', b'\xFF' * numBytesNeeded)


    def randomize(self, weight=0.50):
        """Set the pixels in the terminal bitmap randomly. The weight
        determines how many pixels are True. A weight of 1.0 means they'll
        all be True, a weight of 0.0 means they'll all be False, and 0.5
        means that they are randomly half True and half False.

        Note that due to how the code is written, using a weight of 0.5
        is currently about 20x faster than a non-0.5 weight."""
        numBytesNeeded = self._getNumBytesNeeded()

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
        """Toggle all of the pixels in the bitmap: True becomes False and
        False becomes True."""
        for x in range(self._width):
            for y in range(self._height):
                self[x, y] = not self[x, y]


    def toggle(self, x, y):
        """Toggle the pixel at the x, y coordinates: True becomes False and
        False becomes True."""
        self[x, y] = not self[x, y]


    def hFlip(self):
        """Flip all the pixels in the terminal bitmap horizontally."""
        for x in range(self._width // 2):
            for y in range(self._height):
                self[x, y], self[self._width - x - 1, y] = self[self._width - x - 1, y], self[x, y]


    def vFlip(self):
        """Flip all the pixels in the terminal bitmap vertically."""
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
        """Shift all of the pixels by xOffset and yOffset. Pixels shifted
        off the edge of the bitmap are lost, and the void created on the
        opposite side of the shifting has cleared pixels.

        Args:
            xOffset (int) - The number of pixels to shift right. If negative,
            pixels are shifted to the left.
            yOffset (int) - The number of pixels to shift down. If negative,
            pixels are shifted up."""

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
            # Shifting the bitmap to the left:
            xOffset = -xOffset
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
            # Shifting the bitmap up:
            yOffset = -yOffset
            for x in range(self._width):
                for iy in range(self._height - yOffset):
                    self[x, iy] = self[x, iy + yOffset]
            # Blank out the bottom side of the bitmap:
            for x in range(self._width):
                for iy in range(yOffset):
                    self[x, self._height - 1 - iy] = False


    def copy(self, left=0, top=0, width=None, height=None):
        """Copy the bitmap or a subregion of the bitmap to a new TBMP
        object and return it.

        Args:
            left (int) - The left edge of the region to copy. Defaults to 0.
            top (int) - The top edge of the region to copy. Defaults to 0.
            width (None, int) - The width of the region to copy. If None,
                then the entire width of the bitmap is copied. Defaults to
                None.
            height (None, int) - The height of the region to copy. If None,
                then the entire height of the bitmap is copied. Defaults to
                None."""

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
        if not SILENCE:
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
        """Pastes the bitmap onto another TBMP object's bitmap.

        Args:
            termBitmapObj (TBMP) - The TBMP object to paste this bitmap onto.
            left (int) - The left edge on termBitmapObj to paste this bitmap
                at. Defaults to 0.
            top (int) - The top edge on termBitmapobj to paste this bitmap
                at. Defaults to 0."""

        # Parameter validaton:
        if not isinstance(left, int):
            raise TBMPException('left argument must be an int')
        if not isinstance(top, int):
            raise TBMPException('top argument must be an int')

        # If silence mode isn't enabled to suppress errors, then
        # left/top/width/height values that go beyond the borders of the
        # bitmap should raise an exception.
        if not SILENCE:
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
        """The width of this bitmap in pixels. This is a read-only property."""
        return self._width


    @property
    def height(self):
        """The height of this bitmap in pixels. This is a read-only property."""
        return self._height


    @property
    def size(self):
        """A tuple of the (width, height) of this bitmap. This is a read-only
        property."""
        return (self._width, self._height)


    def __getitem__(self, key):
        """Retrieve the bool of the pixel at x, y. The key is a tuple of the
        (x, y) coordinates."""
        x, y = key
        arrayIndex = (y * self._width + x)
        byteIndex = arrayIndex // 8
        bitIndex = arrayIndex % 8

        return (self._bitmap[byteIndex] >> bitIndex) % 2


    def __setitem__(self, key, value): # TODO - note, value must be bool. Any other int besides 0 or 1 will cause bugs.
        """Set the bool of the pixel at x, y. The key is a tuple of the
        (x, y) coordinates."""
        x, y = key
        if x < 0 or y < 0 or x >= self._width or y >= self._height:
            if SILENCE:
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


    def __str__(self):
        """Return a multiline string representation of the bitmap, using
        block characters for the pixels."""

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


    def __int__(self):
        """Return an int representation of the bitmap. The
        binary representation shows the values of the individual pixels."""
        bitmapAsInt = 0
        num = 1
        for bit in self:
            if bit:
                bitmapAsInt += num
            num += num  # Double the number.
        return bitmapAsInt

    def hex(self):
        """Return a string of the hexadecimal representation of the bitmap."""
        return hex(int(self))

    def bin(self):
        """Return a string of the binary number representation of the bitmap."""
        return bin(int(self))

    @property
    def framed(self):
        """Return a multiline string representation of the bitmap, using
        block characters for the pixels. This string includes an outline to
        make the dimensions of the bitmap easy to see."""

        # This code is mostly copied from __str__().

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


    def asInfTBMP(self):
        infTBMPObj = InfTBMP()
        for x in range(self._width):
            for y in range(self._height):
                if self[x, y]:
                    infTBMPObj[x, y] = True
        infTBMPObj._updateDimensions()
        return infTBMPObj


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


class InfTBMP:
    """A limitless terminal bitmap that adjusts its size as you set pixels
    on it. It's slower, uses more memory, and has fewer features than the
    TBMP class. If you need these features, create a TBMP object and then
    paste it to the InfTBMP object.

    A lot of the code is copied from the TBMP class."""

    def __init__(self):
        self._bitmap = set()  # A set of (x, y) tuples of the set pixels.

        # The boundaries of the set pixels on this InfTBMP object are stored here:
        self._left = 0
        self._top = 0
        self._right = 0
        self._bottom = 0

        self._width = self._right - self._left + 1
        self._height = self._top - self._bottom + 1

        # This is set to True when a new pixel is added/removed, and
        # set to False when _updateDimensions() is called.
        self._dimensionsOutOfDate = False


    def asTBMP(self):
        """Returns a TBMP object that is a copy of this InfTBMP bitmap.

        Unlike this InfTBMP object, the TBMP object has a static width
        and height."""
        self._updateDimensions()

        tbmpObj = TBMP(width=self._width, height=self._height)
        for x, y in self._bitmap:
            tbmpObj[x - self._left, y - self._top] = True
        return tbmpObj


    def _updateDimensions(self):
        if not self._dimensionsOutOfDate:
            return  # No need to update the size.

        if len(self._bitmap) == 0:
            self._left = 0
            self._right = 0
            self._top = 0
            self._bottom = 0
            self._width = 1
            self._height = 1
            return

        it = iter(self._bitmap)
        firstPixel = next(it)
        left = firstPixel[0]
        right = firstPixel[0]
        top = firstPixel[1]
        bottom = firstPixel[1]

        for x, y in it:
            # Loop over the rest of the pixels.
            if x < left:
                left = x
            if x > right:
                right = x
            if y < top:
                top = y
            if y > bottom:
                bottom = y
        self._left = left
        self._right = right
        self._width = right - left + 1

        self._top = top
        self._bottom = bottom
        self._height = bottom - top + 1

        self._dimensionsOutOfDate = False


    def image(self, fg='white', bg='black', fgAlpha=255, bgAlpha=255):
        """Returns a Pillow Image object of the bitmap. Requires the Pillow
        module to be installed.

        Args:
            fg (str) - The color of the set pixels in the foreground.
                Can either be a web safe color name or an RGB or RGBA tuple
                of ints from 0 to 255. For example (255, 0, 0) is the tuple
                for red. The alpha channel in this tuple is ignored; use
                fgAlpha instead. Defaults to 'white'.
            bg (str) - The color of the clear pixels in the background.
                Can either be a web safe color name or an RGB or RGBA tuple
                of ints from 0 to 255. For example (255, 0, 0) is the tuple
                for red. The alpha channel in this tuple is ignored; use
                bgAlpha instead. Defaults to 'black'.
            fgAlpha (int) - The opacity of the foreground color, which ranges
                from 0 (completely transparent) to 255 (completely opaque.)
                Defaults to 255.
            bgAlpha (int) - The opacity of the background color, which ranges
                from 0 (completely transparent) to 255 (completely opaque.)
                Defaults to 255.
        """
        return self.asTBMP().image()


    @property
    def width(self):
        """The width of this bitmap in pixels. This is a read-only property."""
        self._updateDimensions()
        return self._width


    @property
    def height(self):
        """The height of this bitmap in pixels. This is a read-only property."""
        self._updateDimensions()
        return self._height


    @property
    def size(self):
        """A tuple of the (width, height) of this bitmap. This is a read-only
        property."""
        self._updateDimensions()
        return (self._width, self._height)


    @property
    def left(self):
        """The leftmost edge of this bitmap. This is a read-only property."""
        self._updateDimensions()
        return self._left


    @property
    def right(self):
        """The rightmost edge of this bitmap. This is a read-only property."""
        self._updateDimensions()
        return self._right


    @property
    def top(self):
        """The topmost edge of this bitmap. This is a read-only property."""
        self._updateDimensions()
        return self._top


    @property
    def bottom(self):
        """The bottommost edge of this bitmap. This is a read-only property."""
        self._updateDimensions()
        return self._bottom


    @property
    def dimensions(self):
        """A tuple of the left, top, right, bottom edges of this bitmap.
        This is a read-only property."""
        self._updateDimensions()
        return (self._left, self._top, self._right, self._bottom)


    def __getitem__(self, key):
        """Retrieve the bool of the pixel at x, y. The key is a tuple of the
        (x, y) coordinates."""
        x, y = key
        return (x, y) in self._bitmap


    def __setitem__(self, key, value): # TODO - note, value must be bool. Any other int besides 0 or 1 will cause bugs.
        """Set the bool of the pixel at x, y. The key is a tuple of the
        (x, y) coordinates."""
        self._dimensionsOutOfDate = True
        x, y = key

        if value == True and (x, y) not in self._bitmap:
            self._bitmap.add((x, y))
            self._dimensionsOutOfDate = True
        elif value == False and (x, y) in self._bitmap:
            self._bitmap.remove((x, y))
            self._dimensionsOutOfDate = True


    def __str__(self):
        """Return a multiline string representation of the bitmap, using
        block characters for the pixels."""
        return str(self.asTBMP())


    def __int__(self):
        """Return an int representation of the bitmap. The
        binary representation shows the values of the individual pixels."""
        return int(self.asTBMP())


    def hex(self):
        """Return a string of the hexadecimal representation of the bitmap."""
        return hex(int(self))


    def bin(self):
        """Return a string of the binary number representation of the bitmap."""
        return bin(int(self))


    def shift(self, xOffset, yOffset):
        """Shift all of the pixels by xOffset and yOffset. Pixels shifted
        off the edge of the bitmap are lost, and the void created on the
        opposite side of the shifting has cleared pixels.

        Args:
            xOffset (int) - The number of pixels to shift right. If negative,
            pixels are shifted to the left.
            yOffset (int) - The number of pixels to shift down. If negative,
            pixels are shifted up."""
        shiftedBitmap = set()
        for x, y in self._bitmap:
            shiftedBitmap.add((x + xOffset, y + yOffset))
        self._bitmap = shiftedBitmap
        self._dimensionsOutOfDate = True
        self._updateDimensions()

        # TODO - this is still buggy when shifting negative
