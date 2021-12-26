"""Langton's Ant, by Al Sweigart al@inventwithpython.com
A cellular automata animation. Press Ctrl-C to stop.
More info: https://en.wikipedia.org/wiki/Langton%27s_ant
This code is available at https://nostarch.com/big-book-small-python-programming
Tags: large, artistic, simulation"""

import copy, random, sys, time, tbmp, os


# Set up the constants:
WIDTH, HEIGHT = tbmp.size()
#HEIGHT -= 20

NUMBER_OF_ANTS = 40  # (!) Try changing this to 1 or 50.
PAUSE_AMOUNT = 0.2  # (!) Try changing this to 1.0 or 0.0.

BLACK_TILE = 'black'
WHITE_TILE = 'white'

NORTH = 'north'
SOUTH = 'south'
EAST = 'east'
WEST = 'west'


def main():
    # Create a new board data structure:
    board = tbmp.TBMP(width=WIDTH, height=HEIGHT)

    # Create ant data structures:
    ants = []
    for i in range(NUMBER_OF_ANTS):
        ant = {
            'x': random.randint(0, WIDTH - 1),
            'y': random.randint(0, HEIGHT - 1),
            'direction': random.choice([NORTH, SOUTH, EAST, WEST]),
        }
        ants.append(ant)

    simulationStep = 0
    while True:  # Main program loop.
        if simulationStep % 10 == 0:  # Display the board every 10 steps.
            # Clear the screen:
            if sys.platform == 'win32':
                os.system('cls')  # Windows uses the cls command.
            else:
                os.system('clear')  # macOS and Linux use the clear command.

            print(board)
            time.sleep(PAUSE_AMOUNT)
        simulationStep += 1

        # nextBoard is what the board will look like on the next step in
        # the simulation. Start with a copy of the current step's board:
        nextBoard = tbmp.TBMP(data=board)

        # Run a single simulation step for each ant:
        for ant in ants:
            if board[ant['x'], ant['y']] == True:
                nextBoard[ant['x'], ant['y']] = False
                # Turn clockwise:
                if ant['direction'] == NORTH:
                    ant['direction'] = EAST
                elif ant['direction'] == EAST:
                    ant['direction'] = SOUTH
                elif ant['direction'] == SOUTH:
                    ant['direction'] = WEST
                elif ant['direction'] == WEST:
                    ant['direction'] = NORTH
            else:
                nextBoard[ant['x'], ant['y']] = True
                # Turn counter clockwise:
                if ant['direction'] == NORTH:
                    ant['direction'] = WEST
                elif ant['direction'] == WEST:
                    ant['direction'] = SOUTH
                elif ant['direction'] == SOUTH:
                    ant['direction'] = EAST
                elif ant['direction'] == EAST:
                    ant['direction'] = NORTH

            # Move the ant forward in whatever direction it's facing:
            if ant['direction'] == NORTH:
                ant['y'] -= 1
            if ant['direction'] == SOUTH:
                ant['y'] += 1
            if ant['direction'] == WEST:
                ant['x'] -= 1
            if ant['direction'] == EAST:
                ant['x'] += 1

            # If the ant goes past the edge of the screen,
            # it should wrap around to other side.
            ant['x'] = ant['x'] % WIDTH
            ant['y'] = ant['y'] % HEIGHT

        board = nextBoard




# If this program was run (instead of imported), run the game:
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Langton's Ant, by Al Sweigart al@inventwithpython.com")
        sys.exit()  # When Ctrl-C is pressed, end the program.
