import requests
import pandas as pd
import os
from pymongo import MongoClient
from datetime import datetime


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
  players = players.assign(now_cost=players['now_cost'].astype(float) / 10)
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

def get_num_gw():
    present_fixtures=url_to_df('https://fantasy.premierleague.com/api/fixtures/?future=1')
    num_gw=present_fixtures['event'].min()
    fixtures=url_to_df('https://fantasy.premierleague.com/api/fixtures')
    fixtures=fixtures[fixtures['event']==num_gw-1]
    if fixtures.iloc[-1]['finished']==False:
        num_gw-=1
    return num_gw

def df_to_text(df):
  num_gw=get_num_gw()
  current_time=datetime.now().date()
  text=f'💰 FPL Daily Price Changes ({current_time})\n'
  risers=df[df['cost_change_event']==1]
  fallers=df[df['cost_change_event']==-1]
  if(len(risers)!=0):
    text+=(f'\n📈 Risers:\n')
    for index,row in risers.iterrows():
      text+=(f'⬆️ {row["web_name"]} #{row["team"]} £{row["now_cost"]}m\n')
  if(len(fallers)!=0):
    text+=(f'\n📉 Fallers:\n')
    for index,row in fallers.iterrows():
      text+=(f'⬇️ {row["web_name"]} #{row["team"]} £{row["now_cost"]}m\n')
  text+=f'\n#FPL #GW{num_gw} #FPL_PriceChanges'
  return text

def get_price_change_text(price_change_db):
    price_changed=price_change_db.find_one()
    del price_changed['_id']
    df=pd.DataFrame(price_changed)
    text=df_to_text(df)
    return text

from dotenv import load_dotenv
load_dotenv()
try:
  MONGODB_URI=os.getenv('MONGODB_URI')
except Exception as e:
  try:
    MONGODB_URI=os.environ.get('MONGODB_URI')
  except Exception as e2:
    print(e2)

client = MongoClient(MONGODB_URI)
db = client['my_database']
collection = db['fpl_data']
price_change_db=db['price_change']

teams=url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/','teams')
short_name=dict(zip(teams['id'],teams['short_name']))
short_name=pd.DataFrame(short_name,index=[0])

if __name__ == '__main__':
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

