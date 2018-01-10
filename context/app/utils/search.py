from whoosh.fields import NGRAMWORDS, TEXT, Schema
from whoosh.filedb.filestore import RamStorage
from whoosh.qparser import OrGroup, QueryParser
from whoosh.query import Every


class SimpleIndex():
    # "Indexing" is fast, but search is a bit slow.

    def __init__(self):
        self._index = []

    def add(self, *gene_ids):
        self._index.extend(gene_ids)

    def search(self, substring):
        return [gene_id for gene_id in self._index if substring in gene_id]


class WhooshIndex():
    # Search might be fast, but indexing is too slow to be useful.

    def __init__(self):
        storage = RamStorage()
        schema = Schema(gene_id=TEXT(stored=True),
                        gene_tokens=NGRAMWORDS(stored=False))
        self._index = storage.create_index(schema)

    def add(self, *gene_ids):
        writer = self._index.writer()
        for gene_id in gene_ids:
            writer.add_document(gene_id=gene_id,
                                gene_tokens=gene_id)
        writer.commit()

    def search(self, substring):
        with self._index.searcher() as searcher:
            parser = QueryParser('gene_tokens', self._index.schema,
                                 group=OrGroup)
            query = parser.parse(substring) if substring else Every()
            results = searcher.search(query)
            return [result['gene_id'] for result in results]
