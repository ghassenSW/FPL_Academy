from pymongo import MongoClient
import os
import requests
import pandas as pd

def url_to_df(url,key=None):
  response = requests.get(url)
  if response.status_code == 200:
      data = response.json()
      return data
  else:
      print(f"Error: {response.status_code}")

# from dotenv import load_dotenv
# load_dotenv()
# MONGODB_URI=os.getenv('MONGODB_URI')

MONGODB_URI = os.environ.get('MONGODB_URI')

client = MongoClient(MONGODB_URI)
db = client['my_database']
collection = db['fpl_data']

def update_mongo_data():
    new_data =url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/')
    collection.delete_many({})
    collection.insert_one(new_data)
    print("MongoDB data overwritten successfully with new fpl data.")

if __name__ == "__main__":
    update_mongo_data()
