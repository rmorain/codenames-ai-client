from sys import argv
from typing import Dict, List

import requests
import socketio
from socketio.exceptions import TimeoutError

from agents.word2vec import W2VAssoc, W2VSpymaster
from base.constants import Team
import time

# Game Constants
BOARD_SIZE = 25
VALID_TEAMS = [team.name.lower() for team in Team]

# Server Configuration
SERVER_URL = "https://mind.cs.byu.edu"
HANDLE = "/codenames"
SOCKET_PATH = "/codenames/socket.io"
GET_STATE_URL = f"{SERVER_URL}{HANDLE}/get_game_state?code="
MAKE_CLUE_URL = f"{SERVER_URL}{HANDLE}/make_clue"


def is_empty_clue(clue: Dict) -> bool:
    return clue["word"] == "" and clue["number"] < 0


def create_board(state: Dict) -> Dict[str, List[str]]:
    board = {"U": [], "R": [], "N": [], "A": []}
    for i in range(BOARD_SIZE):
        if not state["guessed"][i]:
            board[state["colors"][i]].append(state["words"][i])
    return board


def make_clue(ai, board: Dict[str, List[str]], code: str, team: Team) -> Dict:
    clue, intended_words = ai.makeClue(board, team)
    print(f"Clue: {clue}")
    print("Intended words:", *intended_words, sep="\n\t")

    response = requests.post(
        MAKE_CLUE_URL,
        json={
            "orig": "py",
            "code": code,
            "team": team.name.lower(),
            "word": clue[0],
            "number": clue[1],
        },
    )
    return response.json()


def play_game(sio: socketio.SimpleClient, code: str, team: str, ai) -> None:
    state = requests.get(GET_STATE_URL + code).json()
    if "error" in state:
        print(f"Error: {state['error']}")
        raise ValueError(f"Game error: {state['error']}")

    time_started_waiting = time.time()
    while True:
        if Team[state["curr_turn"].upper()] == team and is_empty_clue(
            state["curr_clue"]
        ):
            state = make_clue(ai, create_board(state), code, team)
            time_started_waiting = time.time()

        try:
            elapsed_time = round(time.time() - time_started_waiting, 2)
            print(f'Waiting for my turn to submit clue {elapsed_time} seconds')
            event = sio.receive(timeout=5)
            event_name, data = event[0], event[1]

            if event_name == "update":
                state = data
            elif event_name == "game_end":
                print(f"{data['winner']} won!")
                break
        except TimeoutError:
            pass


# ** Instantiate your AI here! ********
def getAI():
    """Entry point for the game engine to get an AI agent."""
    return W2VSpymaster(W2VAssoc())


def main():
    if len(argv) < 3 or argv[2].lower() not in VALID_TEAMS:
        print("Usage: <game code> <'red' | 'blue'>")
        return 1

    code, team = argv[1], Team[argv[2].upper()]
    ai = getAI()

    with socketio.SimpleClient() as sio:
        sio.connect(
            SERVER_URL, socketio_path=SOCKET_PATH, transports=["websocket", "polling"]
        )
        if sio.connected:
            print(f"SID: {sio.sid}")
            sio.emit("join_room", code)
            print(f"Joined room: {code}")
            print("Starting game loop. Use Ctrl+C to exit early")
            play_game(sio, code, team, ai)


if __name__ == "__main__":
    exit(main())
