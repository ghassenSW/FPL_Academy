import requests
import pandas as pd
import os
from pymongo import MongoClient
from datetime import datetime

teams_names=['Arsenal', 'Aston Villa','Bournemouth','Brentford','Brighton & Hove Albion','Chelsea','Crystal Palace','Everton','Fulham','Ipswich Town','Leicester City','Liverpool','Manchester City','Manchester United','Newcastle United','Nottingham Forest','Southampton','Tottenham Hotspur','West Ham United','Wolverhampton']

team_emoji = {
    "Arsenal": "🔫 Arsenal","Aston Villa": "🦁 Aston Villa","Bournemouth": "🍒 Bournemouth","Brentford": "🐝 Brentford","Brighton & Hove Albion": "🕊 Brighton","Chelsea": "🔵 Chelsea","Crystal Palace": "🦅 Crystal Palace","Everton": "🍬 Everton","Fulham": "⚪️ Fulham","Ipswich Town": "🚜 Ipswich","Leicester City": "🦊 Leicester","Liverpool": "🔴 Liverpool","Manchester City": "🌑 Man City","Manchester United": "👹 Man Utd","Newcastle United": "⚫️ Newcastle","Nottingham Forest": "🌳 Nott'm Forest","Southampton": "😇 Southampton","Tottenham Hotspur": "🐓 Spurs","West Ham United": "⚒️ West Ham","Wolverhampton": "🐺 Wolves"
}

teams_short_names = {'Arsenal': 'ARS','Chelsea': 'CHE','Brentford': 'BRE','Bournemouth': 'BOU','Crystal Palace': 'CRY','Fulham': 'FUL','West Ham United': 'WHU','Everton': 'EVE','Wolverhampton': 'WOL','Southampton': 'SOU','Brighton & Hove Albion': 'BHA','Manchester City': 'MCI','Liverpool': 'LIV','Aston Villa': 'AVL','Manchester United': 'MUN','Leicester City': 'LEI','Nottingham Forest': 'NFO','Newcastle United': 'NEW','Tottenham Hotspur': 'TOT','Ipswich Town': 'IPS'}

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
        cs_rank=df['cs'].rank(ascending=False, method='min')
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
        cs_rank=df['cs'].rank(ascending=False, method='min')
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
        cs_rank=df['cs'].rank(ascending=False, method='min')
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
    
def get_rank(rank):
  if (rank % 100 >= 11 and rank % 100 <= 13):
    return str(rank)+'th'
  if (rank%10==1):
    return str(rank)+'st'
  if (rank%10==1):
    return str(rank)+'st'
  if (rank%10==2):
    return str(rank)+'nd'
  if (rank%10==3):
    return str(rank)+'rd'
  else:
    return str(rank)+'th'

def get_text(team_name,start_gw,end_gw,team_stats,data_type):
    if data_type=='overall':
      data_type =''
    elif data_type=='home':
      data_type='Home '
    elif data_type=='away':
      data_type='Away '
    atk_text=f"{team_emoji[team_name]} {data_type}Attack "
    if num_gw==end_gw-start_gw+1:
      atk_text+=f"so far this season [GW{start_gw}-GW{end_gw}] :\n\n"
    else:
      atk_text+=f"Between GW{start_gw} & GW{end_gw} :\n\n"
    atk_text+=f"⚽️ {int(team_stats['atk']['goals'])} goals scored ({get_rank(int(team_stats['atk']['goal_rank']))});\n"
    atk_text+=f"⚙️ xG = {team_stats['atk']['xg']} ({get_rank(int(team_stats['atk']['xg_rank']))});\n"
    atk_text+=f"👟 {int(team_stats['atk']['shots'])} shots ({get_rank(int(team_stats['atk']['shots_rank']))});\n"
    atk_text+=f"📦 {int(team_stats['atk']['sib'])} shots in box ({get_rank(int(team_stats['atk']['sib_rank']))});\n"
    atk_text+=f"🎯 {int(team_stats['atk']['sot'])} shots on target ({get_rank(int(team_stats['atk']['sot_rank']))});\n"
    atk_text+=f"💥 {int(team_stats['atk']['bc'])} big chances ({get_rank(int(team_stats['atk']['bc_rank']))});\n"
    atk_text+=f"❌ Failed to score {int(team_stats['atk']['failed_to_score'])}: ({get_rank(int(team_stats['atk']['fts_rank']))});"

    def_text=f"{team_emoji[team_name]} {data_type}Defence "
    if num_gw==end_gw-start_gw+1:
      def_text+=f"so far this season [GW{start_gw}-GW{end_gw}] :\n\n"
    else:
      def_text+=f"Between GW{start_gw} & GW{end_gw} :\n\n"
    def_text+=f"🥅 {int(team_stats['def']['cs'])} Clean Sheets ({get_rank(int(team_stats['def']['cs_rank']))});\n"
    def_text+=f"⚽️ {int(team_stats['def']['goalsc'])} goals Conceded ({get_rank(int(team_stats['def']['goalc_rank']))});\n"
    def_text+=f"⚙️ xGC = {team_stats['def']['xgc']} ({get_rank(int(team_stats['def']['xgc_rank']))});\n"
    def_text+=f"👟 {int(team_stats['def']['shotsc'])} shots Conceded ({get_rank(int(team_stats['def']['shotsc_rank']))});\n"
    def_text+=f"📦 {int(team_stats['def']['sibc'])} shots in box Conceded ({get_rank(int(team_stats['def']['sibc_rank']))});\n"
    def_text+=f"🎯 {int(team_stats['def']['sotc'])} shots on target Conceded ({get_rank(int(team_stats['def']['sotc_rank']))});\n"
    def_text+=f"💥 {int(team_stats['def']['bcc'])} big chances Conceded ({get_rank(int(team_stats['def']['bcc_rank']))});"

    return atk_text,def_text

def get_matches(stats_type,data_type,team,start_gw,end_gw):
  stats=list(teams_stats_db.find())
  if stats_type=='atk':
    if data_type=='home':
      home=[i for i in stats if i['team H']==team]
      home_df=pd.DataFrame(home)
      home_df=home_df[home_df['GW']>=start_gw]
      home_df=home_df[home_df['GW']<=end_gw]
      home_df=home_df[['team A','GW','Goals H','xG H','Shots H','SiB H','SoT H','BC H']]
      home_df.loc[:,'team A']=home_df['team A'].apply(lambda x: teams_short_names.get(x, x) + ' (H)')
      home_df.columns=['vs','gw','goals','xg','shots','sib','sot','bc']
      home_df.loc[:,'delta_xg']=home_df['goals']-home_df['xg']
      home_df['delta_xg']=home_df['delta_xg'].apply(lambda x:round(x,2))
      home_df=home_df[['gw','vs','goals','xg','delta_xg','shots','sib','sot','bc']]
      result = [ row.to_dict() for _, row in home_df.iterrows() ]
      return result

    elif data_type=='away':
      away=[i for i in stats if i['team A']==team]
      away_df=pd.DataFrame(away)
      away_df=away_df[away_df['GW']>=start_gw]
      away_df=away_df[away_df['GW']<=end_gw]
      away_df=away_df[['team H','GW','Goals A','xG A','Shots A','SiB A','SoT A','BC A']]
      away_df.loc[:,'team H']=away_df['team H'].apply(lambda x: teams_short_names.get(x, x) + ' (A)')
      away_df.columns=['vs','gw','goals','xg','shots','sib','sot','bc']
      away_df.loc[:,'delta_xg']=away_df['goals']-away_df['xg']
      away_df['delta_xg']=away_df['delta_xg'].apply(lambda x:round(x,2))
      away_df=away_df[['gw','vs','goals','xg','delta_xg','shots','sib','sot','bc']]
      result = [ row.to_dict() for _, row in away_df.iterrows() ]
      return result
    
    elif data_type=='overall':
      home=[i for i in stats if i['team H']==team]
      home_df=pd.DataFrame(home)
      home_df=home_df[home_df['GW']>=start_gw]
      home_df=home_df[home_df['GW']<=end_gw]
      home_df=home_df[['team A','GW','Goals H','xG H','Shots H','SiB H','SoT H','BC H']]
      home_df.loc[:,'team A']=home_df['team A'].apply(lambda x: teams_short_names.get(x, x) + ' (H)')
      home_df.columns=['vs','gw','goals','xg','shots','sib','sot','bc']
      home_df.loc[:,'delta_xg']=home_df['goals']-home_df['xg']
      home_df['delta_xg']=home_df['delta_xg'].apply(lambda x:round(x,2))
      home_df=home_df[['gw','vs','goals','xg','delta_xg','shots','sib','sot','bc']]
      away=[i for i in stats if i['team A']==team]
      away_df=pd.DataFrame(away)
      away_df=away_df[away_df['GW']>=start_gw]
      away_df=away_df[away_df['GW']<=end_gw]
      away_df=away_df[['team H','GW','Goals A','xG A','Shots A','SiB A','SoT A','BC A']]
      away_df.loc[:,'team H']=away_df['team H'].apply(lambda x: teams_short_names.get(x, x) + ' (A)')
      away_df.columns=['vs','gw','goals','xg','shots','sib','sot','bc']
      away_df.loc[:,'delta_xg']=away_df['goals']-away_df['xg']
      away_df['delta_xg']=away_df['delta_xg'].apply(lambda x:round(x,2))
      away_df=away_df[['gw','vs','goals','xg','delta_xg','shots','sib','sot','bc']]
      overall_df=pd.concat([home_df,away_df],axis=0)
      overall_df=overall_df.sort_values(by=['gw'])
      result = [ row.to_dict() for _, row in overall_df.iterrows() ]
      return result
  
  elif stats_type=='def':
    if data_type=='home':
      home=[i for i in stats if i['team H']==team]
      home_df=pd.DataFrame(home)
      home_df=home_df[home_df['GW']>=start_gw]
      home_df=home_df[home_df['GW']<=end_gw]
      home_df=home_df[['team A','GW','Goals A','xG A','Shots A','SiB A','SoT A','BC A']]
      home_df.loc[:,'team A']=home_df['team A'].apply(lambda x: teams_short_names.get(x, x) + ' (H)')
      home_df.columns=['vs','gw','goalsc','xgc','shotsc','sibc','sotc','bcc']
      home_df.loc[:,'delta_xgc']=home_df['goalsc']-home_df['xgc']
      home_df['delta_xgc']=home_df['delta_xgc'].apply(lambda x:round(x,2))
      home_df=home_df[['gw','vs','goalsc','xgc','delta_xgc','shotsc','sibc','sotc','bcc']]
      result = [ row.to_dict() for _, row in home_df.iterrows() ]
      return result
    
    elif data_type=='away':
      away=[i for i in stats if i['team A']==team]
      away_df=pd.DataFrame(away)
      away_df=away_df[away_df['GW']>=start_gw]
      away_df=away_df[away_df['GW']<=end_gw]
      away_df=away_df[['team H','GW','Goals H','xG H','Shots H','SiB H','SoT H','BC H']]
      away_df.loc[:,'team H']=away_df['team H'].apply(lambda x: teams_short_names.get(x, x) + ' (A)')
      away_df.columns=['vs','gw','goalsc','xgc','shotsc','sibc','sotc','bcc']
      away_df.loc[:,'delta_xgc']=away_df['goalsc']-away_df['xgc']
      away_df['delta_xgc']=away_df['delta_xgc'].apply(lambda x:round(x,2))
      away_df=away_df[['gw','vs','goalsc','xgc','delta_xgc','shotsc','sibc','sotc','bcc']]
      result = [ row.to_dict() for _, row in away_df.iterrows() ]
      return result
  
    elif data_type=='overall':
      home=[i for i in stats if i['team H']==team]
      home_df=pd.DataFrame(home)
      home_df=home_df[home_df['GW']>=start_gw]
      home_df=home_df[home_df['GW']<=end_gw]
      home_df=home_df[['team A','GW','Goals A','xG A','Shots A','SiB A','SoT A','BC A']]
      home_df.loc[:,'team A']=home_df['team A'].apply(lambda x: teams_short_names.get(x, x) + ' (H)')
      home_df.columns=['vs','gw','goalsc','xgc','shotsc','sibc','sotc','bcc']
      home_df.loc[:,'delta_xgc']=home_df['goalsc']-home_df['xgc']
      home_df['delta_xgc']=home_df['delta_xgc'].apply(lambda x:round(x,2))
      home_df=home_df[['gw','vs','goalsc','xgc','delta_xgc','shotsc','sibc','sotc','bcc']]
      away=[i for i in stats if i['team A']==team]
      away_df=pd.DataFrame(away)
      away_df=away_df[away_df['GW']>=start_gw]
      away_df=away_df[away_df['GW']<=end_gw]
      away_df=away_df[['team H','GW','Goals H','xG H','Shots H','SiB H','SoT H','BC H']]
      away_df.loc[:,'team H']=away_df['team H'].apply(lambda x: teams_short_names.get(x, x) + ' (A)')
      away_df.columns=['vs','gw','goalsc','xgc','shotsc','sibc','sotc','bcc']
      away_df.loc[:,'delta_xgc']=away_df['goalsc']-away_df['xgc']
      away_df['delta_xgc']=away_df['delta_xgc'].apply(lambda x:round(x,2))
      away_df=away_df[['gw','vs','goalsc','xgc','delta_xgc','shotsc','sibc','sotc','bcc']]
      overall_df=pd.concat([home_df,away_df],axis=0)
      overall_df=overall_df.sort_values(by=['gw'])
      result = [ row.to_dict() for _, row in overall_df.iterrows() ]
      return result

