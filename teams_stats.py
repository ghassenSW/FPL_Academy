import requests
import pandas as pd
import os
from pymongo import MongoClient
from datetime import datetime
import copy

teams_names=['Arsenal', 'Aston Villa','Bournemouth','Brentford','Brighton & Hove Albion','Chelsea','Crystal Palace','Everton','Fulham','Ipswich Town','Leicester City','Liverpool','Manchester City','Manchester United','Newcastle United','Nottingham Forest','Southampton','Tottenham Hotspur','West Ham United','Wolverhampton']

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
teams_stats_db=db['teams_stats']

home_data=[]
stats=list(teams_stats_db.find())
for team in teams_names:
    team_data={}
    home=[i for i in stats if i['team H']==team]
    df=pd.DataFrame(home)
    df=df[['team H','Goals H','xG H','Shots H','SiB H','SoT H','BC H']]
    df.columns=['team','goals','xg','shots','sib','sot','bc']
    sums=df.sum(numeric_only=True, axis=0)
    team_data['team']=team
    [team_data.update({k:round(v,2)}) for k,v in sums.items()]
    home_data.append(team_data)
    
away_data=[]
stats=list(teams_stats_db.find())
for team in teams_names:
    team_data={}
    home=[i for i in stats if i['team A']==team]
    df=pd.DataFrame(home)
    df=df[['team A','Goals A','xG A','Shots A','SiB A','SoT A','BC A']]
    df.columns=['team','goals','xg','shots','sib','sot','bc']
    sums=df.sum(numeric_only=True, axis=0)
    team_data['team']=team
    [team_data.update({k:round(v,2)}) for k,v in sums.items()]
    away_data.append(team_data)

overall_data=copy.deepcopy(home_data)
for team_data in overall_data:
   for away_team in away_data:
      if away_team['team']==team_data['team']:
        team_data['goals']+=away_team['goals']
        team_data['xg']+=away_team['xg']
        team_data['xg']=round(team_data['xg'],2)
        team_data['shots']+=away_team['shots']
        team_data['sib']+=away_team['sib']
        team_data['sot']+=away_team['sot']
        team_data['bc']+=away_team['bc']
        
