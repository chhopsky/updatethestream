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