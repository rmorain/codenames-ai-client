class Assoc:
    def __init__(self):
        pass

    def getAssocs(self, pos, neg, topn) -> list[tuple[str, float]]:
        """
        Find words associated with positive words but not negative words.

        Args:
            pos: List of words to associate with
            neg: List of words to avoid
            topn: Number of associations to return

        Returns:
            List of (word, score) tuples
        """
        raise NotImplementedError

    def preprocess(self, w):
        """
        Preprocess words before looking up associations.

        Args:
            w: Input word

        Returns:
            Processed word
        """
        raise NotImplementedError

    def clearCache(self):
        """Gives subclasses option of clearing cache after each hint generation cycle.

        Provides balance between cached and non-cached operations.
        """
        return
