import requests
import pandas as pd
import os
from pymongo import MongoClient
from datetime import datetime

teams_names=['Arsenal', 'Aston Villa','Bournemouth','Brentford','Brighton & Hove Albion','Chelsea','Crystal Palace','Everton','Fulham','Ipswich Town','Leicester City','Liverpool','Manchester City','Manchester United','Newcastle United','Nottingham Forest','Southampton','Tottenham Hotspur','West Ham United','Wolverhampton']


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
teams_stats_db=db['teams_stats']

stats=list(teams_stats_db.find())
num_gw=stats[-1]['GW']

def filter_by_gw(data_type,start_gw,end_gw,sort_by,sort_order):
  stats=list(teams_stats_db.find())
  if data_type=='home':
    home_data=[]
    for team in teams_names:
      team_data={}
      home=[i for i in stats if i['team H']==team]
      df=pd.DataFrame(home)
      df=df[df['GW']>=start_gw]
      df=df[df['GW']<=end_gw]
      df=df[['team H','Goals H','xG H','Shots H','SiB H','SoT H','BC H']]
      df.columns=['team','goals','xg','shots','sib','sot','bc']
      df.loc[:,'failed_to_score'] = df['goals'] == 0
      df.loc[:,'delta_xg']=df['goals']-df['xg']
      games_played=len(df)
      sums=df.sum(numeric_only=True, axis=0)
      team_data['team']=team
      team_data['games_played']=games_played
      [team_data.update({k:round(v,2)}) for k,v in sums.items()]
      home_data.append(team_data)
    home_data=sorted(home_data,key=lambda x: x[sort_by],reverse=(sort_order=="desc"))
    return home_data

  elif data_type=='away':
    away_data=[]
    for team in teams_names:
      team_data={}
      away=[i for i in stats if i['team A']==team]
      df=pd.DataFrame(away)
      df=df[df['GW']>=start_gw]
      df=df[df['GW']<=end_gw]
      df=df[['team A','Goals A','xG A','Shots A','SiB A','SoT A','BC A']]
      df.columns=['team','goals','xg','shots','sib','sot','bc']
      df.loc[:,'failed_to_score'] = df['goals'] == 0
      df.loc[:,'delta_xg']=df['goals']-df['xg']
      games_played=len(df)
      sums=df.sum(numeric_only=True, axis=0)
      team_data['team']=team
      team_data['games_played']=games_played
      [team_data.update({k:round(v,2)}) for k,v in sums.items()]
      away_data.append(team_data)
    away_data=sorted(away_data,key=lambda x: x[sort_by],reverse=(sort_order=="desc"))
    return away_data
  
  elif data_type=='overall':
    overall_data=[]
    for team in teams_names:
      team_data={}
      home=[i for i in stats if i['team H']==team]
      df_h=pd.DataFrame(home)
      df_h=df_h[df_h['GW']>=start_gw]
      df_h=df_h[df_h['GW']<=end_gw]
      df_h=df_h[['team H','Goals H','xG H','Shots H','SiB H','SoT H','BC H']]
      df_h.columns=['team','goals','xg','shots','sib','sot','bc']
      df_h.loc[:,'failed_to_score'] = df_h['goals']==0
      df_h.loc[:,'delta_xg']=df_h['goals']-df_h['xg']

      away=[i for i in stats if i['team A']==team]
      df_a=pd.DataFrame(away)
      df_a=df_a[df_a['GW']>=start_gw]
      df_a=df_a[df_a['GW']<=end_gw]
      df_a=df_a[['team A','Goals A','xG A','Shots A','SiB A','SoT A','BC A']]
      df_a.columns=['team','goals','xg','shots','sib','sot','bc']
      df_a.loc[:,'failed_to_score'] = df_a['goals'] == 0
      df_a.loc[:,'delta_xg']=df_a['goals']-df_a['xg']
      df=pd.concat([df_h,df_a])
      games_played=len(df)

      sums=df.sum(numeric_only=True, axis=0)
      team_data['team']=team
      team_data['games_played']=games_played
      [team_data.update({k:round(v,2)}) for k,v in sums.items()]
      overall_data.append(team_data)
      
    overall_data=sorted(overall_data,key=lambda x: x[sort_by],reverse=(sort_order=="desc"))
    return overall_data
