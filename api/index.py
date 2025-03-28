from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import requests
import os
import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key for session management

# CoC API configuration
DEFAULT_API_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImJlNmNmODA3LTYwZTgtNGZjMS05OWU1LWM4NzhhMGUwNDU5NyIsImlhdCI6MTc0MzExMTIyNCwic3ViIjoiZGV2ZWxvcGVyLzk0OTBiM2FlLWFlNzEtYTI3OC1jZGQ5LWRkY2RmYzZiNmIyNSIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjQ1Ljc5LjIxOC43OSJdLCJ0eXBlIjoiY2xpZW50In1dfQ.HBUTplaNAWyArxZUJb5F-fPtHmcQDZpreMZ8MdTwjiCBySRuQWSfwbr0FI4T131Mm7XiMisLNuReXV5lKa0VDA'
CLAN_TAG = '%232GU8CQCGY'  # URL encoded clan tag
API_BASE_URL = 'https://cocproxy.royaleapi.dev/v1'

# Helper function to make API requests
def make_api_request(endpoint):
    # Use user's API token from session if available, otherwise use default
    api_token = session.get('api_token', DEFAULT_API_TOKEN)
    
    headers = {
        'Authorization': f'Bearer {api_token}'
    }
    
    response = requests.get(
        f'{API_BASE_URL}/{endpoint}',
        headers=headers
    )
    
    return response

@app.route('/set-token', methods=['POST'])
def set_token():
    api_token = request.form.get('api_token')
    
    if not api_token:
        flash('API token cannot be empty', 'danger')
        return redirect(url_for('index'))
    
    # Store the API token in the session
    session['api_token'] = api_token
    flash('API token has been set successfully', 'success')
    
    # Redirect back to the homepage
    return redirect(url_for('index'))

@app.route('/')
def index():
    try:
        # Check if API token is set
        has_token = 'api_token' in session
        
        # Make the API request to get clan members
        response = make_api_request(f'clans/{CLAN_TAG}/members')
        
        # Check if the request was successful
        if response.status_code == 200:
            clan_data = response.json()
            return render_template('index.html', clan_members=clan_data.get('items', []), has_token=has_token)
        elif response.status_code == 403 or response.status_code == 401:
            # Unauthorized or forbidden - likely an invalid token
            error_message = "Invalid API token. Please provide a valid Clash of Clans API token."
            return render_template('error.html', error=error_message)
        else:
            error_message = f"Error: {response.status_code} - {response.text}"
            return render_template('error.html', error=error_message)
            
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/clear-token')
def clear_token():
    # Remove the API token from the session
    if 'api_token' in session:
        session.pop('api_token')
        flash('API token has been cleared', 'info')
    
    # Redirect back to the homepage
    return redirect(url_for('index'))

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

@app.route('/clan/<clan_tag>')
def clan_details(clan_tag):
    try:
        # URL encode the clan tag (add # prefix if not present)
        if not clan_tag.startswith('%23') and not clan_tag.startswith('#'):
            clan_tag = '%23' + clan_tag
        elif clan_tag.startswith('#'):
            clan_tag = '%23' + clan_tag[1:]
        
        # Make the API request to get clan information
        response = make_api_request(f'clans/{clan_tag}')
        
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

@app.route('/rankings')
def rankings():
    try:
        return render_template('rankings.html')
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/api/locations')
def get_locations():
    try:
        # Make the API request to get locations
        response = make_api_request('locations')
        
        # Return the JSON response directly
        return jsonify(response.json())
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rankings/<location_id>/<ranking_type>')
def get_rankings(location_id, ranking_type):
    try:
        # Validate ranking type
        valid_ranking_types = ['clans', 'players', 'players-builder-base', 'clans-builder-base', 'capitals']
        if ranking_type not in valid_ranking_types:
            return jsonify({'error': 'Invalid ranking type'}), 400
        
        # Construct the endpoint based on location and ranking type
        if location_id == 'global':
            endpoint = f'locations/global/rankings/{ranking_type}'
        else:
            endpoint = f'locations/{location_id}/rankings/{ranking_type}'
        
        # Make the API request to get rankings
        response = make_api_request(endpoint)
        
        # Return the JSON response directly
        return jsonify(response.json())
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)