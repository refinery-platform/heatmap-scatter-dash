class Index():
    # For the moment, we just want to be able to index strings,
    # and return those that match on any substring.

    # TODO:
    # - Simple O(N^2) implementation
    # - Test
    # - Refactor existing code to use this class
    # - Replace internals with Whoosh

    def __init__(self):
        self._index = []

    def add(self, doc):
        self._index.append(doc)

    def search(self, query):
        if query:
            return [doc for doc in self._index if query in doc]
        else:
            return self._index
