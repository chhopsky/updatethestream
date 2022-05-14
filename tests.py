import pytest
from os import walk
from tournament import Tournament
from tournament_objects import Match, Team, Game
import filecmp
import json
import pprint
from copy import deepcopy

def test_load(default_broadcast):
    broadcast = Tournament()
    broadcast.load_from(filename="tests/default-tournament.json")
    assert str(broadcast) == str(default_broadcast)

def test_output(default_broadcast):
    default_broadcast.output_folder = "tests/output_tests/"
    default_broadcast.write_to_stream()
    for (dirpath, dirnames, filenames) in walk("tests/test_labels"):
        for filename in filenames:
            assert filecmp.cmp(f"{dirpath}/{filename}", f"{default_broadcast.output_folder}{filename}", shallow=False)

def test_data_functions(default_broadcast):
    num_matches = len(default_broadcast.matches)
    num_matches_to_drop = 0

    teams = list(default_broadcast.teams.keys())
    team_to_delete = teams.pop()

    for match in default_broadcast.matches.values():
        if team_to_delete in match.teams:
            num_matches_to_drop += 1

    default_broadcast.delete_team(team_to_delete)

    assert teams == list(default_broadcast.teams.keys())
    assert len(default_broadcast.matches) == num_matches - num_matches_to_drop

    for match in default_broadcast.matches.values():
        if team_to_delete in match.teams:
            assert False

def test_action_functions(default_broadcast):
    wins = [0,1,0,0,0,1,1]
    win_pattern = [0,0,1]
    team_points = {}

    for team_id, team in default_broadcast.teams.items():
        team_points[team_id] = 0

    for i, result in enumerate(wins):
        default_broadcast.game_complete(result)
        assert len(default_broadcast.game_history) == i + 1

    for i, item in enumerate(default_broadcast.schedule):
        match = default_broadcast.get_match(item)
        assert match.winner == win_pattern[i]
    
    for i, item in enumerate(win_pattern):
        match = default_broadcast.get_match_from_scheduleid(i)
        team_points[match.teams[item]] += default_broadcast.pts_config["win"]
        team_points[match.teams[flip(item)]] += default_broadcast.pts_config["loss"]

    standings = default_broadcast.get_standings()
    for standing in standings:
        assert team_points[standing[0]] == standing[1]

    matches = deepcopy(default_broadcast.matches)
    default_broadcast.update_match_scores()
    assert matches == default_broadcast.matches

    ## should not be able to progress matches any further. should do nothing
    cached_broadcast = deepcopy(default_broadcast)
    default_broadcast.game_complete(0)
    assert default_broadcast == cached_broadcast

def test_load_from_challonge():
    with open("tests/challonge_load.json") as f:
        data = json.load(f)
        broadcast = Tournament()
        broadcast.load_from_challonge(data)
        broadcast2 = Tournament()
        broadcast2.load_from("tests/loaded_from_challonge.json")
        print(broadcast)
        print(broadcast2)
        assert broadcast == broadcast2

def flip(argument):
    if argument == 1:
        return 0
    if argument == 0:
        return 1

@pytest.fixture
def default_broadcast():
    broadcast = Tournament()
    teams = [
        {
            "id": "2abb8a92-3979-4523-84af-2d2e2b4b45b5",
            "name": "Team Solo Mid",
            "tricode": "TSM",
            "logo_big": "",
            "logo_small": "udts-demo-stream/TSMlogo_profile.png"
        },
        {
            "id": "bf3dff60-fd65-4f10-a521-bb18af4c45f7",
            "name": "Counter-Logic Gaming",
            "tricode": "CLG",
            "logo_big": "",
            "logo_small": "udts-demo-stream/clg_logo.png"
        },
        {
            "id": "fd8bda90-dd67-4310-afcc-7cdc2755523d",
            "name": "Pentanet.GG",
            "tricode": "PGG",
            "logo_big": "",
            "logo_small": "udts-demo-stream/PentanetGG_logo.png"
        }
    ]
    
    for team in teams:
        new_team = Team(**team)
        broadcast.teams[new_team.id] = new_team
        broadcast.mapping[new_team.tricode] = new_team.id
    
    matches = [
        {
            "id": "545f718d-5d21-47ce-9091-40d68320e7f5",
            "teams": [
                "2abb8a92-3979-4523-84af-2d2e2b4b45b5",
                "bf3dff60-fd65-4f10-a521-bb18af4c45f7"
            ],
            "best_of": 3
        },
        {
            "id": "4b21713d-1622-4a02-b3fd-42793e59d4ad",
            "teams": [
                "bf3dff60-fd65-4f10-a521-bb18af4c45f7",
                "fd8bda90-dd67-4310-afcc-7cdc2755523d"
            ],
            "best_of": 3
        },
        {
            "id": "45cad53c-bcb1-4d2b-aa63-9b1a92814dbb",
            "teams": [
                "fd8bda90-dd67-4310-afcc-7cdc2755523d",
                "2abb8a92-3979-4523-84af-2d2e2b4b45b5"
            ],
            "best_of": 3
        }
    ]

    for match in matches:
        match = Match(**match)
        broadcast.matches[match.id] = match
    
    broadcast.schedule = [
        "545f718d-5d21-47ce-9091-40d68320e7f5",
        "45cad53c-bcb1-4d2b-aa63-9b1a92814dbb",
        "4b21713d-1622-4a02-b3fd-42793e59d4ad"
    ]
    broadcast.pts_config = {
        "win": 1,
        "tie": 0,
        "loss": 0
    }

    return broadcast
