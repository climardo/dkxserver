import json, re, requests, sys
from datetime import datetime
from tempfile import SpooledTemporaryFile

today = datetime.now().strftime('%Y-%m-%d')
def get_curr_week():
    # Get current week
    dk_weeks = "https://live.draftkings.com/api/v1/nfl/weeks"
    r = requests.get(url=dk_weeks)
    curr_week = r.json()['week']
    return curr_week

def get_bye_teams(week=None):
    if week == None:
        week = get_curr_week()

    # Get list of bye_teams by downloading and parsing data from Yahoo Sports
    # Create URL string including week argument
    get_game_data = 'https://api-secure.sports.yahoo.com/v1/editorial/s/scoreboard?leagues=nfl&week={}&season=current'.format(str(int(week) + 1))
    r = requests.get(url=get_game_data) # GET URL
    game_data = r.json()['service']['scoreboard'] # All relevant data is contained within service/scoreboard/*

    # Search through list of teams, if the id number matches one in bye_teams_raw, then add to list bye_teams
    if 'bye_teams' in game_data.keys():
        bye_teams_raw = set(game_data['bye_teams']) # Bye teams are listed as team id numbers
        bye_teams = [] 
        for team in game_data['teams']:
            if team in bye_teams_raw:
                bye_teams.append(game_data['teams'][team]['display_name'])
        
        # Create a string with list items separated by commas
        bye_teams_str = ', '.join(bye_teams)
    else:
        bye_teams_str = "None"
    
    return bye_teams_str # Return string

def dk_data(week=None):
    if week == None:
        week = get_curr_week()

    # Get data from live.draftkings.com for week specified by user input
    data = '{"sport":"nfl","embed":"stats"}'

    # Visit dk_live to obtain cookies used to make POST request to dk_api
    dk_live = 'https://live.draftkings.com/sports/nfl/seasons/2019/week/{}/games/all'.format(week)
    dk_api = 'https://live.draftkings.com/api/v2/leaderboards/players/seasons/2019/weeks/{}'.format(week)

    # Create a session to maintain cookies
    s = requests.session()
    s0 = s.get(dk_live)
    # Create headers for POST request
    headers = {
        'Host': 'live.draftkings.com',
        'Connection': 'keep-alive',
        'Content-Length': '31',
        'Origin': 'https://live.draftkings.com',
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 12499.46.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.81 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://live.draftkings.com/sports/nfl/seasons/2019/week/{}/games/all'.format(week),
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,la;q=0.8'
    }
    # Make a post request including headers and data
    dk_resp = s.post(dk_api, headers=headers, data=data)

    # Convert dk_resp (string) into a JSON object (dict)
    raw = json.loads(dk_resp.text).get('data')
    # Include only players with stats and salary, assuming players with neither were not drafted
    players = [x for x in raw if x.get('salary') and x['stats']]
    # Sort players in descending order based on fantasyPoints
    players = sorted(players, key=lambda x: x['fantasyPoints'], reverse=True)

    for player in players:
        # Create fpts_salary (int:quotient of fantasyPoints and salary) element for each player (dict)
        fpts_salary = player['fantasyPoints'] / player['salary']
        player.update({"fpts_salary": fpts_salary})

        # Create a fullName element for each player by combining firstName (string) and lastName (string)
        fullName = player['firstName']
        if player['lastName']:
            fullName += ' {}'.format(player['lastName'])
            
        player.update({"fullName": '{} {}'.format(player['firstName'], player['lastName'])})

    return players

def superlatives(week=None):
    if week == None:
        week = get_curr_week()

    players = dk_data(week)
    # Create a list (bust_players) of dicts where salary is greater than or equal to 5000
    bust_players = [x for x in players if x.get('salary') >= 5000]

    # MVP is the player with the most fantasyPoints
    # Sleeper is the player with the most fpts_salary (see previously added element)
    # Bust is the player with the least fpts_salary from bust_players list (see previously created list)
    mvp = max(players, key=lambda x: x['fantasyPoints'])
    sleeper = max(players, key=lambda x: x['fpts_salary'])
    bust = min(bust_players, key=lambda x: x['fpts_salary'])

    superlatives = {
        'mvp': mvp['fullName'],
        'sleeper': sleeper['fullName'],
        'bust': bust['fullName'],
    }

    return superlatives

def get_drafted(results_file, week=None):
    if week == None:
        week = get_curr_week()
    
    mvp_draft, sleeper_draft, bust_draft, users, drafted = [], [], [], [], set()
    players = dk_data(week)

    with open(results_file) as csv_file:
        # Use only the first 6 fields of csv_file to create a list (lines)
        for line in csv_file:
            lines = line.split(',')[:6]

            # Add entries to users list containing user and user_pts as a string
            if lines[0] and lines[0] != 'Rank':
                user_name = lines[2]
                user_pts = lines[4]
                users.append("{} - {} fpts".format(user_name, user_pts))

            # Add list of users whose teams contain a player to the specified lists
            if lines[0] and superlatives(week)['mvp'] in lines[5]:
                mvp_draft.append(lines[2])
            if lines[0] and superlatives(week)['sleeper'] in lines[5]:
                sleeper_draft.append(lines[2])
            if lines[0] and superlatives(week)['bust'] in lines[5]:
                bust_draft.append(lines[2])
            
            # Add drafted players to drafted set
            # Create draft (list) by splitting each lines[5], omitting positions (QB, RB, etc.)
            # Add each draft_player (item) from draft (list) to drafted (set), while trimming (strip()) whitespace
            if lines[5] != 'Lineup' and lines[5]:
                draft = re.split('QB| RB | WR | TE | FLEX | DST ', lines[5])
                for draft_player in draft:
                    if draft_player != '':
                        drafted.add(draft_player.strip())

    # Create alphabetical list of user_pts
    sorted_list = sorted(users, key=str.casefold)
    i = 0
    for x in sorted_list:
        sorted_list[i] = x.split()[2]
        i += 1

    # Find top undrafted player (draft_dodger), players list is sorted by highest fantasyPoints
    find_undrafted = []
    for player in players:
        if player['fullName'] not in drafted:
            find_undrafted.append(player)

    draft_dodger = find_undrafted[0]

    result = {
        'draft_dodger': draft_dodger['fullName'],
        'sorted_scores': '\n'.join(sorted_list),
        'users_pts_list': users,
        'mvp_draft': mvp_draft,
        'sleeper_draft': sleeper_draft,
        'bust_draft': bust_draft
    }

    return result

def draft_string(my_list):
    # Function used to display 'Drafted by' list or 'Undrafted'
    if my_list:
        members = ', '.join(my_list)
        return 'Drafted by <span class="font-weight-bold">{}</span>'.format(members)
    else:
        return '<span class="font-weight-bold">Undrafted</span>'

def png_name(player, week=None):
    if week == None:
        week = get_curr_week()

    # Function used to create a string (filename) used to rename player screenshots
    filename = 'week-' + week + '-'
    filename += '-'.join(player.split())
    filename += '.png'
    return filename.lower()

def create_results(users, output_file):
    # Compose ordered list HTML string of winners (users[:3])
    winner_str = '<ol>\n'
    for user in users[:3]:
        winner_str += '\t<li>{}</li>\n'.format(user)
    winner_str += '</ol>'
    try:
        # Write winner_str to file (results_output)
        with open(output_file, 'w+') as results_output:
            results_output.write(winner_str)
        return 0
    except:
        return 1

def create_blogpost(results_file, template="/static/weekly-template.md", values=None, contest_id=None, week=None, outdir="/temp/"):
    if values == None:
        contest_id = contest_id
        week = week
        drafted = get_drafted(results_file, week)
        best = superlatives(week)
        values = {
            'bust_draft': draft_string(drafted['bust_draft']),
            'bust': best['bust'],
            'bye_teams': get_bye_teams(week),
            'contest_id': contest_id,
            'draft_dodger': drafted['draft_dodger'],
            'mvp_draft': draft_string(drafted['mvp_draft']),
            'mvp': best['mvp'],
            'sleeper_draft': drafted['sleeper_draft'],
            'sleeper': best['sleeper'],
            'week': week
        }
        filename = today + '-week-' + values['week']+ '-results.md'
    try:
        # Replace placeholders in weekly-template with values listed below
        with open(template, 'r') as weekly_template:
            with f"{outdir}/{filename}" as weekly_output:
                template_str = weekly_template.read()
                weekly_output.write(template_str.format(
                    bust_draft=draft_string(values['bust_draft']), 
                    bust_png=png_name(values['bust'], week),
                    bye_teams=values['bye_teams'],
                    contest_id=values['contest_id'],
                    draft_dodger_png=png_name(values['draft_dodger']),
                    mvp_draft=draft_string(values['mvp_draft']),
                    mvp_png=png_name(values['mvp']),
                    sleeper_draft=draft_string(values['sleeper_draft']),
                    sleeper_png=png_name(values['sleeper']),
                    week=values['week'])
                )
                return weekly_output
    except:
        return 1