from pydantic import BaseModel, Field
from typing import Text, List, Dict, Optional
from uuid import uuid4
from errors import MatchScheduleDesync
import os
import json
import logging
import errno
import shutil

class Team(BaseModel):
    id: str = ""
    name: str = ""
    tricode: str = ""
    points: int = 0
    logo_big: str = ""
    logo_small: str = ""

    def to_dict(self, state=False):
        if state:
            return self.__dict__
        else:
            dict_to_return = {}
            for key, value in self.__dict__.items():
                if key != "points":
                    dict_to_return[key] = value
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


    def update_match_history_from_challonge(self, round_match_list):
        self.game_history = []
        for match in round_match_list:
            if match["state"] == "complete":
                match_id = str(match["id"])
                scheduleid = self.get_scheduleid_from_match_id(match_id)
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
                self.matches[match_id].best_of = (match["scores"][t1] * 2) - 1
                
                match_count = match["scores"][t2]
                while match_count > 0:
                    self.game_complete(scheduleid, t2)
                    match_count -= 1

                match_count = match["scores"][t1]
                while match_count > 0:
                    self.game_complete(scheduleid, t1)
                    match_count -= 1

        for match in round_match_list:
            if match["state"] == "pending":
                for match_id, our_match in enumerate(self.matches):
                    if our_match.id == match["id"]:
                        if match.get("player1_id"):
                            self.matches[match_id][0] == match["player1_id"]
                        if match.get("player2_id"):
                            self.matches[match_id][1] == match["player1_id"]


    def load_from_challonge(self, tournamentinfo):
        self.mapping = {}
        self.clear_everything()
        logging.debug("loading teams")
        match_list = []
        team_list = []
        for value in tournamentinfo.get("matches"):
            match = value.get("match")
            match["id"] = str(match["id"])
            match["player1_id"] = str(match["player1_id"])
            match["player2_id"] = str(match["player2_id"])
            match_list.append(match)

        for value in tournamentinfo.get("participants"):
            participant = value.get("participant")
            if len(participant["group_player_ids"]):
                participant["id"] = str(participant["group_player_ids"])
            team_list.append(participant)

        try:
            for i, match in enumerate(match_list):
                if not match.get("id"):
                    match_list[i]["id"] = str(uuid4())

            for team in team_list:
                logging.debug(f"found new team with id {team['id']}")
                new_team = Team()
                new_team.name = team["display_name"]
                new_team.id = str(team["id"])
                new_team.tricode = team["name"][0:3].upper()
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

            # create match history for them
            # TODO: update this for match/schedule split
            self.update_match_history_from_challonge(match_list)

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
                    if match.get("player1_id"):
                        new_match.teams.append(match["player1_id"])
                    else:
                        new_match.teams.append(self.teams[self.get_team_id_by_tricode("TBD")].id)
                    if match.get("player2_id"):
                        new_match.teams.append(match["player2_id"])
                    else:
                        new_match.teams.append(self.teams[self.get_team_id_by_tricode("TBD")].id)
                    self.add_match(new_match)
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
        
        if len(self.schedule):
            #try: MATT FIX
                # This section is for things that are written out for every scheduled match
                for index, schedule_item in enumerate(self.schedule):
                    match = self.matches[schedule_item]
                    team1 = self.teams.get(match.teams[0])
                    team2 = self.teams.get(match.teams[1])

                    with open(f"streamlabels\match-{index + 1}-teams.txt", "w") as f_teams:
                        f_teams.write(f"{team1.get_name()}\n")
                        f_teams.write(f"{team2.get_name()}\n")
         
                    for i, team in enumerate([team1,team2]):
                        video_extensions = [".mkv",".mov",".mp4", ".avi"]
                        if team.logo_small and os.path.isfile(team.logo_small):
                            extension = ".png"
                            if team.logo_small.rsplit('.',1) in video_extensions:
                                extension = ".mp4"    
                            shutil.copy(team.logo_small, f"streamlabels\match-{index + 1}-team{i + 1}-icon{extension}")
                        if team.logo_big and os.path.isfile(team.logo_big):
                            extension = ".png"
                            if team.logo_big.rsplit('.',1) in video_extensions:
                                extension = ".mp4"
                            shutil.copy(team.logo_big, f"streamlabels\match-{index + 1}-team{i + 1}-hero{extension}")

                    with open(f"streamlabels\match-{index + 1}-teams-horizontal.txt", "w") as f_teams:
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_teams.write(f"{team1.get_name()} vs {team2.get_name()}\n")

                    with open(f"streamlabels\match-{index + 1}-tricodes.txt", "w") as f_teams:
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_teams.write(f"{team1.get_tricode()}\n")
                        f_teams.write(f"{team2.get_tricode()}\n")

                    with open(f"streamlabels\match-{index + 1}-tricodes-horizontal.txt", "w") as f_teams:
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_teams.write(f"{team1.get_tricode()} vs {team2.get_tricode()}\n")

                    with open(f"streamlabels\match-{index + 1}-scores.txt", "w") as f_scores:
                        f_scores.write(f"{match.scores[0]}\n")
                        f_scores.write(f"{match.scores[1]}\n")

                    with open(f"streamlabels\match-{index + 1}-scores-horizontal.txt", "w") as f_scores:
                        f_scores.write(f"{match.scores[0]} - {match.scores[1]}\n")

                # This section is for things that are written out once for the entire schedule
                with open(f"streamlabels\schedule-teams.txt", "w") as f_schedule:
                    for index, schedule_item in enumerate(self.schedule):
                        match = self.matches[schedule_item]
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_schedule.write(f"{team1.get_name()} vs {team2.get_name()}\n")
                
                with open(f"streamlabels\schedule-tricodes.txt", "w") as f_schedule:
                    for index, schedule_item in enumerate(self.schedule):
                        match = self.matches[schedule_item]
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_schedule.write(f"{team1.get_tricode()} vs {team2.get_tricode()}\n")

                with open(f"streamlabels\schedule-scores.txt", "w") as f_schedule:
                    for index, schedule_item in enumerate(self.schedule):
                        match = self.matches[schedule_item]
                        f_schedule.write(f"{match.scores[0]} - {match.scores[1]}\n")

                with open(f"streamlabels\schedule-full-name.txt", "w") as f_schedule:
                    for index, schedule_item in enumerate(self.schedule):
                        match = self.matches[schedule_item]
                        team1 = self.teams.get(match.teams[0])
                        team2 = self.teams.get(match.teams[1])
                        f_schedule.write(f"{team1.get_name()} vs {team2.get_name()} ")
                        f_schedule.write(f"({match.scores[0]} - {match.scores[1]})\n")

                with open(f"streamlabels\schedule-full-tricode.txt", "w") as f_schedule:
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
                    with open(f"streamlabels\current-match-teams.txt", "w") as f_current:
                        f_current.write(f"{current_teams[0].get_name()} vs {current_teams[1].get_name()}\n")
                    
                    with open(f"streamlabels\current-match-tricodes.txt", "w") as f_current:
                        f_current.write(f"{current_teams[0].get_tricode()} vs {current_teams[1].get_tricode()}\n")

                    with open(f"streamlabels\current-match-team1-tricode.txt", "w") as f_current:
                        f_current.write(f"{current_teams[t0].get_tricode()}\n")

                    with open(f"streamlabels\current-match-team2-tricode.txt", "w") as f_current:
                        f_current.write(f"{current_teams[t1].get_tricode()}\n")
                    
                    with open(f"streamlabels\current-match-team1-name.txt", "w") as f_current:
                        f_current.write(f"{current_teams[t0].get_name()}\n")

                    with open(f"streamlabels\current-match-team2-name.txt", "w") as f_current:
                        f_current.write(f"{current_teams[t1].get_name()}\n")

                    with open(f"streamlabels\current-match-team1-score.txt", "w") as f_current:
                        f_current.write(f"{match.scores[t0]}\n")

                    with open(f"streamlabels\current-match-team2-score.txt", "w") as f_current:
                        f_current.write(f"{match.scores[t1]}\n")
                    

                    for i, team in enumerate([current_teams[t0],current_teams[t1]]):
                        video_extensions = [".mkv",".mov",".mp4", ".avi"]
                        if team.logo_small and os.path.isfile(team.logo_small):
                            extension = ".png"
                            if team.logo_small.rsplit('.',1) in video_extensions:
                                extension = ".mp4"    
                            shutil.copy(team.logo_small, f"streamlabels\current-match-team{i + 1}-icon{extension}")
                        if team.logo_big and os.path.isfile(team.logo_big):
                            extension = ".png"
                            if team.logo_big.rsplit('.', 1) in video_extensions:
                                extension = ".mp4"
                            shutil.copy(team.logo_big, f"streamlabels\current-match-team{i + 1}-hero{extension}")
                        


                
                # This section is for the standings / match history win/loss
                standings = self.get_standings()
                if standings:
                    with open(f"streamlabels\standings-complete.txt", "w") as f_current:
                        for result in standings:
                            team = self.teams[result[0]]
                            f_current.write(f"{team.get_name()}: {result[1]}\n")

                    with open(f"streamlabels\standings-teams-names.txt", "w") as f_current:
                        for result in standings:
                            team = self.teams[result[0]]
                            f_current.write(f"{team.get_name()}\n")

                    with open(f"streamlabels\standings-teams-tricodes.txt", "w") as f_current:
                        for result in standings:
                            team = self.teams[result[0]]
                            f_current.write(f"{team.get_tricode()}\n")

                    with open(f"streamlabels\standings-teams-points.txt", "w") as f_current:
                        for result in standings:
                            team = self.teams[result[0]]
                            f_current.write(f"{result[1]}\n")

                    with open(f"streamlabels\standings-teams-leader.txt", "w") as f_current:
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
        cutoff = match.best_of / 2
        match.scores[winner_index] += 1
        match.in_progress = True
        if match.scores[0] > cutoff or match.scores[1] > cutoff or sum(match.scores) == match.best_of:
            match.in_progress = False
            match.finished = True
            if match.scores[0] == match.scores[1]:
                match.winner = 3  # Tie
            else:
                match.winner = winner_index
            # TODO UDTS-25: split points and starting points
            # self.teams[match.teams[winner_index]].points += 1
            self.current_match += 1


    def game_complete(self, scheduleid, winner_index):
        self.process_game(scheduleid, winner_index)
        match_id = self.get_match_id_from_scheduleid(scheduleid)
        finished_game = Game(match = match_id, winner=winner_index)
        self.game_history.append(finished_game)


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
            match = self.get_match_from_scheduleid(schedule_item)
            if id in match.teams or self.teams[id].tricode in match.teams:
                self.matches.pop(match.id)
                del(self.schedule[i])
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


    def edit_match(self, match_id, match):
        self.matches[match_id].teams = match.teams
        self.matches[match_id].best_of = match.best_of


    def get_team_id_by_tricode(self, tricode):
        for key, team in self.teams.items():
            if team.tricode == tricode:
                return key
        return None

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


    def get_scheduleid_from_match_id(self, match_id):
        return self.schedule.index(match_id)


    def swap_matches(self, scheduleid1, scheduleid2):
        temp_value = self.schedule[scheduleid1]
        self.schedule[scheduleid1] = self.schedule[scheduleid2]
        self.schedule[scheduleid2] = temp_value
    

    def get_current_match(self):
        return self.get_match_from_scheduleid(self.current_match)


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