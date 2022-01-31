from tourneydefs import Tournament, Match, Team
import requests
import tools
import pprint


tournament_id = "cf6c68c9-2f50-4589-a30c-16817e406b97"

tournament = tools.poll_faceit(tournament_id)
pprint.pprint(tournament)
# teams = {}
# for team in tournament["teams"]["payload"]["items"]:
#     current_team = team["team"]
#     new_team = Team()
#     new_team.id = current_team["id"]
#     new_team.name = current_team["name"]
#     new_team.tricode = current_team["name"][0:3].upper()
#     teams[new_team.id] = new_team

# match_list = []
# group_config = tournament["groups"]["payload"]["groups"]
# for group in list(group_config.keys()):
#     group_url = f"https://api.faceit.com/championships/v1/championship/{tournament_id}/group/{group}/bracket"
#     response = requests.get(group_url)
#     group_json = response.json()
#     for match in group_json["payload"]["matches"].values():
#         new_match = Match()
#         new_match.best_of = match.get("bestOf")
#         new_match.id = match["id"]
#         new_match.teams = [0,0]
#         if match["status"] == "finished":
#             new_match.finished = True
#             new_match.scores = [0,0]
#         if match["status"] == "ongoing":
#             new_match.in_progress = True

#         for team in match["factions"]:
            
#             i = team["number"] - 1
#             if team.get("entity"):
#                 new_match.teams[i] = team["entity"].get("id")
#             else:
#                 new_match.teams[i] = "666"

#             if new_match.finished:
#                 new_match.scores[i] = team["score"]
            
#             if team.get("winner"):
#                 if team["winner"]:
#                     new_match.winner = i

#         if not (new_match.finished and "bye" in new_match.teams):
#             match_list.append(new_match)

# matches = sorted(match_list, key=lambda x: (x.finished, x.in_progress), reverse=True)
