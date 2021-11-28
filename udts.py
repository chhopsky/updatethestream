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
    window.team_list_widget.itemSelectionChanged.connect(team_selected)
    window.match_list_widget.itemSelectionChanged.connect(match_selected)
    window.add_match_button.clicked.connect(add_match)
    window.edit_match_button.clicked.connect(edit_match)
    window.delete_match_button.clicked.connect(delete_match)
    window.delete_match_confirm_checkbox.clicked.connect(confirm_delete_match)
    window.undo_button.clicked.connect(undo)
    window.undo_button.setEnabled(False)
    populate_teams()
    populate_matches()
    refresh_team_win_labels()
    set_button_states()
    window.add_match_team1_dropdown.setCurrentIndex(-1)
    window.add_match_team2_dropdown.setCurrentIndex(-1)
    window.edit_match_team1_dropdown.setCurrentIndex(-1)
    window.edit_match_team2_dropdown.setCurrentIndex(-1)

def undo():
    broadcast.game_history.pop()
    broadcast.update_match_scores()
    broadcast.write_to_stream()
    refresh_team_win_labels()
    set_button_states()

def set_button_states():
    # rules for when to enable or disable buttons
    # undo button is disabled if at the first game
    if len(broadcast.game_history):
        window.undo_button.setEnabled(True)
    else:
        window.undo_button.setEnabled(False)

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
    set_button_states()
    if match_in_progress != broadcast.current_match:
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
    try:
        new_team.points = int(window.add_team_points_field.text())
    except ValueError:
        new_team.points = 0
    broadcast.add_edit_team(new_team)
    window.add_team_name_field.setText("")
    window.add_team_tricode_field.setText("")
    window.add_team_points_field.setText("")
    populate_teams()

def edit_team():
    new_team = Team()
    new_team.name = window.add_team_name_field.text()
    new_team.tricode = window.add_team_tricode_field.text()
    try:
        new_team.points = int(window.add_team_points_field.text())
    except ValueError:
        new_team.points = 0
    broadcast.add_edit_team(new_team)
    window.add_team_name_field.setText("")
    window.add_team_tricode_field.setText("")
    window.add_team_points_field.setText("")
    populate_teams()

def team_selected():
    if window.team_list_widget.selectedItems():
        selected_item = window.team_list_widget.selectedItems()[0]
        label = selected_item.text()
        tricode = label.split(": ")
        window.edit_team_tricode_field.setText(broadcast.teams[tricode[0]].tricode)
        window.edit_team_name_field.setText(broadcast.teams[tricode[0]].name)
        window.edit_team_points_field.setText(str(broadcast.teams[tricode[0]].points))

def add_match():
    t1 = window.add_match_team1_dropdown.currentIndex()
    t2 = window.add_match_team2_dropdown.currentIndex()
    bo = window.add_match_bestof_dropdown.currentIndex()

    if t1 > -1 and t2 > -1 and bo > -1:
        new_match = Match()
        new_match.teams.append(window.add_match_team1_dropdown.currentText())
        new_match.teams.append(window.add_match_team2_dropdown.currentText())
        new_match.best_of = int(window.add_match_bestof_dropdown.currentText())
        broadcast.add_match(new_match)
        populate_matches()

def edit_match():
    selected_item = window.match_list_widget.currentRow()
    if selected_item > -1:
        broadcast.matches[selected_item].teams[0] = window.edit_match_team1_dropdown.currentText()
        broadcast.matches[selected_item].teams[1] = window.edit_match_team2_dropdown.currentText()
        broadcast.matches[selected_item].best_of = int(window.edit_match_bestof_dropdown.currentText())
        populate_matches()

def confirm_delete_match():
    if window.delete_match_confirm_checkbox.isChecked():
        window.delete_match_button.setEnabled(True)
    else:
        window.delete_match_button.setEnabled(False)

def delete_match():
    match_id = window.match_list_widget.currentRow()
    if match_id > -1 and window.delete_match_confirm_checkbox.isChecked():
        window.delete_match_confirm_checkbox.setCheckState(False)
        window.delete_match_button.setEnabled(False)
        window.match_list_widget.takeItem(match_id)
        broadcast.delete_match(match_id)
        populate_matches()

def match_selected():
    selected_item = window.match_list_widget.currentRow()
    window.edit_match_team1_dropdown.setCurrentText(broadcast.matches[selected_item].teams[0])
    window.edit_match_team2_dropdown.setCurrentText(broadcast.matches[selected_item].teams[1])
    window.edit_match_bestof_dropdown.setCurrentText(str(broadcast.matches[selected_item].best_of))
    print(f"match {selected_item} {broadcast.matches[selected_item].teams[0]}")
    
def populate_teams():
    window.team_list_widget.clear()
    window.add_match_team1_dropdown.clear()
    window.add_match_team2_dropdown.clear()
    window.edit_match_team1_dropdown.clear()
    window.edit_match_team2_dropdown.clear()
    for tricode, team in broadcast.teams.items():
        item = QtWidgets.QListWidgetItem(f"{team.tricode}: {team.name}")
        window.team_list_widget.addItem(item)
        window.add_match_team1_dropdown.addItem(team.tricode)
        window.add_match_team2_dropdown.addItem(team.tricode)
        window.edit_match_team1_dropdown.addItem(team.tricode)
        window.edit_match_team2_dropdown.addItem(team.tricode)

def populate_matches():
    window.match_list_widget.clear()
    for match in broadcast.matches:
        item = QtWidgets.QListWidgetItem(f"{match.teams[0]} vs {match.teams[1]}, BO{match.best_of}")
        window.match_list_widget.addItem(item)
    window.add_match_team1_dropdown.setCurrentIndex(-1)
    window.add_match_team2_dropdown.setCurrentIndex(-1)
    window.add_match_bestof_dropdown.setCurrentIndex(-1)
    window.edit_match_team1_dropdown.setCurrentIndex(-1)
    window.edit_match_team2_dropdown.setCurrentIndex(-1)
    window.edit_match_bestof_dropdown.setCurrentIndex(-1)

broadcast = Tournament()
broadcast.load_from()
broadcast.write_to_stream()
current_match = 0
app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = Ui() # Create an instance of our class
setup()
app.exec_() # Start the application