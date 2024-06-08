import json
import os
import lucene
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, StringField, TextField, NumericDocValuesField, LongPoint,StoredField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from java.nio.file import Paths
from pathlib import Path

#initialize lucene and the JVM
lucene.initVM()

def create_index(data_dir, index_dir):
    data_dir = Path(data_dir)
    index_dir = Path(index_dir)

    #set up the index directory
    if not index_dir.exists():
        index_dir.mkdir(parents=True, exist_ok=True)
    
    store = SimpleFSDirectory(Paths.get(str(index_dir)))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    writer = IndexWriter(store, config)

    min_timestamp = float('inf')
    
    #iterate over JSONL files in the data directory
    for filename in data_dir.glob("*.jsonl"):
        try:
            with filename.open('r', encoding='utf-8') as file:
                print(f"Indexing file: {filename}") 
                for line in file:
                    data = json.loads(line)
                    index_data(writer, data)
                    if 'timestamp' in data and data['timestamp'] < min_timestamp:
                        min_timestamp = data['timestamp']
        except Exception as e:
            print(f"Error processing file {filename}: {e}")

    #save the minimum timestamp to a file
    with open(index_dir / 'min_timestamp.txt', 'w') as f:
        f.write(str(min_timestamp))
    
    writer.close()

def index_data(writer, data):
    doc = Document()
    # Index each field appropriately
    doc.add(StringField("id", str(data.get("id", "")), Field.Store.YES))
    doc.add(TextField("title", data.get("title", ""), Field.Store.YES))
    doc.add(TextField("user", data.get("user", ""), Field.Store.YES))
    doc.add(TextField("body", data.get("body", ""), Field.Store.YES))
    if "comments" in data and isinstance(data["comments"], list):
        comments_text = " ".join(data["comments"])
        doc.add(TextField("comments", comments_text, Field.Store.YES))
    doc.add(TextField("url", data.get("url", ""), Field.Store.YES))
    doc.add(TextField("linked_title", data.get("linked_title", ""), Field.Store.YES))
    votes = int(data.get("votes", 0))
    timestamp = int(data.get("timestamp", 0))
    doc.add(NumericDocValuesField("votes", votes))  # Enables sorting and scoring on votes
    doc.add(StoredField("votes", votes))            # Stores the actual value for retrieval
    doc.add(LongPoint("timestamp", timestamp))      # Enables efficient range queries on timestamp
    doc.add(NumericDocValuesField("timestamp", timestamp))  # Enables sorting and scoring on timestamp
    doc.add(StoredField("timestamp", timestamp))    # Stores the actual value for retrieval
    writer.addDocument(doc)
    #print(f"Added document: {data}")


#path to data directory and index directory
data_dir = '/home/cs172/CS172-Project/MultiThreading_PartA/CrawledData'
index_dir = '/home/cs172/CS172-Project/PyLucene_PartB/Indexed_Data'

#create the index
create_index(data_dir, index_dir)

print(f"Indexing completed. The index is stored in '{index_dir}'")

