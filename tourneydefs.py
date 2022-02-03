from pydantic import BaseModel, Field
from typing import Text, List, Dict, Optional
from uuid import uuid4
from errors import MatchScheduleDesync
from copy import deepcopy
import os
import json
import base64
import logging
import errno
import shutil
import processors

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

class Tournament(BaseModel):
    placeholder_team = Team(tricode="TBD", name = "TBD", id="666", logo_small="static/tbd-team-icon.png")
    teams: Dict = {}
    matches: Dict = {}
    schedule: List[str] = []
    current_match: int = 0
    game_history: List[Game] = []
    mapping: Dict = {}
    version : str = "0.3"
    pts_config: Dict = {"win": 1, "tie": 0, "loss": 0}
    default_pts_config: Dict = {"win": 1, "tie": 0, "loss": 0}
    blank_image = "static/empty-graphic.png"
    output_folder = "streamlabels/"


    def get_placeholder_team(self):
        placeholder = self.get_team(self.placeholder_team.id)
        if placeholder:
            return placeholder
        else:
            return self.placeholder_team


    def load_from(self, filename="tournament-config.json"):
        try:
            with open(filename) as f:
                data = json.load(f)

                self.mapping = {}
                self.clear_everything()

                teams = data.get("teams")
                if teams:
                    for team in teams:
                        team = Team(**team)
                        if team != self.placeholder_team:
                            id = self.add_team(team)
                            self.mapping[team.tricode] = id

                matches = data.get("matches")
                if matches:
                    for current_match in data["matches"]:
                        match = Match(**current_match)
                        self.add_match(match)

                self.schedule = data.get("schedule", [])

                game_history = data.get("game_history")
                if game_history is not None:
                    for game in game_history:
                        game = Game(**game)
                        self.game_history.append(game)

                current_match = data.get("current_match")
                if current_match is not None:
                    self.current_match = current_match
                
                pts_config = data.get("pts_config")
                if pts_config:
                    self.pts_config = pts_config

        except:
            return False
        return True

    def load_from_faceit(self, tournament_data):
        self.mapping = {}
        self.clear_everything()

        for team in tournament_data["teams"].values():
            self.add_team(team)

        for match in tournament_data["matches"]:
            new_match = deepcopy(match)
            new_match.finished = False
            new_match.in_progress = False
            new_match.scores = [0,0]
            new_match.winner = 2
            self.add_match(new_match)
        
        for i, match_state in enumerate(tournament_data["matches"]):
            match = deepcopy(match_state)

            if match.finished:
                t1 = 0
                t2 = 1
                if match.winner == 1:
                    t1 = 1
                    t2 = 0
                
                match.ensure_safe_scores()

                game_count = match.scores[t2]
                while game_count > 0:
                    self.game_complete(t2)
                    game_count -= 1

                game_count = match.scores[t1]
                while game_count > 0:
                    self.game_complete(t1)
                    game_count -= 1
        return True

    def update_match_history_from_challonge(self, round_match_list):
        self.game_history = []
        for match in round_match_list:
            if match["state"] == "complete":
                match_id = str(match["id"])
                self.matches[match_id].scores = [0, 0]
                match["scores"] = match["scores_csv"].split("-")
                match["scores"] = list(map(int, match["scores"]))

                # assume winner index is for player 1
                t1 = 0
                t2 = 1

                # if winner was player 2, invert the winner index
                if match["winner_id"] == match["player2_id"]:
                    t1 = 1
                    t2 = 0
                
                # calculate best of
                if match["winner_id"]:
                    self.matches[match_id].best_of = (match["scores"][t1] * 2) - 1  
                else:
                    self.matches[match_id].best_of = sum(match["scores"])

                # if someone marks a match as complete but doesn't enter a score for the winner,
                # assume it was a best of 1 with one game
                if self.matches[match_id].best_of < 1 or sum(match["scores"]) == 0:
                    self.matches[match_id].best_of = 1
                    self.game_complete(t1)
                else:
                    match_count = match["scores"][t2]
                    while match_count > 0:
                        self.game_complete(t2)
                        match_count -= 1

                    match_count = match["scores"][t1]
                    while match_count > 0:
                        self.game_complete(t1)
                        match_count -= 1

        for match in round_match_list:
            if match["state"] == "pending":
                for match_id, our_match in self.matches.items():
                    if our_match.id == match["id"]:
                        if match.get("player1_id"):
                            self.matches[match_id].teams[0] == match["player1_id"]
                        if match.get("player2_id"):
                            self.matches[match_id].teams[1] == match["player2_id"]


    def load_from_challonge(self, tournamentinfo):
        # TODO: make this a debug-level operation
        # with open(f"challonge_load.json", "w") as f_current:
        #     f_current.write(json.dumps(tournamentinfo))
        self.mapping = {}
        self.clear_everything()
        logging.debug("Loading teams")
        match_list = []
        team_list = []

        # fixups on the raw data
        for value in tournamentinfo.get("matches"):
            match = value.get("match")
            match["id"] = str(match["id"])
            if match.get("winner_id"):
                match["winner_id"] = str(match["winner_id"])

            # playerx_id is false if teams arent locked in. set placeholder
            if match.get("player1_id"):
                match["player1_id"] = str(match["player1_id"])
            else:
                match["player1_id"] = self.placeholder_team.id

            if match.get("player2_id"):
                match["player2_id"] = str(match["player2_id"])
            else:
                match["player2_id"] = self.placeholder_team.id

            match_list.append(match)

        # some retrieve the palyer ids, which can be in two differentplaces
        for value in tournamentinfo.get("participants"):
            participant = value.get("participant")
            if len(participant["group_player_ids"]):
                participant["id"] = participant["group_player_ids"][0]
            participant["id"] = str(participant["id"])
            team_list.append(participant)

        try:
            # this should never happen, but if for some reason there isn't a
            # match id in the match, set our own
            for i, match in enumerate(match_list):
                if not match.get("id"):
                    match_list[i]["id"] = str(uuid4())

            #locate teams
            tricode_list = []
            for team in team_list:
                logging.debug(f"found new team with id {team['id']}")
                new_team = Team()
                new_team.name = team["display_name"]
                new_team.id = str(team["id"])
                new_team.tricode = processors.determine_tricode(team["name"], tricode_list)[0:3]
                tricode_list.append(new_team.tricode)
                self.mapping[new_team.tricode] = new_team.id
                self.add_team(new_team)

            # load in completed matches
            for match in match_list:
                if match["state"] == "complete":
                    new_match = Match()
                    new_match.id = str(match["id"])
                    new_match.teams.append(match["player1_id"])
                    new_match.teams.append(match["player2_id"])
                    self.add_match(new_match)

            # add the upcoming matches where teams are locked in
            for match in match_list:
                if match["state"] == "open":
                    new_match = Match()
                    new_match.id = str(match["id"])
                    new_match.teams.append(match["player1_id"])
                    new_match.teams.append(match["player2_id"])
                    self.add_match(new_match)

            # add the upcoming matches where teams are not locked in
            for match in match_list:
                if match["state"] == "pending":
                    new_match = Match()
                    new_match.id = str(match["id"])
                    new_match.teams.append(match["player1_id"])
                    new_match.teams.append(match["player2_id"])
                    self.add_match(new_match)

            # run the match history for the completed matches
            # there is a risk here that matches on the tournament may be
            # completed out of order, that we're not handling
            # currently we only re-order on import. probably need to
            # sort matches in schedule on update, just to be safe
            self.update_match_history_from_challonge(match_list)
        except:
            return False

        self.write_to_stream()
        return True
    

    def save_to(self, filename, savestate=False):
        # do write here
        output_dict = {}
        output_dict["teams"] = []

        for id, team in self.teams.items():
            if team.id != "666":
                output_dict["teams"].append(team.to_dict(savestate))

        output_dict["matches"] = []
        for id, match in self.matches.items():
            output_dict["matches"].append(match.to_dict(savestate))

        output_dict["schedule"] = self.schedule

        if savestate:
            output_dict["current_match"] = self.current_match
            output_dict["game_history"] = []
            for game in self.game_history:
                output_dict["game_history"].append(game.to_dict())

        output_dict["pts_config"] = self.pts_config
        
        if not filename.endswith('.json'):
            filename = filename + '.json'   
        with open(filename, "w") as f:
            json.dump(output_dict, f)
        return


    def write_to_stream(self, swap=False):
        # do text write here
        filename = f"{self.output_folder}start.txt"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        
        if len(self.schedule):
            #try: MATT FIX
                # This section is for things that are written out for every scheduled match
                for index, schedule_item in enumerate(self.schedule):
                    match = self.matches[schedule_item]
                    team1 = self.teams.get(match.teams[0])
                    team2 = self.teams.get(match.teams[1])

                    with open(f"{self.output_folder}match-{index + 1}-teams.txt", "w") as f_teams:
                        f_teams.write(f"{team1.get_name()}\n")
                        f_teams.write(f"{team2.get_name()}\n")
         
                    for i, team in enumerate([team1,team2]):
                        video_extensions = [".mkv",".mov",".mp4", ".avi"]
                        sourcefile = self.blank_image
                        extension = ".png"
                        if team.logo_small and os.path.isfile(team.logo_small):
                            sourcefile = team.logo_small
                            if team.logo_small.rsplit('.',1) in video_extensions:
                                extension = ".mp4"
                        shutil.copy(sourcefile, f"{self.output_folder}match-{index + 1}-team{i + 1}-icon{extension}")
                        
                        sourcefile = self.blank_image
                        extension = ".png"
                        if team.logo_big and os.path.isfile(team.logo_big):
                            sourcefile = team.logo_big
                            if team.logo_big.rsplit('.', 1) in video_extensions:
                                extension = ".mp4"
                        shutil.copy(sourcefile, f"{self.output_folder}match-{index + 1}-team{i + 1}-hero{extension}")

                    with open(f"{self.output_folder}match-{index + 1}-teams-horizontal.txt", "w") as f_teams:
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_teams.write(f"{team1.get_name()} vs {team2.get_name()}\n")

                    with open(f"{self.output_folder}match-{index + 1}-tricodes.txt", "w") as f_teams:
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_teams.write(f"{team1.get_tricode()}\n")
                        f_teams.write(f"{team2.get_tricode()}\n")

                    with open(f"{self.output_folder}match-{index + 1}-tricodes-horizontal.txt", "w") as f_teams:
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_teams.write(f"{team1.get_tricode()} vs {team2.get_tricode()}\n")

                    with open(f"{self.output_folder}match-{index + 1}-scores.txt", "w") as f_scores:
                        f_scores.write(f"{match.scores[0]}\n")
                        f_scores.write(f"{match.scores[1]}\n")

                    with open(f"{self.output_folder}match-{index + 1}-scores-horizontal.txt", "w") as f_scores:
                        f_scores.write(f"{match.scores[0]} - {match.scores[1]}\n")

                # This section is for things that are written out once for the entire schedule
                with open(f"{self.output_folder}schedule-teams.txt", "w") as f_schedule:
                    for index, schedule_item in enumerate(self.schedule):
                        match = self.matches[schedule_item]
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_schedule.write(f"{team1.get_name()} vs {team2.get_name()}\n")
                
                with open(f"{self.output_folder}schedule-tricodes.txt", "w") as f_schedule:
                    for index, schedule_item in enumerate(self.schedule):
                        match = self.matches[schedule_item]
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_schedule.write(f"{team1.get_tricode()} vs {team2.get_tricode()}\n")

                with open(f"{self.output_folder}schedule-scores.txt", "w") as f_schedule:
                    for index, schedule_item in enumerate(self.schedule):
                        match = self.matches[schedule_item]
                        f_schedule.write(f"{match.scores[0]} - {match.scores[1]}\n")
                
                with open(f"{self.output_folder}schedule-teams-combined.txt", "w") as f_schedule:
                    for index, schedule_item in enumerate(self.schedule):
                        match = self.matches[schedule_item]
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_schedule.write(f"{team1.get_name()}\n{team2.get_name()}\n\n")

                with open(f"{self.output_folder}schedule-scores-combined.txt", "w") as f_schedule:
                    for index, schedule_item in enumerate(self.schedule):
                        match = self.matches[schedule_item]
                        f_schedule.write(f"{match.scores[0]}\n{match.scores[1]}\n\n")

                with open(f"{self.output_folder}schedule-tricodes-combined.txt", "w") as f_schedule:
                    for index, schedule_item in enumerate(self.schedule):
                        match = self.matches[schedule_item]
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_schedule.write(f"{team1.get_tricode()}\n{team2.get_tricode()}\n\n")

                with open(f"{self.output_folder}schedule-full-name.txt", "w") as f_schedule:
                    for index, schedule_item in enumerate(self.schedule):
                        match = self.matches[schedule_item]
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_schedule.write(f"{team1.get_name()} vs {team2.get_name()} ")
                        f_schedule.write(f"({match.scores[0]} - {match.scores[1]})\n")

                with open(f"{self.output_folder}schedule-full-tricode.txt", "w") as f_schedule:
                    for index, schedule_item in enumerate(self.schedule):
                        match = self.matches[schedule_item]
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_schedule.write(f"{team1.get_tricode()} vs {team2.get_tricode()} ")
                        f_schedule.write(f"({match.scores[0]} - {match.scores[1]})\n")

                # This section is for things that are written out about the current match    
                current_match = self.current_match if self.current_match < len(self.schedule) else self.current_match - 1
                current_teams = self.get_teams_from_scheduleid(current_match)
                match = self.get_match_from_scheduleid(current_match)
                if current_teams is not None:
                    t0 = 0
                    t1 = 1

                    if swap:
                        t0 = 1
                        t1 = 0
                    with open(f"{self.output_folder}current-match-teams.txt", "w") as f_current:
                        f_current.write(f"{current_teams[0].get_name()} vs {current_teams[1].get_name()}\n")
                    
                    with open(f"{self.output_folder}current-match-tricodes.txt", "w") as f_current:
                        f_current.write(f"{current_teams[0].get_tricode()} vs {current_teams[1].get_tricode()}\n")

                    with open(f"{self.output_folder}current-match-team1-tricode.txt", "w") as f_current:
                        f_current.write(f"{current_teams[t0].get_tricode()}\n")

                    with open(f"{self.output_folder}current-match-team2-tricode.txt", "w") as f_current:
                        f_current.write(f"{current_teams[t1].get_tricode()}\n")
                    
                    with open(f"{self.output_folder}current-match-team1-name.txt", "w") as f_current:
                        f_current.write(f"{current_teams[t0].get_name()}\n")

                    with open(f"{self.output_folder}current-match-team2-name.txt", "w") as f_current:
                        f_current.write(f"{current_teams[t1].get_name()}\n")

                    with open(f"{self.output_folder}current-match-team1-score.txt", "w") as f_current:
                        f_current.write(f"{match.scores[t0]}\n")

                    with open(f"{self.output_folder}current-match-team2-score.txt", "w") as f_current:
                        f_current.write(f"{match.scores[t1]}\n")
                    

                    for i, team in enumerate([current_teams[t0],current_teams[t1]]):
                        video_extensions = [".mkv",".mov",".mp4", ".avi"]
                        sourcefile = self.blank_image
                        extension = ".png"
                        if team.logo_small and os.path.isfile(team.logo_small):
                            sourcefile = team.logo_small
                            if team.logo_small.rsplit('.',1) in video_extensions:
                                extension = ".mp4"    
                        shutil.copy(sourcefile, f"{self.output_folder}current-match-team{i + 1}-icon{extension}")

                        sourcefile = self.blank_image
                        extension = ".png"
                        if team.logo_big and os.path.isfile(team.logo_big):
                            sourcefile = team.logo_big
                            if team.logo_big.rsplit('.', 1) in video_extensions:
                                extension = ".mp4"
                        shutil.copy(sourcefile, f"{self.output_folder}current-match-team{i + 1}-hero{extension}")
                
                # This section is for the standings / match history win/loss
                standings = self.get_standings()
                if standings:
                    with open(f"{self.output_folder}standings-complete.txt", "w") as f_current:
                        for result in standings:
                            team = self.teams[result[0]]
                            f_current.write(f"{team.get_name()}: {result[1]}\n")

                    with open(f"{self.output_folder}standings-teams-names.txt", "w") as f_current:
                        for result in standings:
                            team = self.teams[result[0]]
                            f_current.write(f"{team.get_name()}\n")

                    with open(f"{self.output_folder}standings-teams-tricodes.txt", "w") as f_current:
                        for result in standings:
                            team = self.teams[result[0]]
                            f_current.write(f"{team.get_tricode()}\n")

                    with open(f"{self.output_folder}standings-teams-points.txt", "w") as f_current:
                        for result in standings:
                            team = self.teams[result[0]]
                            f_current.write(f"{result[1]}\n")

                    with open(f"{self.output_folder}standings-teams-leader.txt", "w") as f_current:
                        result = standings[0]
                        team = self.teams[result[0]]
                        f_current.write(f"{team.get_name()}")
            #except: MATT FIX
                # TODO: return an error to the UI and have it display
             #   return False MATT FIX
                
        return
    
    def update_match_scores(self):
        self.current_match = 0
        for match_id in self.matches.keys():
            self.matches[match_id].scores = [0, 0]
            self.matches[match_id].winner = 2
            self.matches[match_id].finished = False
            self.matches[match_id].in_progress = False
        for game in self.game_history:
            scheduleid = self.get_scheduleid_from_match_id(game.match)
            self.process_game(scheduleid, game.winner)


    def process_game(self, scheduleid, winner_index):
        match_id = self.get_match_id_from_scheduleid(scheduleid)
        match = self.matches[match_id]
        cutoff = (match.best_of + 1) / 2
        match.scores[winner_index] += 1
        match.in_progress = True
        if match.scores[0] == cutoff or match.scores[1] == cutoff or sum(match.scores) == match.best_of:
            match.in_progress = False
            match.finished = True
            if match.scores[0] == match.scores[1]:
                match.winner = 3  # Tie
            else:
                match.winner = winner_index
            # TODO UDTS-25: split points and starting points
            # self.teams[match.teams[winner_index]].points += 1
            self.current_match += 1


    def game_complete(self, winner_index):
        if self.current_match < len(self.schedule):
            scheduleid = self.current_match
            self.process_game(scheduleid, winner_index)
            match_id = self.get_match_id_from_scheduleid(scheduleid)
            finished_game = Game(match = match_id, winner=winner_index)
            self.game_history.append(finished_game)


    def undo(self):
        self.game_history.pop()
        self.update_match_scores()

    def get_standings(self):
        standings = []
        standing_data = {}
        for team in self.teams.values():
            if team.id != "666":
                standing_data[team.id] = 0
                standing_data[team.id] += int(team.points)

        for match in self.matches.values():
            if match.winner not in [2, 3]:
                winner = match.teams[match.winner]
                loser = match.teams[0] if winner == match.teams[1] else match.teams[1]
                standing_data[winner] += self.get_points_config("win")
                standing_data[loser] += self.get_points_config("loss")
            elif match.winner == 3:  # Tie
                pts_on_tie = self.get_points_config("tie")
                standing_data[match.teams[0]] += pts_on_tie
                standing_data[match.teams[1]] += pts_on_tie

        for team_id, points in standing_data.items():
            if team.id != "666":
                standings.append((team_id, points))
        actual_standings = sorted(standings, key=lambda y:y[1], reverse=True)
        return actual_standings


    ## TEAM READ/WRITE/EDIT
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

        for i, schedule_item in reversed(list(enumerate(self.schedule))):
            match = self.get_match(schedule_item)
            if id in match.teams:
                self.delete_match(match.id)
        self.teams.pop(id)


    ## MATCH READ/WRITE/EDIT
    def add_match(self, match, schedule=True):
        self.matches[match.id] = match
        if schedule:
            self.schedule.append(match.id)
        if len(self.schedule) != len(self.matches):
            raise MatchScheduleDesync(self.matches, self.schedule)


    def delete_match(self, match_id):
        scheduleid = self.get_scheduleid_from_match_id(match_id)
        del(self.schedule[scheduleid])
        for i, game in reversed(list(enumerate(self.game_history))):
            if game.match == match_id:
                del(self.game_history[i])
        self.matches.pop(match_id)
        if scheduleid <= self.current_match:
            self.current_match -= 1


    def edit_match(self, match_id, match):
        self.matches[match_id].teams = match.teams
        self.matches[match_id].best_of = match.best_of


    def get_team_id_by_tricode(self, tricode):
        for key, team in self.teams.items():
            if team.tricode == tricode:
                return key
        return None

    def get_current_match_data_json(self):
        match_to_use = self.current_match if self.current_match < len(self.schedule) else self.current_match - 1
        teams = self.get_teams_from_scheduleid(match_to_use)
        match = self.get_match_from_scheduleid(match_to_use)
        return { "match": match.to_dict(state=True), "teams": [team.to_dict(state=True) for team in teams] }

    def get_schedule_standings_json(self):
        standings_original = self.get_standings()
        standings = []
        for standing in standings_original:
            standing_dict = {}
            standing_dict["team"] = self.get_team(standing[0]).get_name()
            standing_dict["points"] = standing[1]
            standings.append(standing_dict)
        schedule = self.get_schedule()
        return { "schedule": schedule, "standings": standings }
    
    def get_schedule(self):
        schedule_output = []
        for item in self.schedule:
            match_dict = {}
            teams = self.get_teams_from_match_id(item)
            match = self.get_match(item)
            match_dict["teams"] = f"{teams[0].get_name()} vs {teams[1].get_name()}"
            match_dict["scores"] = f"{match.scores[0]} - {match.scores[1]}"
            match_dict["status"] = "Not Started"
            match_dict["winner"] = ""
            if match.finished:
                match_dict["status"] = "Finished"
                if match.winner < 2:
                    match_dict["winner"] = teams[match.winner].get_name()
                else:
                    match_dict["winner"] = "Tie"
            elif match.in_progress:
                match_dict["status"] = "In Progress"
            schedule_output.append(match_dict)
        return schedule_output

    ## POINTS GETTER/SETTER
    def get_points_config(self, result):
        if result in self.pts_config.keys():
            return self.pts_config.get(result)
        else:
            return self.default_pts_config.get(result)


    def get_points_config_all(self):
        if len(self.pts_config) == 3:
            return self.pts_config
        else:
            return self.default_pts_config


    def edit_points(self, new_pts_config):
        self.pts_config = new_pts_config

    ## HELPER FUNCTIONS

    def get_team(self, team_id):
        if team_id in self.teams.keys():
            return self.teams[team_id]
        else:
            return None

    def get_all_teams(self):
        return self.teams

    def get_teams_from_scheduleid(self, id):
        try:    
            match_id = self.schedule[id]
            team1 = self.teams[self.matches[match_id].teams[0]]
            team2 = self.teams[self.matches[match_id].teams[1]]
            return [team1, team2]
        except IndexError:
            return None


    def get_teams_from_match_id(self, match_id):
        try:    
            team1 = self.teams[self.matches[match_id].teams[0]]
            team2 = self.teams[self.matches[match_id].teams[1]]
            return [team1, team2]
        except IndexError:
            return None


    def get_all_matches(self):
        return self.matches

    
    def get_schedule(self, item = None):
        if not item:
            return self.schedule
        elif int(item) < len(self.schedule):
            return self.schedule[item]


    def get_scheduleid_from_match_id(self, match_id):
        return self.schedule.index(match_id)


    def swap_matches(self, scheduleid1, scheduleid2):
        # flip the match ids in the relevant schedule indexes
        match_1 = self.get_match_from_scheduleid(scheduleid1)
        match_2 = self.get_match_from_scheduleid(scheduleid2)
      
        # we cant swap a completed match with an incomplete match
        if (match_1.finished != match_2.finished) or (match_1.in_progress != match_2.in_progress):
            return False

        temp_value = self.schedule[scheduleid1]
        self.schedule[scheduleid1] = self.schedule[scheduleid2]
        self.schedule[scheduleid2] = temp_value

        # start with the lowest game id and overwrite them from the list we just made
        # we only need to do this if we found games to swap
        if match_1.finished and match_2.finished:
            rearrange = {
            1: [],
            2: []
        }
        # locate the game ids we care about
            new_games = []
            for i, game in enumerate(self.game_history):
                if game.match == match_1.id:
                    rearrange[1].append(i)
                if game.match == match_2.id:
                    rearrange[2].append(i)

                starting_game = min(rearrange[1] + rearrange[2])

                # assume arg1 is first, flip if arg2 is first
                i1 = 1
                i2 = 2
                if scheduleid2 < scheduleid1:
                    i1 = 2
                    i2 = 1

                for game_id in rearrange[i2] + rearrange[i1]:
                    new_games.append(self.game_history[game_id])

                while len(new_games):
                    self.game_history[starting_game] = new_games.pop(0)
                    starting_game += 1

        return True
    

    def get_current_match(self):
        return self.get_match_from_scheduleid(self.current_match)

    def get_match(self, id):
        return self.matches.get(id)

    def get_match_id_from_scheduleid(self, scheduleid):
        match_id = self.schedule[scheduleid]
        return self.matches[match_id].id


    def get_match_from_scheduleid(self, scheduleid):
        match_id = self.schedule[scheduleid]
        return self.matches[match_id]


    def clear_everything(self):
        self.teams = {}
        self.add_team(self.placeholder_team)
        self.matches = {}
        self.schedule = []
        self.game_history = []
        self.current_match = 0
        self.mapping = {}