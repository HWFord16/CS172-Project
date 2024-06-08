from flask import Flask, request, render_template_string, send_from_directory
import lucene
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher, BooleanQuery, BooleanClause
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

# Read minimum timestamp for normalization
with open('/home/cs172/CS172-Project/PyLucene_PartB/Indexed_Data/min_timestamp.txt', 'r') as f:
    min_timestamp = float(f.read().strip())

def custom_score(doc, bm25_score, votes, timestamp, vote_weight, time_weight, relevance_weight):
    normalized_votes = votes / (votes + 1.0)
    current_time = float(time.time() * 1000)  # Current time in milliseconds

    # Ensure timestamp is not zero to avoid division errors and unrealistic score calculations
    if timestamp == 0:
        timestamp = min_timestamp

    # Normalization formula
    normalized_time = 1.0 - (current_time - timestamp) / (current_time - min_timestamp)
    combined_score = (relevance_weight * bm25_score) + (vote_weight * normalized_votes) + (time_weight * normalized_time)
    
    return combined_score

@app.route('/')
def home():
    with open('index.html') as f:
        return render_template_string(f.read())

@app.route('/search', methods=['POST'])
def search():
    lucene.getVMEnv().attachCurrentThread()
    query_str = request.form['query']
    ranking_option = request.form['ranking_option']
    sort_by = request.form.get('sort_by')
    vote_weight = float(request.form.get('vote_weight', 0.5))
    time_weight = float(request.form.get('time_weight', 0.25))
    relevance_weight = float(request.form.get('relevance_weight', 1.0))
    
    print(f"Query: {query_str}")  # Debug statement
    print(f"Ranking Option: {ranking_option}, Sort by: {sort_by}")  # Debug statement

    fields = ["title", "body", "user", "linked_title", "comments"]
    query = BooleanQuery.Builder()

    for field in fields:
        parser = QueryParser(field, analyzer)
        parsed_query = parser.parse(query_str)
        query.add(parsed_query, BooleanClause.Occur.SHOULD)

    hits = searcher.search(query.build(), 10).scoreDocs

    print(f"Number of hits: {len(hits)}")  # Debug statement

    results = []
    seen_docs = set()
    for hit in hits:
        doc = searcher.doc(hit.doc)
        doc_id = doc.get("id")
        if doc_id not in seen_docs:
            seen_docs.add(doc_id)
            bm25_score = hit.score
            votes = int(doc.get("votes")) if doc.get("votes") else 0
            timestamp = int(doc.get("timestamp")) if doc.get("timestamp") else 0
            if ranking_option == 'custom':
                combined_score = custom_score(doc, bm25_score, votes, timestamp, vote_weight, time_weight, relevance_weight)
            else:
                combined_score = bm25_score

            result = {
                "id": doc.get("id"),
                "title": doc.get("title"),
                "user": doc.get("user"),
                "body": doc.get("body"),
                "url": doc.get("url"),
                "linked_title": doc.get("linked_title"),
                "votes": votes,
                "timestamp": timestamp,
                "score": combined_score,
                "bm25_score": bm25_score
            }
            results.append(result)
            print(f"Document: {result}")  # Debug statement

    if ranking_option == 'custom':
        if sort_by == 'relevance':
            results.sort(key=lambda x: x["bm25_score"], reverse=True)
        elif sort_by == 'votes':
            results.sort(key=lambda x: x["votes"], reverse=True)
        elif sort_by == 'time':
            results.sort(key=lambda x: x["timestamp"], reverse=True)
        elif sort_by == 'combined':
            results.sort(key=lambda x: x["score"], reverse=True)
    else:
        results.sort(key=lambda x: x["bm25_score"], reverse=True)

    with open('results.html') as f:
        return render_template_string(f.read(), query=query_str, results=results)

@app.route('/webUI_styling.css')
def css():
    return send_from_directory('', 'webUI_styling.css')

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')

