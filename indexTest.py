import lucene
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.analysis.standard import StandardAnalyzer
from java.nio.file import Paths

# Initialize lucene and the JVM
lucene.initVM()
directory = SimpleFSDirectory(Paths.get('/home/cs172/CS172-Project/PyLucene_PartB/Indexed_Data'))
reader = DirectoryReader.open(directory)
searcher = IndexSearcher(reader)
analyzer = StandardAnalyzer()

# Read and print all indexed documents
for i in range(reader.maxDoc()):
    doc = reader.document(i)
    print(f"Document {i}:")
    print(f"ID: {doc.get('id')}")
    print(f"Title: {doc.get('title')}")
    print(f"User: {doc.get('user')}")
    print(f"Body: {doc.get('body')}")
    print(f"Comments: {doc.get('comments')}")
    print(f"URL: {doc.get('url')}")
    print(f"Linked Title: {doc.get('linked_title')}")
    print(f"Votes: {doc.get('votes')}")
    print(f"Timestamp: {doc.get('timestamp')}")
    print()

# Perform a test query
query_str = " "  # Replace with your test query
query = QueryParser("comments", analyzer).parse(query_str)
hits = searcher.search(query, 10).scoreDocs

print(f"Number of hits: {len(hits)}")

for hit in hits:
    doc = searcher.doc(hit.doc)
    print(f"Document: {doc.get('title')}, User: {doc.get('user')}, Body: {doc.get('body')}, URL: {doc.get('url')}, Votes: {doc.get('votes')}, Timestamp: {doc.get('timestamp')}")

