import requests
import pandas as pd
import os
from pymongo import MongoClient
from datetime import datetime

try:
  from dotenv import load_dotenv
  load_dotenv()
  MONGODB_URI=os.getenv('MONGODB_URI')
except Exception as e:
  try:
    MONGODB_URI=os.environ.get('MONGODB_URI')
  except Exception as e2:
    print(e2)

teams_tag = {'Arsenal': 'ARS','Chelsea': 'CHE','Brentford': 'BRE','Bournemouth': 'BOU','Crystal Palace': 'CRY','Fulham': 'FUL','West Ham': 'WHU','Everton': 'EVE','Wolves': 'WOL','Southampton': 'SOU','Brighton': 'BHA','Man City': 'MCI','Liverpool': 'LIV','Aston Villa': 'AVL','Man Utd': 'MUN','Leicester': 'LEI',"Nott'm Forest": 'NFO','Newcastle': 'NEW','Spurs': 'TOT','Ipswich': 'IPS'}
teams_names_fpl=sorted(list(teams_tag.keys()))

client = MongoClient(MONGODB_URI)
db = client['my_database']
collection = db['fpl_data']
players_stats_db=db['players_stats']

stats=list(players_stats_db.find())
df=pd.DataFrame(stats)
players_names=list(df['web_name'])
id_player=dict(zip(df['id'],df['web_name']))
def prepare_players(position,start_gw,end_gw,team):
    stats=list(players_stats_db.find())
    df=pd.DataFrame(stats)
    df=df[(df['num_gw']>=start_gw) & (df['num_gw']<=end_gw)]
    if position!='all':
       df=df[df['position']==position]
    df=df[['id','web_name','position','team','minutes_played','xG','xA','assists','goals','bonus','OG','shots','bc','chances_created','bc_created','sot','hit_wood_work','total_cross','total_points']]
    if team!='ALL':
      df=df[df['team']==team]
    df['team_tag']=df['team'].map(teams_tag)
    df=df.groupby(["web_name","team","position","id",'team_tag'], as_index=False).sum()
    df['xG']= df["xG"].round(2)
    df['xA']=df["xA"].round(2)
    df=df.sort_values(by="total_points",ascending=False)
    df = df.to_dict(orient="index")
    df=[v for k,v in df.items()]
    return df

def get_player_matches(player_id,start_gw,end_gw):
  stats=list(players_stats_db.find())
  df=pd.DataFrame(stats)
  df=df[['id','num_gw','opp_team','total_points','minutes_played','goals','xG','assists','xA','goals_conceded','CS','shots','sot','bc','chances_created','bc_created','hit_wood_work','total_cross','penalties_missed','saves','penalties_saved','bonus','bps','OG','yellow_cards','red_cards','value','opta_code']]
  df=df[(df['num_gw']>=start_gw) & (df['num_gw']<=end_gw)]
  df=df[df['id']==player_id]
  df['xG']= df["xG"].round(2)
  df['xA']=df["xA"].round(2)
  df=df.sort_values(by="num_gw",ascending=False)
  df = df.to_dict(orient="index")
  df=[v for k,v in df.items()]
  return df