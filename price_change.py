import requests
import numpy as np
import pandas as pd
import time
import tweepy
from datetime import datetime,timedelta
import json
import os
from pymongo import MongoClient

def url_to_json(url,key=None):
  response = requests.get(url)
  if response.status_code == 200:
      data = response.json()
      return data
  else:
      print(f"Error: {response.status_code}")

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

def prepare(players):
  players=players[['team','web_name','cost_change_event','now_cost']]
  players.loc[:,'now_cost']=players.loc[:,'now_cost']/10
  players=players[players['cost_change_event']!=0]
  players = players.rename(columns={'team': 'team_id'})
  players.loc[:,'team']=players['team_id'].map(short_name.iloc[0])
  players=players.sort_values(by=['cost_change_event','now_cost'],ascending=False)
  return players

def update_mongo_data():
    new_data =url_to_json('https://fantasy.premierleague.com/api/bootstrap-static/')
    collection.delete_many({})
    collection.insert_one(new_data)
    print("MongoDB data overwritten successfully with new fpl data.")

MONGODB_URI=os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client['my_database']
collection = db['fpl_data']
price_change_db=db['price_change']

teams=url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/','teams')
short_name=dict(zip(teams['id'],teams['short_name']))
short_name=pd.DataFrame(short_name,index=[0])

fpl_data=collection.find_one()
old_stats=pd.DataFrame(fpl_data['elements'])
old=prepare(old_stats)

new_stats=url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/','elements')
new=prepare(new_stats)
unique_to_new = pd.concat([old, new]).drop_duplicates(keep=False)
result_players = unique_to_new[~unique_to_new.isin(old)].dropna()

update = result_players.to_dict(orient="list")
price_change_db.delete_many({})
price_change_db.insert_one(update)

update_mongo_data()

