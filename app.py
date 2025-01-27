from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import re
import os 
from pymongo import MongoClient
from datetime import datetime
from price_change import get_price_change_text
from injury_updates import get_injury_updates_text
from teams_stats import num_gw,filter_by_gw,teams_names,get_text,get_matches
from players_stats import prepare_players,get_player_matches,id_player
from urllib.parse import unquote


app = Flask(__name__)
app.secret_key = 'f3082ef12d47bf71416425c7eef8d573'
CORS(app)

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
collection = db['accounts']
price_change_db=db['price_change']
injury_updates_db=db['injuries']
teams_stats_db=db['teams_stats']

if 'accounts' not in db.list_collection_names():
    db.create_collection('accounts')
    collection.create_index('username', unique=True)
    collection.create_index('password', unique=True)
    collection.create_index('email', unique=True)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = collection.find_one({'username': username, 'password': password})

        if account:
            session['loggedin'] = True
            session['id'] = str(account['_id'])
            session['username'] = account['username']
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account = collection.find_one({'username': username})

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            collection.insert_one({'username': username, 'password': password, 'email': email})
            msg = 'You have successfully registered!'
            return render_template('login.html')
    return render_template('register.html', msg=msg)

# price change
@app.route("/price_change")
def price_change():
    price_changed_list=list(price_change_db.find())
    day_data=[]
    for price_changed in price_changed_list:
        data={'day':price_changed['day'],'id':price_changed['_id']}
        risers={'players':[price_changed['web_name'][i] for i in range(len(price_changed['web_name'])) if price_changed['cost_change_event'][i]==1],
                'cost':[price_changed['now_cost'][i] for i in range(len(price_changed['now_cost'])) if price_changed['cost_change_event'][i]==1],
                'team':[price_changed['team'][i] for i in range(len(price_changed['team'])) if price_changed['cost_change_event'][i]==1]}
        fallers={'players':[price_changed['web_name'][i] for i in range(len(price_changed['web_name'])) if price_changed['cost_change_event'][i]==-1],
                'cost':[price_changed['now_cost'][i] for i in range(len(price_changed['now_cost'])) if price_changed['cost_change_event'][i]==-1],
                'team':[price_changed['team'][i] for i in range(len(price_changed['team'])) if price_changed['cost_change_event'][i]==-1]}
        data['risers']=risers
        data['fallers']=fallers
        day_data.append(data)

    return render_template("price_change.html",day_data=day_data)

@app.route('/get-copy-price-change', methods=['GET'])
def get_copy_price_change():
    id = request.args.get('id', type=str)
    if not id:
        return jsonify({'error': 'No ID provided'}), 400
    price_changes=list(price_change_db.find())
    price_change_df = next((item for item in price_changes if str(item['_id']) == str(id)), None)
    if not price_change_df:
        return jsonify({'error': 'Injury not found'}), 404
    text_to_copy = get_price_change_text(price_change_df)
    return jsonify({'text': text_to_copy})

# injury updates
@app.route("/injury_updates")
def injury_updates():
    injuries=list(injury_updates_db.find())
    current_date=datetime.now()
    day=f'{str(current_date.day)}/{str(current_date.month)}/{str(current_date.year)}'
    return render_template("injury_updates.html",injuries=injuries,day=day)

@app.route('/get-copy-injury-updates', methods=['GET'])
def get_copy_injury_updates():
    id = request.args.get('id', type=str)
    if not id:
        return jsonify({'error': 'No ID provided'}), 400
    injuries=list(injury_updates_db.find())
    injury = next((item for item in injuries if str(item['_id']) == str(id)), None)
    if not injury:
        return jsonify({'error': 'Injury not found'}), 404
    text_to_copy = get_injury_updates_text(injury)
    return jsonify({'text': text_to_copy})

# teams stats
@app.route("/atk_stats")
def atk_stats():
    return render_template("atk_stats.html",num_gw=num_gw)

@app.route("/def_stats")
def def_stats():
    return render_template("def_stats.html",num_gw=num_gw)

@app.route('/get_stats', methods=['POST'])
def get_stats():
    data=request.get_json()
    start_gw = int(data.get('start_gw', 1))
    end_gw = int(data.get('end_gw', num_gw))
    stats_type=data.get('stats_type','atk')
    sort_by=data.get('sort_by','team')
    sort_order=data.get('sort_order','desc')

    data_type = data.get('data_type')
    stats_data=filter_by_gw(stats_type,data_type,start_gw,end_gw,sort_by,sort_order)
    return jsonify(stats=stats_data,data_type=data_type,num_gw=num_gw)

# team card
@app.route("/team_card")
def team_card():
    return render_template("team_card.html",num_gw=num_gw,teams_names=teams_names)
 
@app.route('/team/<team_name>', methods=['GET', 'POST'])
def team_page(team_name):
    team_name = unquote(team_name)
    session['team_name']=team_name
    team_name=team_name.upper()
    return render_template("team_page.html", team_name=team_name,num_gw=num_gw)

@app.route('/get_team_page', methods=['POST'])
def get_team_page():
    team_stats={}
    data=request.get_json()
    start_gw = int(data.get('start_gw', 1))
    end_gw = int(data.get('end_gw', num_gw))
    data_type = data.get('data_type')
    team_name = session.get('team_name')
    team_name = unquote(team_name)
    atk_stats=filter_by_gw('atk',data_type,start_gw,end_gw,'team','asc')
    def_stats=filter_by_gw('def',data_type,start_gw,end_gw,'team','asc')
    team_stats['atk']=[data for data in atk_stats if data['team']==team_name][0]
    team_stats['def']=[data for data in def_stats if data['team']==team_name][0]
    
    atk_text,def_text=get_text(team_name,start_gw,end_gw,team_stats,data_type)
    return jsonify(team_stats=team_stats,data_type=data_type,num_gw=num_gw,atk_text=atk_text,def_text=def_text)

# team comparison
@app.route("/team_comparison")
def team_comparison():
    return render_template("team_comparison.html",num_gw=num_gw,teams_names=teams_names)

@app.route('/get_comparison', methods=['POST','GET'])
def get_comparison():
    team_stats={}
    data=request.get_json()
    start_gw = int(data.get('start_gw', 1))
    end_gw = int(data.get('end_gw', num_gw))
    team1=data.get('team1','Arsenal')
    team2=data.get('team2','Arsenal')
    atk_def=data.get('atk_def','atk')
    data_type = data.get('data_type','overall')

    if(team1=='SELECT' or team2=='SELECT'):
        team1='select team1'
        team2='select team2'
    else:
        if(atk_def=='atk'):
            atk_stats=filter_by_gw('atk',data_type,start_gw,end_gw,'team','asc')
            team_stats['team1']=[data for data in atk_stats if data['team']==team1][0]
            team_stats['team2']=[data for data in atk_stats if data['team']==team2][0]
        if(atk_def=='def'):
            def_stats=filter_by_gw('def',data_type,start_gw,end_gw,'team','asc')
            team_stats['team1']=[data for data in def_stats if data['team']==team1][0]
            team_stats['team2']=[data for data in def_stats if data['team']==team2][0]
    return jsonify(team_stats=team_stats,data_type=data_type,num_gw=num_gw,team1=team1,team2=team2)

# team matches
@app.route("/team_matches")
def team_matches():
    return render_template("team_matches.html",num_gw=num_gw,teams_names=teams_names)

@app.route('/get_team_matches', methods=['POST','GET'])
def get_team_matches():
    data=request.get_json()
    start_gw = int(data.get('start_gw', 1))
    end_gw = int(data.get('end_gw', num_gw))
    team=data.get('team','Arsenal')
    atk_def=data.get('atk_def','atk')
    data_type = data.get('data_type','overall')
    if(team=='SELECT'):
        team='select team'
    else:
        matches=get_matches(atk_def,data_type,team,start_gw,end_gw)
    return jsonify(matches=matches,data_type=data_type,num_gw=num_gw,team=team)

# players stats
@app.route("/players_stats")
def players_stats():
    return render_template("players_stats.html",num_gw=num_gw)

@app.route('/get_players_stats', methods=['POST'])
def get_players_stats():
    data=request.get_json()
    start_gw = int(data.get('start_gw', 1))
    end_gw = int(data.get('end_gw', num_gw))

    position = data.get('position')
    stats_data=prepare_players(position,start_gw,end_gw)
    return jsonify(stats=stats_data,position=position,num_gw=num_gw)

@app.route('/player_page/<player_id>', methods=['GET', 'POST'])
def player_page(player_id):
    player_id = unquote(player_id)
    session['player_id']=player_id
    print(player_id)
    player_name=id_player[int(player_id)]
    return render_template("player_page.html", player_name=player_name,num_gw=num_gw)

@app.route('/get_player_page', methods=['POST'])
def get_player_page():
    data=request.get_json()
    start_gw = int(data.get('start_gw', 1))
    end_gw = int(data.get('end_gw', num_gw))
    player_id = session.get('player_id')
    player_id = int(unquote(player_id))
    fix=get_player_matches(player_id,start_gw,end_gw)
    return jsonify(fix=fix,num_gw=num_gw)

@app.route('/index')
def index():
    if 'loggedin' in session:
        return render_template('index.html',session=session)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

