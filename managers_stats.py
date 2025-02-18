import pandas as pd
import requests
from teams_stats import num_gw
import os 
from pymongo import MongoClient

def url_to_df(url,key=None):
  response = requests.get(url)
  if response.status_code == 200:
      data = response.json()
      if key!=None:
        df=pd.DataFrame(data[key])
      else:
        df=pd.DataFrame(data)
      return df
  else:
      print(f"Error: {response.status_code}")

try:
  from dotenv import load_dotenv
  load_dotenv()
  MONGODB_URI=os.getenv('MONGODB_URI')
except Exception as e:
  try:
    MONGODB_URI=os.environ.get('MONGODB_URI')
  except Exception as e2:
    print(e2)

client = MongoClient(MONGODB_URI)
db = client['my_database']
managers_stats_db=db['managers_stats']
teams_table = list(managers_stats_db.find({}, {"_id": 0}))
teams_table = sorted(teams_table, key=lambda x: x["position"])
