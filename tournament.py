from errors import MatchScheduleDesync, ResourceNotFound, AllResourcesNotFound, TournamentProviderFail, ScheduleError, MatchNotInSchedule
from pydantic import BaseModel, Field
from typing import Text, List, Dict, Optional
from uuid import uuid4
from copy import deepcopy
from tournament_objects import Match, Team, Game
from pathlib import Path
import sys
import os
import json
import logging
import errno
import shutil
import processors



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
    blank_image = "static/empty-graphic.png"
    output_folder = "streamlabels/"
    default_placeholder_team = Team(tricode="TBD", name = "TBD", id="666", logo_small="static/tbd-team-icon.png")
    default_pts_config: Dict = {"win": 1, "tie": 0, "loss": 0}
    default_best_of = 1
    default_default_best_of = 1
    base_dir = ""

    def setup(self):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # we are running inside a bundle, so all bundled files will be here.
            exec_dir = Path(sys.executable).parent.resolve()
            bundle_dir = Path(sys._MEIPASS)
            in_bundle = True
        else:
            # we are running inside the default Python interpreter, so the bundle
            # dir is the same as the current file's folder.
            bundle_dir = Path(__file__).parent.resolve()
            exec_dir = bundle_dir
            in_bundle = False

        self.base_dir = exec_dir
        
        if sys.platform.startswith("darwin") and in_bundle:
            home_dir = Path.home()
            self.base_dir = Path.joinpath(home_dir, "Documents/udts")

        self.output_folder = str(Path.joinpath(self.base_dir, self.output_folder) ) + "/"
        self.placeholder_team.logo_small = str(Path.joinpath(self.base_dir, self.placeholder_team.logo_small))
        self.default_placeholder_team.logo_small = str(Path.joinpath(self.base_dir, self.default_placeholder_team.logo_small))
        self.blank_image = str(Path.joinpath(self.base_dir, self.blank_image))
    
    def save_to(self, filename, savestate=False):
        # do write here
        output_dict = {}
        output_dict["teams"] = []

        for id, team in self.teams.items():
            if team.id != self.placeholder_team.id:
                output_dict["teams"].append(team.to_dict(savestate))

        output_dict["matches"] = []
        for id, match in self.matches.items():
            output_dict["matches"].append(match.to_dict(savestate))

        output_dict["schedule"] = self.schedule

        output_dict["default_best_of"] = self.default_best_of

        output_dict["placeholder_team"] = self.placeholder_team.to_dict()

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

    ## Tournament loaders

    def load_from(self, filename="tournament-config.json"):
        with open(filename) as f:
            data = json.load(f)

            self.mapping = {}
            self.clear_everything()

            teams = data.get("teams")
            if teams:
                for team in teams:
                    team = Team(**team)
                    if team.id != self.placeholder_team.id:
                        id = self.add_team(team)
                        self.mapping[team.tricode] = id

            placeholder_dict = data.get("placeholder_team")
            if placeholder_dict:
                if placeholder_dict.get("logo_small").startswith("static"):
                    placeholder_dict["logo_small"] = str(Path.joinpath(self.base_dir, placeholder_dict["logo_small"])) 
                self.placeholder_team = Team(**placeholder_dict)
            else:
                self.placeholder_team = self.default_placeholder_team

            matches = data.get("matches")
            if matches:
                for current_match in data["matches"]:
                    match = Match(**current_match)
                    self.add_match(match)

            self.schedule = data.get("schedule", [])

            self.default_best_of = data.get("default_best_of", self.default_default_best_of)

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
                    new_match.best_of = self.default_best_of
                    self.add_match(new_match)

            # add the upcoming matches where teams are not locked in
            for match in match_list:
                if match["state"] == "pending":
                    new_match = Match()
                    new_match.id = str(match["id"])
                    new_match.teams.append(match["player1_id"])
                    new_match.teams.append(match["player2_id"])
                    new_match.best_of = self.default_best_of
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

    ## Program outputs

    def write_to_stream(self, swap=False):
        # do text write here
        video_extensions = [".mkv",".mov",".mp4", ".avi"]
        
        filename = f"{self.output_folder}start.txt"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        
        if len(self.schedule):
            for index, schedule_item in enumerate(self.schedule):
                match = self.get_match(schedule_item)
                teams = match.get_team_ids()
                teamlist = self.get_teams_from_ids(teams)

                with open(f"{self.output_folder}match-{index + 1}-teams.txt", "w") as f_teams:
                    for team in teamlist:
                        f_teams.write(f"{team.get_name()}\n")
        
                for i, team in enumerate(teamlist):
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
                    for i, team in enumerate(teamlist):
                        if i < len(teamlist) - 1:
                            suffix = " vs "
                        else:
                            suffix = "\n"
                        f_teams.write(f"{team.get_name()}{suffix}")

                with open(f"{self.output_folder}match-{index + 1}-tricodes.txt", "w") as f_teams:
                    for team in teamlist:
                        f_teams.write(f"{team.get_tricode()}\n")

                with open(f"{self.output_folder}match-{index + 1}-tricodes-horizontal.txt", "w") as f_teams:
                    for i, team in enumerate(teamlist):
                        if i < len(teamlist) - 1:
                            suffix = " vs "
                        else:
                            suffix = "\n"
                        f_teams.write(f"{team.get_tricode()}{suffix}")

                ## TODO: figure out how to handle scores in 2+participant matches
                with open(f"{self.output_folder}match-{index + 1}-scores.txt", "w") as f_scores:
                    for score in match.scores:
                        f_scores.write(f"{score}\n")

                with open(f"{self.output_folder}match-{index + 1}-scores-horizontal.txt", "w") as f_scores:
                    for i, score in enumerate(match.scores):
                        if i < len(match.scores) - 1:
                            suffix = " - "
                        else:
                            suffix = "\n"
                        f_scores.write(f"{score}{suffix}")

            # This section is for things that are written out once for the entire schedule
            with open(f"{self.output_folder}schedule-teams.txt", "w") as f_schedule:
                for index, schedule_item in enumerate(self.schedule):
                    match = self.get_match(schedule_item)
                    teams = match.get_team_ids()
                    teamlist = self.get_teams_from_ids(teams)
                    for team in teamlist:
                        f_schedule.write(f"{team.get_name()}\n")
            
            with open(f"{self.output_folder}schedule-tricodes.txt", "w") as f_schedule:
                for index, schedule_item in enumerate(self.schedule):
                    match = self.get_match(schedule_item)
                    teams = match.get_team_ids()
                    teamlist = self.get_teams_from_ids(teams)
                    for i, team in enumerate(teamlist):
                        if i < len(teamlist) - 1:
                            suffix = " vs "
                        else:
                            suffix = "\n"
                        f_schedule.write(f"{team.get_tricode()}{suffix}")

            with open(f"{self.output_folder}schedule-scores.txt", "w") as f_schedule:
                for index, schedule_item in enumerate(self.schedule):
                    match = self.get_match(schedule_item)
                    for i, score in enumerate(match.scores):
                        if i < len(match.scores) - 1:
                            suffix = " - "
                        else:
                            suffix = "\n"
                        f_schedule.write(f"{score}{suffix}")
            
            with open(f"{self.output_folder}schedule-teams-combined.txt", "w") as f_schedule:
                for index, schedule_item in enumerate(self.schedule):
                    match = self.get_match(schedule_item)
                    teams = match.get_team_ids()
                    teamlist = self.get_teams_from_ids(teams)
                    for team in teamlist:
                        f_schedule.write(f"{team.get_name()}\n")
                    f_schedule.write("\n")

            with open(f"{self.output_folder}schedule-scores-combined.txt", "w") as f_schedule:
                for index, schedule_item in enumerate(self.schedule):
                    match = self.get_match(schedule_item)
                    for i, score in enumerate(match.scores):
                        f_schedule.write(f"{score}\n")
                    f_schedule.write("\n")

            with open(f"{self.output_folder}schedule-tricodes-combined.txt", "w") as f_schedule:
                for index, schedule_item in enumerate(self.schedule):
                    match = self.get_match(schedule_item)
                    teams = match.get_team_ids()
                    teamlist = self.get_teams_from_ids(teams)
                    for team in teamlist:
                        f_schedule.write(f"{team.get_tricode()}\n")
                    f_schedule.write("\n")
                    

            with open(f"{self.output_folder}schedule-full-name.txt", "w") as f_schedule:
                for index, schedule_item in enumerate(self.schedule):
                    match = self.get_match(schedule_item)
                    teams = match.get_team_ids()
                    teamlist = self.get_teams_from_ids(teams)
                    for i, team in enumerate(teamlist):
                        if i < len(teamlist) - 1:
                            suffix = " vs "
                        else:
                            suffix = " ("
                        f_schedule.write(f"{team.get_name()}{suffix}")
                    for i, score in enumerate(match.scores):
                        if i < len(match.scores) - 1:
                            suffix = " - "
                        else:
                            suffix = ")\n"
                        f_schedule.write(f"{score}{suffix}")

            with open(f"{self.output_folder}schedule-full-tricode.txt", "w") as f_schedule:
                for index, schedule_item in enumerate(self.schedule):
                    match = self.get_match(schedule_item)
                    teams = match.get_team_ids()
                    teamlist = self.get_teams_from_ids(teams)
                    for i, team in enumerate(teamlist):
                        if i < len(teamlist) - 1:
                            suffix = " vs "
                        else:
                            suffix = " ("
                        f_schedule.write(f"{team.get_tricode()}{suffix}")
                    for i, score in enumerate(match.scores):
                        if i < len(match.scores) - 1:
                            suffix = " - "
                        else:
                            suffix = ")\n"
                        f_schedule.write(f"{score}{suffix}")

            # This section is for things that are written out about the current match    
            current_match = self.current_match if self.current_match < len(self.schedule) else self.current_match - 1
            last_match = current_match - 1 if current_match != 0 else 0
                 
            labels = ["current", "last"]
            for i, scheduleid in enumerate([current_match, last_match]):
                match = self.get_match_from_scheduleid(scheduleid)
                current_teams = self.get_teams_from_scheduleid(scheduleid)
                if current_teams:
                    t0 = 0
                    t1 = 1

                    if swap:
                        t0 = 1
                        t1 = 0
                    
                    sides = ["blue", "red"]

                    with open(f"{self.output_folder}{labels[i]}-match-teams.txt", "w") as f_current:
                        for i2, team in enumerate(current_teams):
                            if i2 < len(current_teams) - 1:
                                suffix = " vs "
                            else:
                                suffix = "\n"
                            f_current.write(f"{team.get_name()}{suffix}")
                        f_current.close()
                    
                    with open(f"{self.output_folder}{labels[i]}-match-teams-vertical.txt", "w") as f_current2:
                        for i2, team in enumerate(current_teams):
                            f_current2.write(f"{team.get_name()}\n")
                        f_current2.close()
                    
                    with open(f"{self.output_folder}{labels[i]}-match-tricodes.txt", "w") as f_current:
                        for i2, team in enumerate(current_teams):
                            if i2 < len(current_teams) - 1:
                                suffix = " vs "
                            else:
                                suffix = "\n"
                            f_current.write(f"{team.get_tricode()}{suffix}")
                        f_current.close()

                    with open(f"{self.output_folder}{labels[i]}-match-scores.txt", "w") as f_current:
                        for score in match.scores:
                            f_current.write(f"{score}\n")
                        f_current.close()

                    with open(f"{self.output_folder}{labels[i]}-match-scores-horizontal.txt", "w") as f_current:
                        for i2, score in enumerate(match.scores):
                            if i < len(match.scores) - 1:
                                suffix = " - "
                            else:
                                suffix = ""
                        f_current.write(f"{score}{suffix}")

                    with open(f"{self.output_folder}{labels[i]}-match-blue-tricode.txt", "w") as f_current:
                        f_current.write(f"{current_teams[t0].get_tricode()}\n")
                        f_current.close()

                    with open(f"{self.output_folder}{labels[i]}-match-red-tricode.txt", "w") as f_current:
                        f_current.write(f"{current_teams[t1].get_tricode()}\n")
                        f_current.close()
                    
                    with open(f"{self.output_folder}{labels[i]}-match-blue-name.txt", "w") as f_current:
                        f_current.write(f"{current_teams[t0].get_name()}\n")
                        f_current.close()

                    with open(f"{self.output_folder}{labels[i]}-match-red-name.txt", "w") as f_current:
                        f_current.write(f"{current_teams[t1].get_name()}\n")
                        f_current.close()

                    with open(f"{self.output_folder}{labels[i]}-match-blue-score.txt", "w") as f_current:
                        f_current.write(f"{match.scores[t0]}\n")
                        f_current.close()

                    with open(f"{self.output_folder}{labels[i]}-match-red-score.txt", "w") as f_current:
                        f_current.write(f"{match.scores[t1]}\n")
                        f_current.close()
                    

                    for i2, team in enumerate([current_teams[t0],current_teams[t1]]):
                        sourcefile = self.blank_image
                        extension = ".png"
                        if team.logo_small and os.path.isfile(team.logo_small):
                            sourcefile = team.logo_small
                            if team.logo_small.rsplit('.',1) in video_extensions:
                                extension = ".mp4"    
                        shutil.copy(sourcefile, f"{self.output_folder}{labels[i]}-match-{sides[i2]}-icon{extension}")

                        sourcefile = self.blank_image
                        extension = ".png"
                        if team.logo_big and os.path.isfile(team.logo_big):
                            sourcefile = team.logo_big
                            if team.logo_big.rsplit('.', 1) in video_extensions:
                                extension = ".mp4"
                        shutil.copy(sourcefile, f"{self.output_folder}{labels[i]}-match-{sides[i2]}-hero{extension}")

                    for i2, team in enumerate(teamlist):
                        sourcefile = self.blank_image
                        extension = ".png"
                        if team.logo_small and os.path.isfile(team.logo_small):
                            sourcefile = team.logo_small
                            if team.logo_small.rsplit('.',1) in video_extensions:
                                extension = ".mp4"    
                        shutil.copy(sourcefile, f"{self.output_folder}current-match-team{i2 + 1}-icon{extension}")

                        sourcefile = self.blank_image
                        extension = ".png"
                        if team.logo_big and os.path.isfile(team.logo_big):
                            sourcefile = team.logo_big
                            if team.logo_big.rsplit('.', 1) in video_extensions:
                                extension = ".mp4"
                        shutil.copy(sourcefile, f"{self.output_folder}current-match-team{i2 + 1}-hero{extension}")
            
            # This section is for the standings / match history win/loss
            standings = self.get_standings()
            if standings:
                with open(f"{self.output_folder}standings-complete.txt", "w") as f_current:
                    for result in standings:
                        team = self.get_team(result[0])
                        f_current.write(f"{team.get_name()}: {result[1]}\n")

                with open(f"{self.output_folder}standings-teams-names.txt", "w") as f_current:
                    for result in standings:
                        team = self.get_team(result[0])
                        f_current.write(f"{team.get_name()}\n")

                with open(f"{self.output_folder}standings-teams-tricodes.txt", "w") as f_current:
                    for result in standings:
                        team = self.get_team(result[0])
                        f_current.write(f"{team.get_tricode()}\n")

                with open(f"{self.output_folder}standings-teams-points.txt", "w") as f_current:
                    for result in standings:
                        f_current.write(f"{result[1]}\n")

                with open(f"{self.output_folder}standings-teams-leader.txt", "w") as f_current:
                    result = standings[0]
                    team = self.get_team(result[0])
                    f_current.write(f"{team.get_name()}")


    ## Tournament operation functions
    
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


    ## TEAM READ/WRITE/EDIT

    def get_team(self, team_id):
        if team_id == self.placeholder_team.id:
            return self.placeholder_team
        team = self.teams.get(team_id)
        if team:
            return team
        else:
            raise ResourceNotFound("team", team_id)

    def add_team(self, team_to_add, callback = None):
        if not team_to_add.id:
            new_team_id = str(uuid4())
            team_to_add.id = new_team_id
        self.teams[team_to_add.id] = team_to_add
        return team_to_add.id

    def edit_team(self, update):
        self.teams[update.id] = update

    def delete_team(self, id):
        for i, schedule_item in reversed(list(enumerate(self.schedule))):
            match = self.get_match(schedule_item)
            if id in match.teams:
                self.delete_match(match.id)
        self.teams.pop(id)

    ## MATCH READ/WRITE/EDIT

    def get_match(self, match_id):
        match = self.matches.get(match_id)
        if match:
            return match
        else:
            return ResourceNotFound("match", match_id)

    def add_match(self, match, schedule=True):
        self.matches[match.id] = match
        if schedule:
            self.schedule.append(match.id)
        if len(self.schedule) != len(self.matches):
            raise MatchScheduleDesync(self)

    def delete_match(self, match_id):
        """ Deletes a match, removes it from the match history, and schedule"""
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

    ## Tournament data retrievers

    def get_current_match_data_json(self):
        try:
            match_to_use = self.current_match if self.current_match < len(self.schedule) and self.current_match >= 0 else self.current_match - 1
            teams = self.get_teams_from_scheduleid(match_to_use)
            match = self.get_match_from_scheduleid(match_to_use)
        except ScheduleError as e:
            return { "match": {}, "teams": [] }
        return { "match": match.to_dict(state=True), "teams": [team.to_dict(state=True) for team in teams] }

    def get_schedule_standings_json(self):
        standings_original = self.get_standings()
        standings = []
        for standing in standings_original:
            standing_dict = {}
            standing_dict["team"] = self.get_team(standing[0]).get_name()
            standing_dict["points"] = standing[1]
            standings.append(standing_dict)
        schedule = self.get_schedule_readable()
        return { "schedule": schedule, "standings": standings }
    
    def get_schedule_readable(self):
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

    def get_standings(self):
        standings = []
        standing_data = {}
        for team in self.teams.values():
            if team.id != self.placeholder_team.id:
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
            if team.id != self.placeholder_team.id:
                standings.append((team_id, points))
        actual_standings = sorted(standings, key=lambda y:y[1], reverse=True)
        return actual_standings

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

    def set_default_best_of(self, default_best_of):
        self.default_best_of = default_best_of

    def get_default_best_of(self):
        return self.default_best_of

    ## HELPER FUNCTIONS
    # TBD override included here

    def get_placeholder_team(self):
        placeholder = self.get_team(self.placeholder_team.id)
        if placeholder:
            return placeholder
        else:
            return self.placeholder_team

    def get_all_teams(self, with_placeholder = False):
        placeholder = {}
        if with_placeholder:
            placeholder = { self.placeholder_team.id: self.placeholder_team}
        return {**self.teams, **placeholder}

    def get_teams_from_scheduleid(self, id):
        try:    
            match_id = self.get_match_id_from_scheduleid(id)
            return self.get_teams_from_match_id(match_id)
        except IndexError:
            raise ScheduleError(id)

    def get_teams_from_match_id(self, match_id):
        match = self.get_match(match_id)
        team_ids = match.get_team_ids()
        teams = self.get_teams_from_ids(team_ids)
        if len(team_ids) == len(teams):
            return teams
        else:
            raise AllResourcesNotFound(len(team_ids), len(teams))

    def get_teams_from_ids(self, teamlist):
        output = []
        for team in teamlist:
            output.append(self.get_team(team))
        return output

    def get_all_matches(self):
        return self.matches

    def get_schedule(self):
        return self.schedule

    def get_scheduleid_from_match_id(self, match_id):
        try:
            scheduleid = self.schedule.index(match_id)
            return scheduleid
        except IndexError:
            raise MatchNotInSchedule(match_id)

    def get_match_id_from_scheduleid(self, schedule_id):
        try:
            match_id = self.schedule[schedule_id]
            return match_id
        except IndexError:
            raise ScheduleError(schedule_id)

    def get_current_match(self):
        return self.get_match_from_scheduleid(self.current_match)

    def get_current_match_scheduleid(self):
        return self.current_match

    def get_match_from_scheduleid(self, scheduleid):
        match_id = self.get_match_id_from_scheduleid(scheduleid)
        return self.get_match(match_id)

    def get_team_id_by_tricode(self, tricode):
        for key, team in self.teams.items():
            if team.tricode == tricode:
                return key
        return None

    ## Reset Zone

    def clear_matches_and_game_history(self):
        self.matches = {}
        self.schedule = []
        self.current_match = 0
        self.game_history = []


    def clear_everything(self):
        self.teams = {}
        self.matches = {}
        self.schedule = []
        self.game_history = []
        self.current_match = 0
        self.mapping = {}
