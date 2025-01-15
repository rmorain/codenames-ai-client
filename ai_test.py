from random import randint, sample, seed, shuffle
from sys import argv

from agents.word2vec import W2VAssoc, W2VSpymaster
from base.constants import Team

"""
This script is used to test the AI agents in a local environment. It generates a random
board and then asks the AI to generate a clue. The board and clue are then printed to
the console. The answer is revealed when the user presses Enter.

To run this script, simply execute it from the command line. You can optionally provide
a seed value as an argument to reproduce a specific game board. For example:

    python ai_test.py 1234
"""

row_col = 5
BOARD_SIZE = row_col**2


# provide colors to capitalize blue words
def printBoard(selected, colors=None):
    max_width = len(sorted(selected, key=lambda s: len(s), reverse=True)[0]) + 1
    line = []
    for i in range(len(selected)):
        curr = selected[i]
        if colors and colors[i] == "U":
            curr = curr.upper()
        line.append(f"{curr:{max_width}}")
        if len(line) % row_col == 0:
            print(" ".join(line))
            line = []


def loadWords(filename:str ="word_list.txt") -> list:
    """Load words from a text file, one word per line."""
    try:
        with open(filename, "r") as file:
            # Strip whitespace and filter out empty lines
            return [word.strip().lower() for word in file if word.strip()]
    except FileNotFoundError:
        print(f"Error: Could not find {filename}")
        return []
    except IOError:
        print(f"Error: Could not read {filename}")
        return []


# ** Instantiate your AI here! ********
def getAI():
    """Entry point for the game engine to get an AI agent."""
    return W2VSpymaster(W2VAssoc())


# ===============================================


def runTrial():
    # blue first
    words = loadWords()
    colors = ["U"] * 9 + ["R"] * 8 + ["N"] * 7 + ["A"] # Blue team has more words to guess

    shuffle(colors)

    selected = sample(words, BOARD_SIZE)
    covered = [False] * BOARD_SIZE # This variable seems unused.

    board = {"U": [], "R": [], "N": [], "A": []}
    for i in range(BOARD_SIZE):
        if covered[i]:
            continue
        color = colors[i]
        word = selected[i]
        board[color].append(word)

    m = getAI()
    clue, combo = m.makeClue(board, Team.BLUE)
    return selected, colors, board, clue, combo


if __name__ == "__main__":
    s = randint(1, 10000)
    if len(argv) > 1:
        try:
            s = int(argv[1])
        except ValueError:
            pass
    seed(s)
    print("Seed:", s)

    selected, colors, board, clue, combo = runTrial()
    print()
    printBoard(selected, colors)

    print(clue)
    print()

    input("Press Enter to reveal answer(s)...\n")

    printBoard(selected, colors)

    print(", ".join(combo))
