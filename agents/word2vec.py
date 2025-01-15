from collections import defaultdict
from typing import Optional

from gensim.models import KeyedVectors

from base.assoc import Assoc
from base.constants import Team
from base.spymaster import BaseSpymaster
from utils.helpers import isValid, powerset


class ModelSingleton:
    """Word2Vec model singleton."""

    _instance: Optional[KeyedVectors] = None

    @classmethod
    def get_model(cls) -> KeyedVectors:
        if not cls._instance:
            print("loading w2v model")
            cls._instance = KeyedVectors.load_word2vec_format(
                "GoogleNews-vectors-negative300.bin", binary=True, limit=500000
            )
        return cls._instance


class W2VAssoc(Assoc):
    def __init__(self, debug=False):
        super().__init__()
        self.model = ModelSingleton.get_model()
        self.debug = debug

    def getAssocs(self, pos, neg, topn):
        if self.debug:
            print("W2V", pos, neg)
        # See https://radimrehurek.com/gensim_3.8.3/models/keyedvectors.html#gensim.models.keyedvectors.WordEmbeddingsKeyedVectors.most_similar
        return self.model.most_similar(
            positive=pos, negative=neg, topn=topn, restrict_vocab=50000
        )

    def preprocess(self, w):
        try:
            # First try to find word in model's vocabulary
            self.model.key_to_index[w]
        except KeyError:
            # If word not found, convert to CamelCase format
            w = "_".join([part[0].upper() + part[1:] for part in w.split("_")])
        return w


class Combo:
    """Stores and manages clues and their similarity scores."""
    def __init__(self):
        self.scores = []
        self.max_clue = None
        self.max_sim = -9999

    def addOption(self, clue, sim):
        self.scores.append(sim)
        if self.max_sim < sim:
            self.max_sim = sim
            self.max_clue = clue

    def getAvgSim(self):
        return sum(self.scores) / len(self.scores)


class W2VSpymaster(BaseSpymaster):
    def __init__(self, assoc, debug=False):
        super().__init__(assoc)
        self.debug = debug

    def makeClue(self, board, team: Team):
        # Step 1: Extract all words from the game board into a set
        # This will be used later to ensure our clue isn't one of the board words
        board_words = set(
            [item for sublist in list(board.values()) for item in sublist]
        )

        # Step 2: Identify our team's words and the opponent's words based on team color
        # 'U' represents blue team, 'R' represents red team
        my_words = board["U" if team == Team.BLUE else "R"]
        opponent_words = board["R" if team == Team.BLUE else "U"]

        # Step 3: Create negative word list (words we want to avoid)
        # Combines opponent's words with neutral ('N') and assassin ('A') words
        # These are words our clue should NOT be similar to
        neg = board["N"] + board["A"] + opponent_words
        # Create positive word list (words we want to target)
        pos = my_words

        # Step 4: Preprocess all words to match the word2vec model's format
        neg = [self.assoc.preprocess(w) for w in neg]
        pos = [self.assoc.preprocess(w) for w in pos]

        # Clear any cached results from previous calculations
        self.assoc.clearCache()

        # Step 5: Initialize dictionary to store word combinations and their potential
        # clues
        combos = defaultdict(Combo)

        # Step 6: Generate word combinations
        # If only one word, skip powerset calculation
        # Otherwise, generate all possible combinations of our team's words
        if len(pos) == 1:
            pow_set = [tuple(pos)]
        else:
            pow_set = powerset(pos)

        # Step 7: For each word combination, find potential clues
        for combo in pow_set:
            # Get word associations using word2vec model
            # Returns top 10 similar words for this combination
            curr = self.assoc.getAssocs(list(combo), neg, 10)

            # Step 8: Filter and store valid clues
            any_added = False
            for clue, similarity in curr:
                clue = clue.lower()
                # Only accept clues that aren't already on the board
                if isValid(clue, board_words):
                    combos[combo].addOption(clue, similarity)
                    any_added = True
            if not any_added:
                print("NONE ADDED:", combo, [clue for clue, sim in curr])

        if self.debug:
            print("mH combos:", combos)

        # Step 9: Find the best word combination based on similarity scores
        max_avg_sim = -9999
        max_combo = None

        # Handle case where no valid clues were found
        if not combos.keys():
            print("NO CLUE!", board, team, pos, neg)
            return ("None", 1)

        # Step 10: Select the combination with highest average similarity score
        for combo in combos.keys():
            avg_sim = combos[combo].getAvgSim()
            if self.debug:
                print("mH combo+avg\t:", combo, avg_sim)
            if max_avg_sim < avg_sim:
                max_avg_sim = avg_sim
                max_combo = combo

        if self.debug:
            print("mH max_combo:", max_combo)
        # Return tuple of (best_clue, number_of_words_to_guess), and the winning
        # combination
        return (combos[max_combo].max_clue, len(max_combo)), max_combo
