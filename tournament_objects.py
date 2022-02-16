from pydantic import BaseModel, Field
from typing import Text, List, Dict, Optional
from uuid import uuid4
import base64
import os


class Team(BaseModel):
    id: str = ""
    name: str = ""
    tricode: str = ""
    points: int = 0
    logo_big: str = ""
    logo_small: str = ""

    def to_dict(self, state=False, b64images=False):
        dict_to_return = {}
        if state:
            dict_to_return = self.__dict__
        else:
            for key, value in self.__dict__.items():
                if key != "points":
                    dict_to_return[key] = value
        if b64images:
            dict_to_return["logo_small_b64"] = self.get_logo_b64()
        return dict_to_return

    def get_name(self):
        if self.name:
            return self.name
        else:
            return self.tricode
        
    def get_tricode(self):
        if self.tricode:
            return self.tricode
        else:
            return self.name

    def get_display_name(self):
        if self.tricode and not self.name:
            return self.tricode
        elif self.name and not self.tricode:
            return self.name
        else:
            return f"{self.tricode}: {self.name}"
    
    def get_logo_b64(self):
        if os.path.isfile(self.logo_small):
            with open(self.logo_small, "rb") as f:
                file = f.read()
                if file:
                    return base64.b64encode(file).decode()

class Match(BaseModel):
    id: str = str(uuid4())
    teams: List[str] = []
    scores: List[int] = [0, 0]
    best_of: int = 1
    finished: bool = False
    in_progress: bool = False
    winner: int = 2

    def to_dict(self, state=False):
        if state:
            return self.__dict__
        else:
            list_to_not_return = ["scores", "finished", "in_progress", "winner"]
            dict_to_return = {}
            for key, value in self.__dict__.items():
                if key not in list_to_not_return:
                    dict_to_return[key] = value
            return dict_to_return

    def get_team_ids(self):
        return self.teams

    def ensure_safe_scores(self):
        scores_invalid = False
        t1 = 0
        t2 = 1
        if self.winner == 1:
            t1 = 1
            t2 = 0
        if self.best_of < sum(self.scores):
            scores_invalid = True

        if self.scores[t1] != (self.best_of + 1) / 2:
            scores_invalid = True

        if self.scores[t2] >= (self.best_of + 1) / 2:
            scores_invalid = True

        if self.scores[t1] or self.scores[t2] < 0:
            scores_invalid = True

        if scores_invalid:
            if self.best_of == 2:
                if self.winner < 2:
                    self.scores[t1] = 2
                else:
                    self.scores = [1, 1]
            else:
                self.scores[t1] = (self.best_of + 1) / 2
                if (self.scores[t2] >= (self.best_of + 1) / 2) or self.scores[t2] < 0:
                    self.scores[t2] = 0

class Game(BaseModel):
    match: str = ""
    winner: int = 3
    scores: List[int] = [0, 0]

    def to_dict(self):
        return self.__dict__
