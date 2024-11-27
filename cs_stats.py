import http.client
import pandas as pd
import json
import time
import os
import requests
from collections import defaultdict
import tweepy

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

def get_cleansheet_data():
    teams=pd.read_excel(r'C:\Users\ghass\OneDrive\Desktop\injury_updates_actions\website\teams_data_from_2017.xlsx',sheet_name='2024-2025')
    team_names=set()
    for team in teams['team H']:
        team_names.add(team)
    teams_cs={team_name:{} for team_name in team_names}

    gw=teams['GW'].iloc[-1]
    for team in team_names:
        teams_cs[team]={'a':[],'h':[]}
        for i in range(1,gw+1):
            matchy=teams[teams['GW']==i]
            if team in list(matchy['team A']):
                matchy_a=matchy[(matchy['team A']==team)]
                if matchy_a['Goals H'].iloc[0]==0:
                    teams_cs[team]['a'].append(i)
            else:
                matchy_h=matchy[matchy['team H']==team]
                if matchy_h['Goals A'].iloc[0]==0:
                    teams_cs[team]['h'].append(i)
    for team in teams_cs.keys():
        teams_cs[team]['a (%)']=round(len(teams_cs[team]['a'])/(len(teams_cs[team]['a'])+len(teams_cs[team]['h']))*100,2)
        teams_cs[team]['h (%)']=round(len(teams_cs[team]['h'])/(len(teams_cs[team]['a'])+len(teams_cs[team]['h']))*100,2)
    df=pd.DataFrame(teams_cs).T
    df['a']=df['a'].apply(lambda x: len(x))
    df['h']=df['h'].apply(lambda x: len(x))
    df['CS']=df['a']+df['h']
    df=df[['CS','h','a','h (%)','a (%)']]
    df=df.sort_values(by=['CS','a'],ascending=False)
    df=df.reset_index()
    df.columns=['Teams','CS','h','a','h (%)','a (%)']
    return df