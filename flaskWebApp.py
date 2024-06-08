from flask import Flask, request, render_template_string, send_from_directory
import lucene
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher, Sort, SortField
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.analysis.standard import StandardAnalyzer
from java.nio.file import Paths
import time

app = Flask(__name__, static_folder='')

# Initialize lucene and the JVM
lucene.initVM()
directory = SimpleFSDirectory(Paths.get('/home/cs172/CS172-Project/PyLucene_PartB/Indexed_Data'))
reader = DirectoryReader.open(directory)
searcher = IndexSearcher(reader)
analyzer = StandardAnalyzer()

# Sample minimum timestamp for normalization, replace with actual minimum timestamp in your data
min_timestamp = time.time() * 1000

def custom_score(doc, score, votes, timestamp):
    vote_weight = 1.0
    time_weight = 0.5
    relevance_weight = 1.0

    normalized_votes = votes / (votes + 1.0)
    current_time = float(time.time() * 1000)
    normalized_time = 1.0 - (current_time - timestamp) / (current_time - min_timestamp)

    combined_score = (relevance_weight * score) + (vote_weight * normalized_votes) + (time_weight * normalized_time)
    return combined_score

@app.route('/')
def home():
    with open('index.html') as f:
        return render_template_string(f.read())

@app.route('/search', methods=['POST'])
def search():
    lucene.getVMEnv().attachCurrentThread()
    query_str = request.form['query']
    sort_by = request.form['sort_by']
    print(f"Search query: {query_str}, Sort by: {sort_by}")  # Debug statement
    query = QueryParser("body", analyzer).parse(query_str)
    hits = searcher.search(query, 10).scoreDocs

    print(f"Number of hits: {len(hits)}")  # Debug statement

    results = []
    for hit in hits:
        doc = searcher.doc(hit.doc)
        score = hit.score
        votes = int(doc.get("votes")) if doc.get("votes") else 0
        timestamp = int(doc.get("timestamp")) if doc.get("timestamp") else 0
        combined_score = custom_score(doc, score, votes, timestamp)

        result = {
            "id": doc.get("id"),
            "title": doc.get("title"),
            "user": doc.get("user"),
            "body": doc.get("body"),
            "url": doc.get("url"),
            "linked_title": doc.get("linked_title"),
            "votes": votes,
            "timestamp": timestamp,
            "score": combined_score
        }
        results.append(result)
        print(f"Document: {result}")  # Debug statement

    if sort_by == 'relevance':
        results.sort(key=lambda x: x["score"], reverse=True)
    elif sort_by == 'votes':
        results.sort(key=lambda x: x["votes"], reverse=True)
    elif sort_by == 'time':
        results.sort(key=lambda x: x["timestamp"], reverse=True)
    elif sort_by == 'combined':
        results.sort(key=lambda x: x["score"], reverse=True)

    with open('results.html') as f:
        return render_template_string(f.read(), query=query_str, results=results)

@app.route('/webUI_styling.css')
def css():
    return send_from_directory('', 'webUI_styling.css')

if __name__ == '__main__':
    app.run(debug=True, port=8888, host='0.0.0.0')

