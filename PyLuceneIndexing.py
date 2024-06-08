import json
import os
import lucene
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, StringField, TextField,NumericDocValuesField, LongPoint
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from java.nio.file import Paths
from pathlib import Path

# Initialize lucene and the JVM
lucene.initVM()

def create_index(data_dir, index_dir):
    data_dir = Path(data_dir)
    index_dir = Path(index_dir)

    # Set up the index directory
    if not index_dir.exists():
        index_dir.mkdir(parents=True, exist_ok=True)
    
    store = SimpleFSDirectory(Paths.get(str(index_dir)))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    writer = IndexWriter(store, config)
    
    # Iterate over JSONL files in the data directory
    for filename in data_dir.glob("*.jsonl"):
        try:
            with filename.open('r', encoding='utf-8') as file:
                print(f"Indexing file: {filename}") 
                for line in file:
                    data = json.loads(line)
                    index_data(writer, data)
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
    
    writer.close()

def index_data(writer, data):
    doc = Document()
    for key, value in data.items():
        if isinstance(value, str):
            doc.add(TextField(key, value, Field.Store.YES))
        elif key == 'votes':
            doc.add(NumericDocValuesField("votes", int(value)))
        elif key == 'timestamp':
            doc.add(LongPoint("timestamp", value))
            doc.add(NumericDocValuesField("timestamp", value))
        else:
            doc.add(TextField(key, json.dumps(value), Field.Store.YES))
    writer.addDocument(doc)
    print(f"Added document: {data}")

#path to data directory and 
data_dir = '/home/cs172/CS172-Project/MultiThreading_PartA/CrawledData'
index_dir = '/home/cs172/CS172-Project/PyLucene_PartB/Indexed_Data'

#create the index
create_index(data_dir, index_dir)
print(f"Indexing completed. The index is stored in '{index_dir}'")

