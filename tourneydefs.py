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

class Tournament(BaseModel):
   
    def load_from(self, filename="tournament-config.json"):
        with open(filename) as f:
            data = json.load(f)

        self.teams = data["teams"]

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
            f_teams.write(f"{self.teams[match.teams[0]]['name']}\n")
            f_teams.write(f"{self.teams[match.teams[1]]['name']}\n")
            f_teams.close()
            f_scores = open(f"streamlabels\match-{index}-scores.txt", "w")
            f_scores.write(f"{match.scores[0]}\n")
            f_scores.write(f"{match.scores[1]}\n")
            f_scores.close()
        return

    def game_complete(self, match_id, winner_index):
        cutoff = self.matches[match_id].best_of / 2
        self.matches[match_id].scores[winner_index] += 1
        self.matches[match_id].in_progress = True
        if self.matches[match_id].scores[0] > cutoff or self.matches[match_id].scores[1] > cutoff:
            self.matches[match_id].in_progress = False
            self.matches[match_id].finished = True
            self.matches[match_id].winner = winner_index
            self.current_match += 1
        
        finished_game = Game(match = match_id, winner=winner_index)
        self.game_history.append(finished_game)

    teams: Dict = {}
    matches: List[Match] = []
    current_match: int = 0
    game_history: List[Game] = []