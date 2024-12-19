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
    events=url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/','events')
    num_gw=len(events[events['finished']==True])+1
    return num_gw

def df_to_text(df,day):
  num_gw=get_num_gw()
  text=f'💰 FPL Daily Price Changes ({day})\n'
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

def get_price_change_text(price_changed):
    del price_changed['_id']
    day=price_changed['day']
    del price_changed['day']
    df=pd.DataFrame(price_changed)
    text=df_to_text(df,day)
    return text

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
collection = db['fpl_data']
price_change_db=db['price_change']

if __name__ == '__main__':
  teams=url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/','teams')
  short_name=dict(zip(teams['id'],teams['short_name']))
  short_name=pd.DataFrame(short_name,index=[0])
  fpl_data=collection.find_one()
  old_stats=pd.DataFrame(fpl_data['elements'])
  old=prepare(old_stats)
  current_date=datetime.now()

  events=url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/','events')
  events['deadline_time'] = pd.to_datetime(events['deadline_time'])
  current_date = pd.Timestamp.now(tz="UTC").normalize()
  previous_date = current_date - pd.Timedelta(days=1)

  gw_begins=len(events[(events['deadline_time']<current_date) & (events['deadline_time']>previous_date)])!=0
  if gw_begins:
    price_change_db.delete_many({})


  new_stats=url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/','elements')
  new=prepare(new_stats) 
  unique_to_new = pd.concat([old, new]).drop_duplicates(keep=False)
  result_players = unique_to_new[~unique_to_new.isin(old)].dropna()
  if len(result_players)>0:
    day=f'{str(current_date.day)}/{str(current_date.month)}/{str(current_date.year)}'
    update = result_players.to_dict(orient="list")
    update['day']=day
    price_change_db.insert_one(update)

