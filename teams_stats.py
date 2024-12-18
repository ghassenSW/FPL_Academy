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

def filter_by_gw(stats_type,data_type,start_gw,end_gw,sort_by,sort_order):
  stats=list(teams_stats_db.find())
  if stats_type=='atk':
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
      df=pd.DataFrame(home_data)
      for team_data in home_data:
        goal_rank=df['goals'].rank(ascending=False, method='min')
        team_data['goal_rank'] =goal_rank[df['goals'] == team_data['goals']].iloc[0]
        xg_rank=df['xg'].rank(ascending=False, method='min')
        team_data['xg_rank'] =xg_rank[df['xg'] == team_data['xg']].iloc[0]
        delta_xg_rank=df['delta_xg'].rank(ascending=False, method='min')
        team_data['delta_xg_rank'] =delta_xg_rank[df['delta_xg'] == team_data['delta_xg']].iloc[0]
        shots_rank=df['shots'].rank(ascending=False, method='min')
        team_data['shots_rank'] =shots_rank[df['shots'] == team_data['shots']].iloc[0]
        sib_rank=df['sib'].rank(ascending=False, method='min')
        team_data['sib_rank'] =sib_rank[df['sib'] == team_data['sib']].iloc[0]
        sot_rank=df['sot'].rank(ascending=False, method='min')
        team_data['sot_rank'] =sot_rank[df['sot'] == team_data['sot']].iloc[0]
        bc_rank=df['bc'].rank(ascending=False, method='min')
        team_data['bc_rank'] =bc_rank[df['bc'] == team_data['bc']].iloc[0]
        fts_rank=df['failed_to_score'].rank(ascending=False, method='min')
        team_data['fts_rank'] =fts_rank[df['failed_to_score'] == team_data['failed_to_score']].iloc[0]
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
      df=pd.DataFrame(away_data)
      for team_data in away_data:
        goal_rank=df['goals'].rank(ascending=False, method='min')
        team_data['goal_rank'] =goal_rank[df['goals'] == team_data['goals']].iloc[0]
        xg_rank=df['xg'].rank(ascending=False, method='min')
        team_data['xg_rank'] =xg_rank[df['xg'] == team_data['xg']].iloc[0]
        delta_xg_rank=df['delta_xg'].rank(ascending=False, method='min')
        team_data['delta_xg_rank'] =delta_xg_rank[df['delta_xg'] == team_data['delta_xg']].iloc[0]
        shots_rank=df['shots'].rank(ascending=False, method='min')
        team_data['shots_rank'] =shots_rank[df['shots'] == team_data['shots']].iloc[0]
        sib_rank=df['sib'].rank(ascending=False, method='min')
        team_data['sib_rank'] =sib_rank[df['sib'] == team_data['sib']].iloc[0]
        sot_rank=df['sot'].rank(ascending=False, method='min')
        team_data['sot_rank'] =sot_rank[df['sot'] == team_data['sot']].iloc[0]
        bc_rank=df['bc'].rank(ascending=False, method='min')
        team_data['bc_rank'] =bc_rank[df['bc'] == team_data['bc']].iloc[0]
        fts_rank=df['failed_to_score'].rank(ascending=False, method='min')
        team_data['fts_rank'] =fts_rank[df['failed_to_score'] == team_data['failed_to_score']].iloc[0]
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

      df=pd.DataFrame(overall_data)
      for team_data in overall_data:
        goal_rank=df['goals'].rank(ascending=False, method='min')
        team_data['goal_rank'] =goal_rank[df['goals'] == team_data['goals']].iloc[0]
        xg_rank=df['xg'].rank(ascending=False, method='min')
        team_data['xg_rank'] =xg_rank[df['xg'] == team_data['xg']].iloc[0]
        delta_xg_rank=df['delta_xg'].rank(ascending=False, method='min')
        team_data['delta_xg_rank'] =delta_xg_rank[df['delta_xg'] == team_data['delta_xg']].iloc[0]
        shots_rank=df['shots'].rank(ascending=False, method='min')
        team_data['shots_rank'] =shots_rank[df['shots'] == team_data['shots']].iloc[0]
        sib_rank=df['sib'].rank(ascending=False, method='min')
        team_data['sib_rank'] =sib_rank[df['sib'] == team_data['sib']].iloc[0]
        sot_rank=df['sot'].rank(ascending=False, method='min')
        team_data['sot_rank'] =sot_rank[df['sot'] == team_data['sot']].iloc[0]
        bc_rank=df['bc'].rank(ascending=False, method='min')
        team_data['bc_rank'] =bc_rank[df['bc'] == team_data['bc']].iloc[0]
        fts_rank=df['failed_to_score'].rank(ascending=False, method='min')
        team_data['fts_rank'] =fts_rank[df['failed_to_score'] == team_data['failed_to_score']].iloc[0]
      overall_data=sorted(overall_data,key=lambda x: x[sort_by],reverse=(sort_order=="desc"))
      return overall_data
  
  elif stats_type=='def':
    if data_type=='home':
      home_data=[]
      for team in teams_names:
        team_data={}
        home=[i for i in stats if i['team H']==team]
        df=pd.DataFrame(home)
        df=df[df['GW']>=start_gw]
        df=df[df['GW']<=end_gw]
        df=df[['team H','Goals A','xG A','Shots A','SiB A','SoT A','BC A']]
        df.columns=['team','goalsc','xgc','shotsc','sibc','sotc','bcc']
        df.loc[:,'cs'] = df['goalsc'] == 0
        df.loc[:,'delta_xgc']=df['goalsc']-df['xgc']
        games_played=len(df)
        sums=df.sum(numeric_only=True, axis=0)
        team_data['team']=team
        team_data['games_played']=games_played
        [team_data.update({k:round(v,2)}) for k,v in sums.items()]
        home_data.append(team_data)
      df=pd.DataFrame(home_data)
      for team_data in home_data:
        cs_rank=df['cs'].rank(ascending=True, method='min')
        team_data['cs_rank'] =cs_rank[df['cs'] == team_data['cs']].iloc[0]
        goalc_rank=df['goalsc'].rank(ascending=True, method='min')
        team_data['goalc_rank'] =goalc_rank[df['goalsc'] == team_data['goalsc']].iloc[0]
        xgc_rank=df['xgc'].rank(ascending=True, method='min')
        team_data['xgc_rank'] =xgc_rank[df['xgc'] == team_data['xgc']].iloc[0]
        delta_xgc_rank=df['delta_xgc'].rank(ascending=True, method='min')
        team_data['delta_xgc_rank'] =delta_xgc_rank[df['delta_xgc'] == team_data['delta_xgc']].iloc[0]
        shotsc_rank=df['shotsc'].rank(ascending=True, method='min')
        team_data['shotsc_rank'] =shotsc_rank[df['shotsc'] == team_data['shotsc']].iloc[0]
        sibc_rank=df['sibc'].rank(ascending=True, method='min')
        team_data['sibc_rank'] =sibc_rank[df['sibc'] == team_data['sibc']].iloc[0]
        sotc_rank=df['sotc'].rank(ascending=True, method='min')
        team_data['sotc_rank'] =sotc_rank[df['sotc'] == team_data['sotc']].iloc[0]
        bcc_rank=df['bcc'].rank(ascending=True, method='min')
        team_data['bcc_rank'] =bcc_rank[df['bcc'] == team_data['bcc']].iloc[0]
      home_data=sorted(home_data,key=lambda x: x[sort_by],reverse=(sort_order=="asc"))
      return home_data

    elif data_type=='away':
      away_data=[]
      for team in teams_names:
        team_data={}
        away=[i for i in stats if i['team A']==team]
        df=pd.DataFrame(away)
        df=df[df['GW']>=start_gw]
        df=df[df['GW']<=end_gw]
        df=df[['team A','Goals H','xG H','Shots H','SiB H','SoT H','BC H']]
        df.columns=['team','goalsc','xgc','shotsc','sibc','sotc','bcc']
        df.loc[:,'cs'] = df['goalsc'] == 0
        df.loc[:,'delta_xgc']=df['goalsc']-df['xgc']
        games_played=len(df)
        sums=df.sum(numeric_only=True, axis=0)
        team_data['team']=team
        team_data['games_played']=games_played
        [team_data.update({k:round(v,2)}) for k,v in sums.items()]
        away_data.append(team_data)
      df=pd.DataFrame(away_data)
      for team_data in away_data:
        cs_rank=df['cs'].rank(ascending=True, method='min')
        team_data['cs_rank'] =cs_rank[df['cs'] == team_data['cs']].iloc[0]
        goalc_rank=df['goalsc'].rank(ascending=True, method='min')
        team_data['goalc_rank'] =goalc_rank[df['goalsc'] == team_data['goalsc']].iloc[0]
        xgc_rank=df['xgc'].rank(ascending=True, method='min')
        team_data['xgc_rank'] =xgc_rank[df['xgc'] == team_data['xgc']].iloc[0]
        delta_xgc_rank=df['delta_xgc'].rank(ascending=True, method='min')
        team_data['delta_xgc_rank'] =delta_xgc_rank[df['delta_xgc'] == team_data['delta_xgc']].iloc[0]
        shotsc_rank=df['shotsc'].rank(ascending=True, method='min')
        team_data['shotsc_rank'] =shotsc_rank[df['shotsc'] == team_data['shotsc']].iloc[0]
        sibc_rank=df['sibc'].rank(ascending=True, method='min')
        team_data['sibc_rank'] =sibc_rank[df['sibc'] == team_data['sibc']].iloc[0]
        sotc_rank=df['sotc'].rank(ascending=True, method='min')
        team_data['sotc_rank'] =sotc_rank[df['sotc'] == team_data['sotc']].iloc[0]
        bcc_rank=df['bcc'].rank(ascending=True, method='min')
        team_data['bcc_rank'] =bcc_rank[df['bcc'] == team_data['bcc']].iloc[0]
      away_data=sorted(away_data,key=lambda x: x[sort_by],reverse=(sort_order=="asc"))
      return away_data
    
    elif data_type=='overall':
      overall_data=[]
      for team in teams_names:
        team_data={}
        home=[i for i in stats if i['team H']==team]
        df_h=pd.DataFrame(home)
        df_h=df_h[df_h['GW']>=start_gw]
        df_h=df_h[df_h['GW']<=end_gw]
        df_h=df_h[['team H','Goals A','xG A','Shots A','SiB A','SoT A','BC A']]
        df_h.columns=['team','goalsc','xgc','shotsc','sibc','sotc','bcc']
        df_h.loc[:,'cs'] = df_h['goalsc']==0
        df_h.loc[:,'delta_xgc']=df_h['goalsc']-df_h['xgc']

        away=[i for i in stats if i['team A']==team]
        df_a=pd.DataFrame(away)
        df_a=df_a[df_a['GW']>=start_gw]
        df_a=df_a[df_a['GW']<=end_gw]
        df_a=df_a[['team A','Goals H','xG H','Shots H','SiB H','SoT H','BC H']]
        df_a.columns=['team','goalsc','xgc','shotsc','sibc','sotc','bcc']
        df_a.loc[:,'cs'] = df_a['goalsc'] == 0
        df_a.loc[:,'delta_xgc']=df_a['goalsc']-df_a['xgc']
        df=pd.concat([df_h,df_a])
        games_played=len(df)

        sums=df.sum(numeric_only=True, axis=0)
        team_data['team']=team
        team_data['games_played']=games_played
        [team_data.update({k:round(v,2)}) for k,v in sums.items()]
        overall_data.append(team_data)

      df=pd.DataFrame(overall_data)
      for team_data in overall_data:
        cs_rank=df['cs'].rank(ascending=True, method='min')
        team_data['cs_rank'] =cs_rank[df['cs'] == team_data['cs']].iloc[0]
        goalc_rank=df['goalsc'].rank(ascending=True, method='min')
        team_data['goalc_rank'] =goalc_rank[df['goalsc'] == team_data['goalsc']].iloc[0]
        xgc_rank=df['xgc'].rank(ascending=True, method='min')
        team_data['xgc_rank'] =xgc_rank[df['xgc'] == team_data['xgc']].iloc[0]
        delta_xgc_rank=df['delta_xgc'].rank(ascending=True, method='min')
        team_data['delta_xgc_rank'] =delta_xgc_rank[df['delta_xgc'] == team_data['delta_xgc']].iloc[0]
        shotsc_rank=df['shotsc'].rank(ascending=True, method='min')
        team_data['shotsc_rank'] =shotsc_rank[df['shotsc'] == team_data['shotsc']].iloc[0]
        sibc_rank=df['sibc'].rank(ascending=True, method='min')
        team_data['sibc_rank'] =sibc_rank[df['sibc'] == team_data['sibc']].iloc[0]
        sotc_rank=df['sotc'].rank(ascending=True, method='min')
        team_data['sotc_rank'] =sotc_rank[df['sotc'] == team_data['sotc']].iloc[0]
        bcc_rank=df['bcc'].rank(ascending=True, method='min')
        team_data['bcc_rank'] =bcc_rank[df['bcc'] == team_data['bcc']].iloc[0]
      overall_data=sorted(overall_data,key=lambda x: x[sort_by],reverse=(sort_order=="asc"))
      return overall_data