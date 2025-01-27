import pandas as pd
import requests

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

managers=url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/','elements')
managers=managers[managers['element_type']==5]
team_manager=dict(zip(managers['team'],managers['web_name']))
teams=url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/','teams')
id_team=dict(zip(teams['id'],teams['name']))
team_position=dict(zip(teams['id'],teams['position']))

df=teams[['name','position','id']]
df['manager'] = df['id'].map(team_manager)
teams_table=df.to_dict(orient="index")
teams_table=[v for k,v in teams_table.items()]
for team_dict in teams_table:
  matches=matches=url_to_df('https://fantasy.premierleague.com/api/fixtures/?future=1')
  matches=matches[(matches['team_a']==team_dict['id']) | (matches['team_h']==team_dict['id'])][['team_a','team_h']]
  matches['opp_team']=matches['team_a']+matches['team_h']-team_dict['id']
  team_dict['fix']=([{str(id_team[x]): team_position[x]} for x in matches['opp_team']])
