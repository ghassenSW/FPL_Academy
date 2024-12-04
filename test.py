import os 
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()
MONGODB_URI=os.getenv('MONGODB_URI')

client = MongoClient(MONGODB_URI)
db = client['my_database']
collection = db['users']

documents = [
    {"name": "Alice", "age": 25, "email": "alice@example.com"},
    {"name": "Bob", "age": 35, "email": "bob@example.com"}
]
collection.insert_many(documents)
for doc in collection.find():
    print(doc)
