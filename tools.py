from tourneydefs import Tournament, Match, Team
from urllib import request
import requests
import json
import pprint
import random
import string

def poll_challonge(tournament_id, API_KEY):
    url = f"https://api.challonge.com/v1/tournaments/{tournament_id}/matches.json?api_key={API_KEY}"
    page = request.urlopen(url)
    response_matches = page.read()
    url = f"https://api.challonge.com/v1/tournaments/{tournament_id}/participants.json?api_key={API_KEY}"
    page = request.urlopen(url)
    response_participants = page.read()
    response = {
        "matches": json.loads(response_matches.decode()),
        "participants": json.loads(response_participants.decode())
    }
    return response

def is_tricode_unique(teamname, tricodelist):
    if teamname in tricodelist:
        return False
    else:
        return True

def generate_random_tricode_from_name(teamname, anything=False):
    i = []
    source_string = teamname
    if anything:
        source_string = string.ascii_uppercase
    
    i.append(random.choice(range(len(source_string))))
    i.append(random.choice(range(len(source_string))))
    i.append(random.choice(range(len(source_string))))
    new_tricode = source_string[i[0]] + source_string[i[1]] + source_string[i[2]]
    return new_tricode.upper()

def determine_tricode(teamname, tricodelist):
    if " " in teamname or "_" in teamname or "-" in teamname:
        new_teamname = teamname.replace("_", " ").replace("-"," ")
        teamname_split = new_teamname.split(" ")
        if len(teamname_split) > 1:
            if len(teamname_split) >= 3:
                if len(teamname_split[0]) and len(teamname_split[1]) and len(teamname_split[2]):
                    if is_tricode_unique(f"{teamname_split[0][0:1]}{teamname_split[1][0:1]}{teamname_split[2][0:1]}".upper(), tricodelist):
                        return f"{teamname_split[0][0:1]}{teamname_split[1][0:1]}{teamname_split[2][0:1]}".upper()
    if "." in teamname:
        teamname_split = teamname.split(".")
        if len(teamname_split) > 1:
            if len(teamname_split[0]) and len(teamname_split[1]):
                if is_tricode_unique(f"{teamname_split[0:1]}{teamname_split[1][0:2]}", tricodelist):
                    return f"{teamname_split[0][0:1]}{teamname_split[1][0:2]}"
    if teamname.upper().startswith("TEAM"):
        new_teamname = teamname.upper().lstrip("TEAM").lstrip("_")
        if is_tricode_unique(new_teamname[0:3], tricodelist):
            return new_teamname[0:3]
    if " " in teamname[0:3]:
        new_teamname = f"{teamname}".replace(" ", "")
        if is_tricode_unique(new_teamname[0:3].upper(), tricodelist):
            return new_teamname[0:3].upper()
    if is_tricode_unique(teamname[0:3].upper(), tricodelist):
        return teamname[0:3].upper()
    if len(teamname) > 3:
        if is_tricode_unique(f"{teamname[0:0]}{teamname[-1:]}".upper(), tricodelist):
            return f"{teamname[0:0]}{teamname[-1:]}"
    
    found_tricode = False
    random_tricode = False
    i=0
    while found_tricode is not True:
        new_tricode = generate_random_tricode_from_name(teamname, anything=random_tricode)
        if is_tricode_unique(new_tricode, tricodelist):
            found_tricode = True
            return new_tricode
        if i > 10:
            random_tricode = True
        if i > 100:
            return "ERR"
        i += 1
    

def poll_faceit(tournament_id):
    teams_url = f"https://api.faceit.com/championships/v1/championship/{tournament_id}/subscription"
    teams_response = requests.get(teams_url)
    teams = teams_response.json()
    groups_url = f"https://api.faceit.com/championships/v1/championship/{tournament_id}"
    groups_response = requests.get(groups_url)
    groups = groups_response.json()
    tournament = { "teams": teams, "groups": groups}
    tricodes = []
    teams = {}
    for team in tournament["teams"]["payload"]["items"]:
        current_team = team["team"]
        new_team = Team()
        new_team.id = current_team["id"]
        new_team.name = current_team["name"]
        new_team.tricode = determine_tricode(current_team["name"], tricodes)
        tricodes.append(new_team.tricode)
        teams[new_team.id] = new_team

    match_list = []
    group_config = tournament["groups"]["payload"]["groups"]
    for group in list(group_config.keys()):
        group_url = f"https://api.faceit.com/championships/v1/championship/{tournament_id}/group/{group}/bracket"
        response = requests.get(group_url)
        group_json = response.json()
        for match in group_json["payload"]["matches"].values():
            new_match = Match()
            new_match.best_of = match.get("bestOf")
            new_match.id = match["id"]
            new_match.teams = [0,0]
            if match["status"] == "finished":
                new_match.finished = True
                new_match.scores = [0,0]
            if match["status"] == "ongoing":
                new_match.in_progress = True

            for team in match["factions"]:
                
                i = team["number"] - 1
                if team.get("entity"):
                    new_match.teams[i] = team["entity"].get("id")
                    if teams.get(new_match.teams[i]) is None:
                        try:
                            new_team = Team()
                            new_team.id = team["entity"].get("id")
                            if new_team.id != "bye":
                                new_team.name = team["entity"].get("name")
                                new_team.tricode = determine_tricode(new_team.name, tricodes)
                                tricodes.append(new_team.tricode)
                                if new_team.name != "bye":
                                    teams[new_team.id] = new_team
                        except TypeError:
                            pprint.pprint(team)
                        except AttributeError:
                            pprint.pprint(team)
                else:
                    new_match.teams[i] = "666"

                if new_match.finished:
                    new_match.scores[i] = team["score"]
                
                if team.get("winner"):
                    if team["winner"]:
                        new_match.winner = i

            if not (new_match.finished and "bye" in new_match.teams):
                match_list.append(new_match)

    matches = sorted(match_list, key=lambda x: (x.finished, x.in_progress), reverse=True)
    tournament = {"matches": matches, "teams": teams}
    return tournament