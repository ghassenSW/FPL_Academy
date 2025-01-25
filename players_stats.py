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

client = MongoClient(MONGODB_URI)
db = client['my_database']
collection = db['fpl_data']
players_stats_db=db['players_stats']

stats=list(players_stats_db.find())
df=pd.DataFrame(stats)
players_names=list(df['web_name'])

def prepare_players(position,start_gw,end_gw):
    stats=list(players_stats_db.find())
    df=pd.DataFrame(stats)
    df=df[(df['num_gw']>=start_gw) & (df['num_gw']<=end_gw)]
    if position!='all':
       df=df[df['position']==position]
    df=df[['web_name','position','team','minutes_played','xG','xA','assists','goals','bonus','OG','shots','bc','chances_created','bc_created','sot','hit_wood_work','total_cross','total_points']]
    df=df.groupby(["web_name","team","position"], as_index=False).sum()
    df['xG']= df["xG"].round(2)
    df['xA']=df["xA"].round(2)
    df=df.sort_values(by="total_points",ascending=False)
    df = df.to_dict(orient="index")
    df=[v for k,v in df.items()]
    return df
