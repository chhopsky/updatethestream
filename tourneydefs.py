from pydantic import BaseModel, Field
from typing import Text, List, Dict, Optional
from uuid import uuid4
import json

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
        with open(filename) as f:
            data = json.load(f)

        self.mapping = {}

        for tricode, team in data["teams"].items():
            print(team)
            team = Team(**team)
            self.add_team(team)
            self.mapping[team.tricode] = team.id

        for current_match in data["matches"]:
            match = Match(**current_match)
            match.teams[0] = self.mapping.get(match.teams[0], match.teams[0])
            match.teams[1] = self.mapping.get(match.teams[1], match.teams[1])
            self.matches.append(match)
        return

    def save_to(self, filename):
        # do write here
        return

    def write_to_stream(self):
        # do text write here
        for index, match in enumerate(self.matches):
            print(match)
            with open(f"streamlabels\match-{index}-teams.txt", "w") as f_teams:
                team1 = self.teams.get(match.teams[0])
                team2 = self.teams.get(match.teams[1])
                f_teams.write(f"{team1.name}\n")
                f_teams.write(f"{team2.name}\n")

            with open(f"streamlabels\match-{index}-scores.txt", "w") as f_scores:
                f_scores.write(f"{match.scores[0]}\n")
                f_scores.write(f"{match.scores[1]}\n")
        
        current_teams = self.get_teams_from_matchid(self.current_match)
        with open(f"streamlabels\current-match-teams.txt", "w") as f_current:
            f_current.write(f"{current_teams[0].name} vs {current_teams[1].name}\n")
            f_current.close()

        with open(f"streamlabels\current-match-team1-tricode.txt", "w") as f_current:
            f_current.write(f"{current_teams[0].tricode}\n")

        with open(f"streamlabels\current-match-team2-tricode.txt", "w") as f_current:
            f_current.write(f"{current_teams[1].tricode}\n")
        
        with open(f"streamlabels\current-match-team1-name.txt", "w") as f_current:
            f_current.write(f"{current_teams[0].name}\n")

        with open(f"streamlabels\current-match-team2-name.txt", "w") as f_current:
            f_current.write(f"{current_teams[1].name}\n")

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
        print(self.teams)

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
        team1 = self.teams[self.matches[id].teams[0]]
        team2 = self.teams[self.matches[id].teams[1]]
        return [team1, team2]

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