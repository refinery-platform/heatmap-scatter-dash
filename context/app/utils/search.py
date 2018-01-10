from whoosh.fields import Schema, TEXT
from whoosh.filedb.filestore import RamStorage
from whoosh.qparser import QueryParser

class Index():
    # For the moment, we just want to be able to index strings,
    # and return those that match on any substring.

    # TODO:
    # - Simple O(N^2) implementation
    # - Test
    # - Refactor existing code to use this class
    # - Replace internals with Whoosh

    def __init__(self):
        storage = RamStorage()
        schema = Schema(gene_id=TEXT(stored=True))
        self._index = storage.create_index(schema)

    def add(self, gene_id):
        writer = self._index.writer()
        writer.add_document(gene_id=gene_id)
        writer.commit()

    def search(self, substring):
        with self._index.searcher() as searcher:
            parser = QueryParser('gene_id', self._index.schema)
            query = parser.parse(substring or '')
            results = searcher.search(query)
            return [result['gene_id'] for result in results]
