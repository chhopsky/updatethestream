from pydantic import BaseModel, Field
from typing import Text, List, Dict, Optional
import json

class Team(BaseModel):
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

        for tricode, team in data["teams"].items():
            print(team)
            team = Team(**team)
            self.add_edit_team(team)

        for current_match in data["matches"]:
            match = Match(**current_match)
            self.matches.append(match)
        return

    def save_to(self, filename):
        # do write here
        return

    def write_to_stream(self):
        # do text write here
        for index, match in enumerate(self.matches):
            print(match)
            f_teams = open(f"streamlabels\match-{index}-teams.txt", "w")
            f_teams.write(f"{self.teams[match.teams[0]].name}\n")
            f_teams.write(f"{self.teams[match.teams[1]].name}\n")
            f_teams.close()
            f_scores = open(f"streamlabels\match-{index}-scores.txt", "w")
            f_scores.write(f"{match.scores[0]}\n")
            f_scores.write(f"{match.scores[1]}\n")
            f_scores.close()
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

    def add_edit_team(self, team_to_add_edit, callback = None):
        self.teams[team_to_add_edit.tricode] = team_to_add_edit
        print(self.teams)

    teams: Dict = {}
    matches: List[Match] = []
    current_match: int = 0
    game_history: List[Game] = []