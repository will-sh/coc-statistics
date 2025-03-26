from flask import Flask, render_template, jsonify
import requests
import os
import datetime

app = Flask(__name__)

# CoC API configuration
API_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjFjZGM4OGQxLWY0NDEtNDQ4YS05Nzk2LTE1MjhkYTE3MzE3YiIsImlhdCI6MTc0Mjk0ODgxMywic3ViIjoiZGV2ZWxvcGVyLzk0OTBiM2FlLWFlNzEtYTI3OC1jZGQ5LWRkY2RmYzZiNmIyNSIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjI0LjEyNS4xOTEuNjYiXSwidHlwZSI6ImNsaWVudCJ9XX0.VBwVqCtIIBZT8hhtQMkahAhptScZWXPWktkugeC0LDsH6YCRvMM9CACqmP63WBMIITVyPZg5jWnx7XJj0h7zwQ'
CLAN_TAG = '%232GU8CQCGY'  # URL encoded clan tag
API_BASE_URL = 'https://api.clashofclans.com/v1'

# Helper function to make API requests
def make_api_request(endpoint):
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }
    
    response = requests.get(
        f'{API_BASE_URL}/{endpoint}',
        headers=headers
    )
    
    return response

@app.route('/')
def index():
    try:
        # Make the API request to get clan members
        response = make_api_request(f'clans/{CLAN_TAG}/members')
        
        # Check if the request was successful
        if response.status_code == 200:
            clan_data = response.json()
            return render_template('index.html', clan_members=clan_data.get('items', []))
        else:
            error_message = f"Error: {response.status_code} - {response.text}"
            return render_template('error.html', error=error_message)
            
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/api/members')
def get_members_api():
    try:
        # Make the API request to get clan members
        response = make_api_request(f'clans/{CLAN_TAG}/members')
        
        # Return the JSON response directly
        return jsonify(response.json())
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clan')
def clan_description():
    try:
        # Make the API request to get clan details
        response = make_api_request(f'clans/{CLAN_TAG}')
        
        # Check if the request was successful
        if response.status_code == 200:
            clan_data = response.json()
            return render_template('clan.html', clan=clan_data)
        else:
            error_message = f"Error: {response.status_code} - {response.text}"
            return render_template('error.html', error=error_message)
            
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/warlog')
def war_log():
    try:
        # Make the API request to get clan war log
        response = make_api_request(f'clans/{CLAN_TAG}/warlog')
        
        # Check if the request was successful
        if response.status_code == 200:
            warlog_data = response.json()
            wars = []
            
            # Process each war entry
            for war in warlog_data.get('items', []):
                # Determine if our clan won, lost, or tied
                if war['result'] == 'win':
                    result = 'win'
                elif war['result'] == 'lose':
                    result = 'lose'
                else:
                    result = 'tie'
                
                # Create a simplified war object with the data we need
                war_obj = {
                    'result': result,
                    'teamSize': war['teamSize'],
                    'endTime': war['endTime'],
                    'clan': war['clan'],
                    'opponent': war['opponent']
                }
                
                wars.append(war_obj)
                
            return render_template('warlog.html', wars=wars)
        else:
            error_message = f"Error: {response.status_code} - {response.text}"
            return render_template('error.html', error=error_message)
            
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/current-war')
def current_war():
    try:
        # Make the API request to get current war information
        response = make_api_request(f'clans/{CLAN_TAG}/currentwar')
        
        # Check if the request was successful
        if response.status_code == 200:
            war_data = response.json()
            return render_template('current_war.html', war=war_data)
        else:
            error_message = f"Error: {response.status_code} - {response.text}"
            return render_template('error.html', error=error_message)
            
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/player/<player_tag>')
def player_details(player_tag):
    try:
        # URL encode the player tag (add # prefix if not present)
        if not player_tag.startswith('%23') and not player_tag.startswith('#'):
            player_tag = '%23' + player_tag
        elif player_tag.startswith('#'):
            player_tag = '%23' + player_tag[1:]
        
        # Make the API request to get player information
        response = make_api_request(f'players/{player_tag}')
        
        # Check if the request was successful
        if response.status_code == 200:
            player_data = response.json()
            return render_template('player.html', player=player_data)
        else:
            error_message = f"Error: {response.status_code} - {response.text}"
            return render_template('error.html', error=error_message)
            
    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)