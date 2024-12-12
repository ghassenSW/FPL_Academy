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

def get_num_gw():
    present_fixtures=url_to_df('https://fantasy.premierleague.com/api/fixtures/?future=1')
    num_gw=present_fixtures['event'].min()
    fixtures=url_to_df('https://fantasy.premierleague.com/api/fixtures')
    fixtures=fixtures[fixtures['event']==num_gw-1]
    if fixtures.iloc[-1]['finished']==False:
        num_gw-=1
    return num_gw

def prepare(df):
  df['full_name']=df['first_name']+' '+df['second_name']
  df['team']=df['team'].map(my_map.iloc[0])
  df.loc[:,'chance_of_playing_next_round']=df.loc[:,'chance_of_playing_next_round'].fillna(101)
  df.loc[:,'news']=df.loc[:,'news'].fillna('')
  return df

def condition(row):
  return row['id'] in ids

def df_to_text(players):
    gw=get_num_gw()
    tweet_text='🚨 Injury Updates\n\n'
    match_tag=f'#GW{gw} #FPL #FPL_InjuryUpdates'
    for index,row in players.iterrows():
        player_name=row['full_name']
        team_name=teams_short_names[row['team']]
        tweet_text+=f'👟 {player_name} (#{team_name})\n'
        if(row['chance_of_playing_next_round']==100):
            tweet_text+=f'✅ Availability is now 100%\n'
        elif row['chance_of_playing_next_round']==0:
           stat=row['news']
           tweet_text+=f'⛔️ {stat}\n'
        else:
            stat=row['news']
            tweet_text+=f'🤕 {stat}\n'
        tweet_text+='\n'
    tweet_text=tweet_text.strip('\n')
    tweet_text+='\n\n'+match_tag
    return tweet_text

def get_injury_updates_text(injury):
    df=pd.DataFrame([injury])
    text=df_to_text(df)
    return text

def update_mongo_data():
    new_data =url_to_json('https://fantasy.premierleague.com/api/bootstrap-static/')
    collection.delete_many({})
    collection.insert_one(new_data)
    print("MongoDB data overwritten successfully with new fpl data.")

# from dotenv import load_dotenv
# load_dotenv()
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
injury_updates_db=db['injuries']

teams=url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/','teams')
teams_short_names=dict(zip(teams['name'],teams['short_name']))
my_map=dict(zip(teams['id'],teams['name']))
my_map=pd.DataFrame(my_map,index=[0])
num_gameweek=get_num_gw()


if __name__ == '__main__':
  fpl_data=collection.find_one()
  old_stats=pd.DataFrame(fpl_data['elements'])
  new_stats=url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/','elements')
  old=prepare(old_stats)
  new=prepare(new_stats)
  ids=list(old['id'])
  new=new[new.apply(condition,axis=1)]
  old=old.reset_index(drop=True)
  new=new.reset_index(drop=True)
  conditions=new[['chance_of_playing_next_round','news']]!=old[['chance_of_playing_next_round','news']]
  first_condition=new[conditions['chance_of_playing_next_round']]
  second_condition=new[conditions['news']]
  players = pd.concat([first_condition, second_condition], axis=0, ignore_index=True)
  players = players.drop_duplicates()
  players=players[['chance_of_playing_next_round','team','full_name','news']]
  players=players.astype({'chance_of_playing_next_round':'int'})

  injury_updates_db.delete_many({})
  for index,row in players.iterrows():
    update = row.to_dict()
    injury_updates_db.insert_one(update)

  update_mongo_data()
