"""Conway's Game of Life, by Al Sweigart al@inventwithpython.com
The classic cellular automata simulation. Press Ctrl-C to stop.
More info at: https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life
This code is available at https://nostarch.com/big-book-small-python-programming
Tags: short, artistic, simulation"""

import tbmp, copy, random, sys, time, os

# Set up the constants:
WIDTH, HEIGHT = tbmp.size()

# (!) Try changing ALIVE to '#' or another character:
ALIVE = True  # The character representing a living cell.
# (!) Try changing DEAD to '.' or another character:
DEAD = False   # The character representing a dead cell.

# (!) Try changing ALIVE to '|' and DEAD to '-'.

# The cells and nextCells are dictionaries for the state of the game.
# Their keys are (x, y) tuples and their values are one of the ALIVE
# or DEAD values.
nextCells = tbmp.TBMP(WIDTH, HEIGHT)
# Put random dead and alive cells into nextCells:
for x in range(WIDTH):  # Loop over every possible column.
    for y in range(HEIGHT):  # Loop over every possible row.
        # 50/50 chance for starting cells being alive or dead.
        if random.randint(0, 1) == 0:
            nextCells[(x, y)] = ALIVE  # Add a living cell.
        else:
            nextCells[(x, y)] = DEAD  # Add a dead cell.

while True:  # Main program loop.
    # Each iteration of this loop is a step of the simulation.

    # Clear the screen:
    if sys.platform == 'win32':
        os.system('cls')  # Windows uses the cls command.
    else:
        os.system('clear')  # macOS and Linux use the clear command.

    cells = tbmp.TBMP(bitmap=nextCells)

    # Print cells on the screen:
    print(cells)
    print('Press Ctrl-C to quit.')

    # Calculate the next step's cells based on current step's cells:
    for x in range(WIDTH):
        for y in range(HEIGHT):
            # Get the neighboring coordinates of (x, y), even if they
            # wrap around the edge:
            left  = (x - 1) % WIDTH
            right = (x + 1) % WIDTH
            above = (y - 1) % HEIGHT
            below = (y + 1) % HEIGHT

            # Count the number of living neighbors:
            numNeighbors = 0
            if cells[(left, above)] == ALIVE:
                numNeighbors += 1  # Top-left neighbor is alive.
            if cells[(x, above)] == ALIVE:
                numNeighbors += 1  # Top neighbor is alive.
            if cells[(right, above)] == ALIVE:
                numNeighbors += 1  # Top-right neighbor is alive.
            if cells[(left, y)] == ALIVE:
                numNeighbors += 1  # Left neighbor is alive.
            if cells[(right, y)] == ALIVE:
                numNeighbors += 1  # Right neighbor is alive.
            if cells[(left, below)] == ALIVE:
                numNeighbors += 1  # Bottom-left neighbor is alive.
            if cells[(x, below)] == ALIVE:
                numNeighbors += 1  # Bottom neighbor is alive.
            if cells[(right, below)] == ALIVE:
                numNeighbors += 1  # Bottom-right neighbor is alive.

            # Set cell based on Conway's Game of Life rules:
            if cells[(x, y)] == ALIVE and (numNeighbors == 2
                or numNeighbors == 3):
                    # Living cells with 2 or 3 neighbors stay alive:
                    nextCells[(x, y)] = ALIVE
            elif cells[(x, y)] == DEAD and numNeighbors == 3:
                # Dead cells with 3 neighbors become alive:
                nextCells[(x, y)] = ALIVE
            else:
                # Everything else dies or stays dead:
                nextCells[(x, y)] = DEAD

    try:
        time.sleep(0.2)  # Add a 0.2 second pause to reduce flickering.
    except KeyboardInterrupt:
        print("Conway's Game of Life")
        print('By Al Sweigart al@inventwithpython.com')
        sys.exit()  # When Ctrl-C is pressed, end the program.
