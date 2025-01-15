from .constants import Team
from base.assoc import Assoc


class BaseSpymaster:
    def __init__(self, assoc: Assoc):
        self.assoc = assoc

    def makeClue(self, board, team: Team) -> tuple[tuple[str, int], tuple[str]]:
        """Generate a clue for the current game state.

        This method should analyze the game board and generate a clue that helps
        the team identify their remaining words while avoiding opponent's words,
        neutral words, and the assassin.

        Args:
            board (dict): Game board state with keys 'U' (blue team words),
                         'R' (red team words), 'N' (neutral words), and
                         'A' (assassin word). Each key maps to a list of words.
            team (Team): Enum indicating which team (BLUE/RED) the spymaster is playing
                        for.

        Returns:
            tuple: A pair containing:
                - tuple: (clue_word: str, num_words: int) where clue_word is the
                        generated clue and num_words is how many words it relates to
                - tuple: The combination of board words this clue is targeting
                        (implementation specific, can be None)

        Raises:
            NotImplementedError: This is an abstract method that must be implemented
                               by concrete spymaster classes.
        """
        raise NotImplementedError
