from json.decoder import JSONDecodeError
from PyQt5.uic.uiparser import DEBUG
from pydantic.errors import JsonError
from tourneydefs import Tournament, Match, Team
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont
from form import ui_string
from bs4 import BeautifulSoup
from urllib import request
import PyQt5.QtGui as pygui
import sys
import io
import json
import logging

class Ui(QtWidgets.QMainWindow):
    def __init__(self, loaded_config):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        f = io.StringIO(ui_string)
        uic.loadUi(f, self) # Load the .ui file
        self.show() # Show the GUI
        self.normalfont = QFont()
        self.boldfont = QFont()
        self.boldfont.setBold(True)
        self.strikefont = QFont()
        self.strikefont.setStrikeOut(True)
        self.config = loaded_config
        self.swapstate = 0
        self.setWindowIcon(pygui.QIcon('static/chhtv.ico'))
        

def setup():
    window.actionNew.triggered.connect(new)
    window.actionOpen.triggered.connect(open_file)
    window.actionOpenFromChallonge.triggered.connect(open_challonge)
    window.actionSave.triggered.connect(save_file)
    window.actionSaveAs.triggered.connect(save_as)
    window.actionSaveAsState.triggered.connect(save_as_state)
    window.actionSaveState.triggered.connect(save_state)
    window.actionExit.triggered.connect(exit_app)
    window.actionHelp.triggered.connect(open_github)
    window.team1_win_button.clicked.connect(on_team1win_click)
    window.team2_win_button.clicked.connect(on_team2win_click)
    window.refresh_ui_button.clicked.connect(force_refresh_ui)
    window.refresh_stream_button.clicked.connect(force_refresh_stream)
    window.add_team_button.clicked.connect(add_team)
    window.edit_team_button.clicked.connect(edit_team)
    window.team_list_widget.itemSelectionChanged.connect(team_selected)
    window.delete_team_button.clicked.connect(delete_team)
    window.delete_team_confirm_checkbox.clicked.connect(confirm_delete_team)
    window.match_list_widget.itemSelectionChanged.connect(match_selected)
    window.add_match_button.clicked.connect(add_match)
    window.edit_match_button.clicked.connect(edit_match)
    window.delete_match_button.clicked.connect(delete_match)
    window.delete_match_confirm_checkbox.clicked.connect(confirm_delete_match)
    window.match_move_up_button.clicked.connect(match_move_up)
    window.match_move_down_button.clicked.connect(match_move_down)
    window.swap_button.clicked.connect(swap_red_blue)
    window.undo_button.clicked.connect(undo)
    window.undo_button.setEnabled(False)
    window.match_move_up_button.setEnabled(False)
    window.match_move_down_button.setEnabled(False)
    window.update_from_challonge.clicked.connect(update_from_challonge)
    populate_teams()
    populate_matches()
    update_schedule()
    refresh_team_win_labels()
    set_button_states()
    window.add_match_team1_dropdown.setCurrentIndex(-1)
    window.add_match_team2_dropdown.setCurrentIndex(-1)
    window.edit_match_team1_dropdown.setCurrentIndex(-1)
    window.edit_match_team2_dropdown.setCurrentIndex(-1)


def open_github():
    url = QUrl('https://github.com/chhopsky/updatethestream')
    if not pygui.QDesktopServices.openUrl(url):
        pygui.QMessageBox.warning(window, 'Open Url', 'Could not open url')


def new():
    broadcast.clear_everything()
    populate_teams()
    populate_matches()
    update_schedule()
    refresh_team_win_labels()
    set_button_states()


def open_file():
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseNativeDialog
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(window,"Select a tournament file", "","Tournament JSON (*.json);;All Files (*)", options=options)
    if filename:
        broadcast.load_from(filename)
        window.config["openfile"] = filename
        window.config["use_challonge"] = False
        window.config["challonge_id"] = False
        save_config(window.config)
        force_refresh_ui()


def poll_challonge(tournament_id):
    page = request.urlopen(f"https://challonge.com/{tournament_id}")
    html = page.read()
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    javascript = f"{scripts[8]}"
    return json.loads(javascript.split(';')[2].split(" = ")[1])


def open_challonge():
    text, ok = QtWidgets.QInputDialog.getText(window, "Name of the Team", "Paste Challonge.com tournament code")
    if text and ok:
        try:
            tournament_info = poll_challonge(text)
            if len(tournament_info["matches_by_round"]["1"]) < 1:
                raise Exception
            else:
                found_tournament = True
        except Exception as e:
            logging.error("Could not load JSON!")
            logging.error(e)
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Load error from Challonge")
            msg.setText("The challonge tournament could not be loaded. Please check your code.")
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            x = msg.exec_()
        if found_tournament:
            broadcast.load_from_challonge(tournament_info)
            window.config["use_challonge"] = True
            window.config["challonge_id"] = text
            force_refresh_ui()

def update_from_challonge():
    tournament_info = poll_challonge(window.config["challonge_id"])
    broadcast.update_match_history_from_challonge(tournament_info)
    force_refresh_ui()

def save_file():
    filename = config.get("openfile")
    if filename:
        broadcast.save_to(filename)
    else:
        broadcast.save_to()


def save_state():
    filename = config.get("openfile")
    if filename:
        broadcast.save_to(filename, savestate=True)
    else:
        broadcast.save_to(savestate=True)


def save_as():
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseNativeDialog
    filename, _ = QtWidgets.QFileDialog.getSaveFileName(window,"Save Tournament As..", "","Tournament JSON (*.json);;All Files (*)", options=options)
    if filename:
        broadcast.save_to(filename)
        window.config["openfile"] = filename
        save_config(window.config)


def save_as_state():
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseNativeDialog
    filename, _ = QtWidgets.QFileDialog.getSaveFileName(window,"Save Tournament As..", "","Tournament JSON (*.json);;All Files (*)", options=options)
    if filename:
        broadcast.save_to(filename, savestate=True)
        window.config["openfile"] = filename
        save_config(window.config)


def exit_app():
    sys.exit()


def undo():
    broadcast.game_history.pop()
    broadcast.update_match_scores()
    broadcast.write_to_stream()
    update_schedule()
    refresh_team_win_labels()
    set_button_states()


def match_move_up():
    match_reorder("up")


def match_move_down():
    match_reorder("down")


def match_reorder(direction):
    match_id = window.match_list_widget.currentRow()
    move_map = {"up": -1, "down": 1}
    temp_match = broadcast.matches[match_id]
    broadcast.matches[match_id] = broadcast.matches[match_id + move_map[direction]]
    broadcast.matches[match_id + move_map[direction]] = temp_match
    populate_matches()
    update_schedule()
    set_button_states()
    refresh_team_win_labels()


def set_button_states():
    # rules for when to enable or disable buttons
    # undo button is disabled if at the first game
    if len(broadcast.game_history):
        window.undo_button.setEnabled(True)
    else:
        window.undo_button.setEnabled(False)

    # disable win buttons if there are no matches
    if len(broadcast.matches):
        set_team_win_buttons_enabled(True)
    else:
        set_team_win_buttons_enabled(False)
        window.team1_win_button.setText("No Matches Configured")
        window.team2_win_button.setText("No Matches Configured")

    # disable win buttons if tournament is over
    if broadcast.current_match < len(broadcast.matches):
        set_team_win_buttons_enabled(True)
    else:
        set_team_win_buttons_enabled(False)


def force_refresh_stream():
    broadcast.write_to_stream()


def force_refresh_ui():
    window.update_from_challonge.setEnabled(config["use_challonge"])
    populate_teams()
    populate_matches()
    update_schedule()
    refresh_team_win_labels()
    set_button_states()

    
def on_team1win_click():
    team_won(0)


def on_team2win_click():
    team_won(1)


def team_won(team):
    logging.debug(f"team {team} won")
    match_in_progress = broadcast.current_match
    broadcast.game_complete(broadcast.current_match, team)
    set_button_states()
    update_schedule()
    if match_in_progress != broadcast.current_match:
        window.swapstate = 0
        refresh_team_win_labels()
    broadcast.write_to_stream()


def set_team_win_buttons_enabled(new_state = True):
    window.team1_win_button.setEnabled(new_state)
    window.team2_win_button.setEnabled(new_state)


def refresh_team_win_labels():
    if broadcast.current_match < len(broadcast.matches):
        team1 = broadcast.teams[broadcast.matches[broadcast.current_match].teams[0]]
        team2 = broadcast.teams[broadcast.matches[broadcast.current_match].teams[1]]
        window.team1_win_button.setText(team1.name)
        window.team2_win_button.setText(team2.name)
        if window.swapstate:
            window.blue_label.setText(f"Blue: {team2.name}")
            window.red_label.setText(f"Red: {team1.name}")
        else:
            window.blue_label.setText(f"Blue: {team1.name}")
            window.red_label.setText(f"Red: {team2.name}")


def swap_red_blue():
    if window.swapstate == 0:
        window.swapstate = 1
        broadcast.write_to_stream(swap = True)
    else:
        window.swapstate = 0
        broadcast.write_to_stream(swap = False)
    refresh_team_win_labels()


def add_team():
    name = window.add_team_name_field.text()
    tricode = window.add_team_tricode_field.text()
    points = window.add_team_points_field.text()
    if name and tricode:
        new_team = Team()
        new_team.name = name
        new_team.tricode = tricode
        try:
            new_team.points = int(points)
        except ValueError:
            new_team.points = 0
        broadcast.add_team(new_team)
        window.add_team_name_field.setText("")
        window.add_team_tricode_field.setText("")
        window.add_team_points_field.setText("")
        populate_teams()


def edit_team():
    if window.team_list_widget.selectedItems():
        selected_item = window.team_list_widget.selectedItems()[0]
        update = Team()
        update.id = selected_item.id
        update.name = window.edit_team_name_field.text()
        update.tricode = window.edit_team_tricode_field.text()
        try:
            update.points = int(window.edit_team_points_field.text())
        except ValueError:
            update.points = 0
        broadcast.edit_team(update)
        window.edit_team_name_field.setText("")
        window.edit_team_tricode_field.setText("")
        window.edit_team_points_field.setText("")
        populate_teams()
        update_schedule()


def team_selected():
    if window.team_list_widget.selectedItems():
        selected_item = window.team_list_widget.selectedItems()[0]
        id = selected_item.id
        window.edit_team_tricode_field.setText(broadcast.teams[id].tricode)
        window.edit_team_name_field.setText(broadcast.teams[id].name)
        window.edit_team_points_field.setText(str(broadcast.teams[id].points))


def confirm_delete_team():
    if window.delete_team_confirm_checkbox.isChecked():
        window.delete_team_button.setEnabled(True)
    else:
        window.delete_team_button.setEnabled(False)


def delete_team():
    if window.team_list_widget.selectedItems():
        team_index = window.team_list_widget.currentRow()
        selected_item = window.team_list_widget.selectedItems()[0]
    if window.delete_team_confirm_checkbox.isChecked():
        window.delete_team_confirm_checkbox.setCheckState(False)
        window.delete_team_button.setEnabled(False)
        window.team_list_widget.takeItem(team_index)
        broadcast.delete_team(selected_item.id)
        populate_teams()
        populate_matches()
        set_button_states()
        refresh_team_win_labels()


def add_match():
    t1 = window.add_match_team1_dropdown.currentIndex()
    t2 = window.add_match_team2_dropdown.currentIndex()
    bo = window.add_match_bestof_dropdown.currentIndex()

    if t1 > -1 and t2 > -1 and bo > -1:
        new_match = Match()
        t1_id = broadcast.get_team_id_by_tricode(window.add_match_team1_dropdown.currentText())
        t2_id = broadcast.get_team_id_by_tricode(window.add_match_team2_dropdown.currentText())
        new_match.teams.append(t1_id)
        new_match.teams.append(t2_id)
        new_match.best_of = int(window.add_match_bestof_dropdown.currentText())
        broadcast.add_match(new_match)
        if len(broadcast.matches) == 1:
            set_button_states()
        populate_matches()
        refresh_team_win_labels()
        


def edit_match():
    selected_item = window.match_list_widget.currentRow()
    if selected_item > -1:
        match_data = Match()
        team1_id = broadcast.get_team_id_by_tricode(window.edit_match_team1_dropdown.currentText())
        team2_id = broadcast.get_team_id_by_tricode(window.edit_match_team2_dropdown.currentText())
        match_data.teams.append(team1_id)
        match_data.teams.append(team2_id)
        match_data.best_of = int(window.edit_match_bestof_dropdown.currentText())
        broadcast.edit_match(selected_item, match_data)
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
        
        if len(broadcast.matches):
            populate_matches()
        else:
            set_button_states()
            
        refresh_team_win_labels()


def match_selected():
    selected_item = window.match_list_widget.currentRow()
    teams = broadcast.get_teams_from_matchid(selected_item)
    window.edit_match_team1_dropdown.setCurrentText(teams[0].tricode)
    window.edit_match_team2_dropdown.setCurrentText(teams[1].tricode)
    window.edit_match_bestof_dropdown.setCurrentText(str(broadcast.matches[selected_item].best_of))
    if selected_item == 0:
        window.match_move_up_button.setEnabled(False)
        window.match_move_down_button.setEnabled(True)
    if selected_item > 0 and selected_item < len(broadcast.matches):
        window.match_move_up_button.setEnabled(True)
        window.match_move_down_button.setEnabled(True)
    if selected_item == len(broadcast.matches) - 1:
        window.match_move_up_button.setEnabled(True)
        window.match_move_down_button.setEnabled(False)
    if selected_item == -1:
        window.match_move_up_button.setEnabled(False)
        window.match_move_down_button.setEnabled(False)


    logging.debug(f"match {selected_item} {broadcast.matches[selected_item].teams[0]}")


def populate_teams():
    window.team_list_widget.clear()
    window.add_match_team1_dropdown.clear()
    window.add_match_team2_dropdown.clear()
    window.edit_match_team1_dropdown.clear()
    window.edit_match_team2_dropdown.clear()
    for tricode, team in broadcast.teams.items():
        item = QtWidgets.QListWidgetItem(f"{team.tricode}: {team.name}")
        item.id = team.id
        window.team_list_widget.addItem(item)
        window.add_match_team1_dropdown.addItem(team.tricode)
        window.add_match_team2_dropdown.addItem(team.tricode)
        window.edit_match_team1_dropdown.addItem(team.tricode)
        window.edit_match_team2_dropdown.addItem(team.tricode)
    reset_dropdowns()


def populate_matches():
    window.match_list_widget.clear()
    window.schedule_list_widget.clear()
    for match in broadcast.matches:
        team1 = broadcast.teams[match.teams[0]]
        team2 = broadcast.teams[match.teams[1]]
        scores = f"{match.scores[0]}-{match.scores[1]}"
        item = QtWidgets.QListWidgetItem(f"{team1.name} vs {team2.name}, BO{match.best_of}")
        item2 = QtWidgets.QListWidgetItem(f"{team1.name} vs {team2.name}, {scores}, BO{match.best_of}")
        item2.setFlags(item2.flags() & ~Qt.ItemIsSelectable)
        window.match_list_widget.addItem(item)
        window.schedule_list_widget.addItem(item2)
    reset_dropdowns()


def update_schedule():
    for i, match in enumerate(broadcast.matches):
        team1 = broadcast.teams[match.teams[0]]
        team2 = broadcast.teams[match.teams[1]]
        scores = f"{match.scores[0]}-{match.scores[1]}"
        current_item = window.schedule_list_widget.item(i)
        current_item.setText(f"{team1.name} vs {team2.name}, {scores}, BO{match.best_of}")
        if i == broadcast.current_match:
            current_item.setFont(window.boldfont)
        elif match.finished:
            current_item.setFont(window.strikefont)
        else:
            current_item.setFont(window.normalfont)
    if broadcast.current_match < len(broadcast.matches):
        window.best_of_count_label.setText(str(broadcast.matches[broadcast.current_match].best_of))
        window.team1_score_label.setText(str(broadcast.matches[broadcast.current_match].scores[0]))
        window.team2_score_label.setText(str(broadcast.matches[broadcast.current_match].scores[1]))
    if broadcast.current_match < len(broadcast.matches) - 1 and len(broadcast.matches):
        teams = broadcast.get_teams_from_matchid(broadcast.current_match + 1)
        window.up_next_match.setText(f"{teams[0].tricode} vs {teams[1].tricode}")
    else:
        window.up_next_match.setText("nothing, go home")


def reset_dropdowns():
    window.add_match_team1_dropdown.setCurrentIndex(-1)
    window.add_match_team2_dropdown.setCurrentIndex(-1)
    window.add_match_bestof_dropdown.setCurrentIndex(-1)
    window.edit_match_team1_dropdown.setCurrentIndex(-1)
    window.edit_match_team2_dropdown.setCurrentIndex(-1)
    window.edit_match_bestof_dropdown.setCurrentIndex(-1)


def save_config(config_to_save):
    with open("config.cfg", "w") as f:
        f.write(json.dumps(config_to_save))

try:
    with open("config.cfg") as f:
        config = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    config = { "openfile": "tournament-config.json",
        "use_challonge": False,
        "challonge_id": False
     }
    save_config(config)

log = logging.Logger
logging.Logger.setLevel(log, level = "DEBUG")
broadcast = Tournament()
broadcast.load_from()
broadcast.write_to_stream()
current_match = 0
app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = Ui(loaded_config = config) # Create an instance of our class
setup()
app.exec_() # Start the application