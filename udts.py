from PyQt5 import QtWidgets, uic
from tourneydefs import Tournament, Match, Team
import sys

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('form.ui', self) # Load the .ui file
        self.show() # Show the GUI

def setup():
    window.team1_win_button.clicked.connect(on_team1win_click)
    window.team2_win_button.clicked.connect(on_team2win_click)
    window.add_team_button.clicked.connect(add_team)
    window.refresh_ui_button.clicked.connect(force_refresh_ui)
    window.refresh_stream_button.clicked.connect(force_refresh_stream)
    window.undo_button.clicked.connect(undo)
    window.undo_button.setEnabled(False)
    populate_teams()
    populate_matches()
    refresh_team_win_labels()
    set_button_states()

def undo():
    broadcast.game_history.pop()
    broadcast.update_match_scores()
    broadcast.write_to_stream()
    refresh_team_win_labels()
    set_button_states()

def set_button_states():
    # rules for when to enable or disable buttons
    # undo button is disabled if at the first game
    if len(broadcast.game_history) == 0:
        window.undo_button.setEnabled(False)
    else:
        window.undo_button.setEnabled(True)

    # disable win buttons if tournament is over
    if broadcast.current_match < len(broadcast.matches):
        set_team_win_buttons_enabled(True)
    else:
        set_team_win_buttons_enabled(False)

def force_refresh_stream():
    broadcast.write_to_stream()

def force_refresh_ui():
    populate_teams()
    populate_matches()
    refresh_team_win_labels()
    set_button_states()
    
def on_team1win_click():
    team_won(0)

def on_team2win_click():
    team_won(1)

def team_won(team):
    print(f"team {team} won")
    match_in_progress = broadcast.current_match
    broadcast.game_complete(broadcast.current_match, team)
    broadcast.write_to_stream()
    if match_in_progress != broadcast.current_match:
        set_button_states()
        refresh_team_win_labels()

def set_team_win_buttons_enabled(new_state = True):
    window.team1_win_button.setEnabled(new_state)
    window.team2_win_button.setEnabled(new_state)

def refresh_team_win_labels():
    if broadcast.current_match < len(broadcast.matches):
        window.team1_win_button.setText(broadcast.matches[broadcast.current_match].teams[0])
        window.team2_win_button.setText(broadcast.matches[broadcast.current_match].teams[1])

def add_team():
    new_team = Team()
    new_team.name = window.add_team_name_field.text()
    new_team.tricode = window.add_team_tricode_field.text()
    broadcast.add_edit_team(new_team)
    window.add_team_name_field.setText("")
    window.add_team_tricode_field.setText("")
    populate_teams()

def populate_teams():
    window.team_list_widget.clear()
    for tricode, team in broadcast.teams.items():
        item = QtWidgets.QListWidgetItem(f"{team.tricode} {team.name}")
        window.team_list_widget.addItem(item)

def populate_matches():
    window.match_list_widget.clear()
    for match in broadcast.matches:
        item = QtWidgets.QListWidgetItem(f"{match.teams[0]} vs {match.teams[1]}, BO{match.best_of}")
        window.match_list_widget.addItem(item)

broadcast = Tournament()
broadcast.load_from()
broadcast.write_to_stream()
current_match = 0
app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = Ui() # Create an instance of our class
setup()
app.exec_() # Start the application