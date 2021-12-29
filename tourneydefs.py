from pydantic import BaseModel, Field
from typing import Text, List, Dict, Optional
from uuid import uuid4
import os
import json
import logging
import errno

class Team(BaseModel):
    id: str = ""
    name: str = ""
    tricode: str = ""
    points: int = 0
    logo_big: str = ""
    logo_small: str = ""

class Match(BaseModel):
    teams: List[str] = []
    scores: List[int] = [0, 0]
    best_of: int = 1
    finished: bool = False
    in_progress: bool = False
    winner: int = 2

class Game(BaseModel):
    match: int = 0
    winner: int = 3
    scores: List[int] = [0, 0]

class Tournament(BaseModel):
    def load_from(self, filename="tournament-config.json"):
        try:
            with open(filename) as f:
                data = json.load(f)

                self.mapping = {}
                self.clear_everything()

                for team in data["teams"]:
                    team = Team(**team)
                    id = self.add_team(team)
                    self.mapping[team.tricode] = id

                for current_match in data["matches"]:
                    match = Match(**current_match)
                    match.teams[0] = self.mapping.get(match.teams[0], match.teams[0])
                    match.teams[1] = self.mapping.get(match.teams[1], match.teams[1])
                    self.matches.append(match)

                game_history = data.get("game_history")
                if game_history is not None:
                    for game in game_history:
                        game = Game(**game)
                        self.game_history.append(game)
                current_match = data.get("current_match")
                if current_match is not None:
                    self.current_match = current_match
        except (json.JSONDecodeError, FileNotFoundError):
            return 

        return

    def save_to(self, filename, savestate=False):
        # do write here
        output_dict = {}
        output_dict["teams"] = []
        for key, value in self.teams.items():
            output = { 
                "name": value.name, 
                "tricode": value.tricode, 
                "points": value.points
                }
            output_dict["teams"].append(output)

        output_dict["matches"] = []
        for match in self.matches:
            match_dict = {
                "teams": [self.teams[match.teams[0]].tricode, self.teams[match.teams[1]].tricode],
                "best_of": match.best_of
            }
            
            if savestate:
                match_dict["scores"] = match.scores
                match_dict["finished"] = match.finished
                match_dict["in_progress"] = match.in_progress
                match_dict["winner"] = match.winner
            output_dict["matches"].append(match_dict)

        if savestate:
            output_dict["current_match"] = self.current_match
            output_dict["game_history"] = []
            for game in self.game_history:
                game_dict = {
                    "match": game.match,
                    "winner": game.winner,
                    "scores": game.scores
                }
                output_dict["game_history"].append(game_dict)
        
        with open(filename, "w") as f:
            json.dump(output_dict, f)
        return

    def write_to_stream(self, swap=False):
        # do text write here

        filename = "streamlabels/start.txt"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        for index, match in enumerate(self.matches):
            logging.debug(match)
            with open(f"streamlabels\match-{index}-teams.txt", "w") as f_teams:
                team1 = self.teams.get(match.teams[0])
                team2 = self.teams.get(match.teams[1])
                f_teams.write(f"{team1.name}\n")
                f_teams.write(f"{team2.name}\n")

            with open(f"streamlabels\match-{index}-scores.txt", "w") as f_scores:
                f_scores.write(f"{match.scores[0]}\n")
                f_scores.write(f"{match.scores[1]}\n")
        
        
        current_teams = self.get_teams_from_matchid(self.current_match)
        if current_teams is not None:
            t0 = 0
            t1 = 1
            if swap:
                t0 = 1
                t1 = 0
            with open(f"streamlabels\current-match-teams.txt", "w") as f_current:
                f_current.write(f"{current_teams[t0].name} vs {current_teams[t1].name}\n")
                f_current.close()
            
            with open(f"streamlabels\current-match-tricodes.txt", "w") as f_current:
                f_current.write(f"{current_teams[t0].tricode} vs {current_teams[t1].tricode}\n")
                f_current.close()

            with open(f"streamlabels\current-match-team1-tricode.txt", "w") as f_current:
                f_current.write(f"{current_teams[t0].tricode}\n")

            with open(f"streamlabels\current-match-team2-tricode.txt", "w") as f_current:
                f_current.write(f"{current_teams[t1].tricode}\n")
            
            with open(f"streamlabels\current-match-team1-name.txt", "w") as f_current:
                f_current.write(f"{current_teams[t0].name}\n")

            with open(f"streamlabels\current-match-team2-name.txt", "w") as f_current:
                f_current.write(f"{current_teams[t1].name}\n")

        return
    
    def update_match_scores(self):
        self.current_match = 0
        for i in range(len(self.matches)):
            self.matches[i].scores = [0, 0]
            self.matches[i].winner = 2
            self.matches[i].finished = False
            self.matches[i].in_progress = False
        for game in self.game_history:
            self.process_game(game.match, game.winner)

    def process_game(self, match_id, winner_index):
        cutoff = self.matches[match_id].best_of / 2
        self.matches[match_id].scores[winner_index] += 1
        self.matches[match_id].in_progress = True
        if self.matches[match_id].scores[0] > cutoff or self.matches[match_id].scores[1] > cutoff:
            self.matches[match_id].in_progress = False
            self.matches[match_id].finished = True
            self.matches[match_id].winner = winner_index
            self.current_match += 1

    def game_complete(self, match_id, winner_index):
        self.process_game(match_id, winner_index)
        finished_game = Game(match = match_id, winner=winner_index)
        self.game_history.append(finished_game)

    def add_team(self, team_to_add, callback = None):
        if not team_to_add.id:
            new_team_id = str(uuid4())
            team_to_add.id = new_team_id
        self.teams[team_to_add.id] = team_to_add
        return team_to_add.id

    def edit_team(self, update):
        self.teams[update.id] = update

    def delete_team(self, id):
        # delete any matches they have
        for i, match in reversed(list(enumerate(self.matches))):
            if id in match.teams or self.teams[id].tricode in match.teams:
                del(self.matches[i])
        self.teams.pop(id)
    
    def add_match(self, match):
        self.matches.append(match)

    def delete_match(self, match_id):
        del(self.matches[match_id])

    def edit_match(self, match_id, match):
        self.matches[match_id].teams = match.teams
        self.matches[match_id].best_of = match.best_of

    def get_team_id_by_tricode(self, tricode):
        for key, team in self.teams.items():
            if team.tricode == tricode:
                return key
        return None

    def get_teams_from_matchid(self, id):
        try:
            team1 = self.teams[self.matches[id].teams[0]]
            team2 = self.teams[self.matches[id].teams[1]]
            return [team1, team2]
        except IndexError:
            return None

    def clear_everything(self):
        self.teams = {}
        self.matches = []
        self.game_history = []
        self.current_match = 0
        self.mapping = {}

    teams: Dict = {}
    matches: List[Match] = []
    current_match: int = 0
    game_history: List[Game] = []
    mapping: Dict = {}