from whoosh.fields import Schema, TEXT, NGRAMWORDS
from whoosh.filedb.filestore import RamStorage
from whoosh.qparser import QueryParser
from  whoosh.query import Every

class Index():
    # For the moment, we just want to be able to index strings,
    # and return those that match on any substring.

    def __init__(self):
        storage = RamStorage()
        schema = Schema(gene_id=TEXT(stored=True),
                        gene_tokens=NGRAMWORDS(stored=False))
        self._index = storage.create_index(schema)

    def add(self, gene_id):
        writer = self._index.writer()
        writer.add_document(gene_id=gene_id,
                            gene_tokens=gene_id)
        writer.commit()

    def search(self, substring):
        with self._index.searcher() as searcher:
            parser = QueryParser('gene_tokens', self._index.schema)
            query = parser.parse(substring) if substring else Every()
            results = searcher.search(query)
            return [result['gene_id'] for result in results]
