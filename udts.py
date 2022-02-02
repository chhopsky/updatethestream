from asyncore import write
import base64
from http.client import OK
from PyQt5.uic.uiparser import DEBUG
from tourneydefs import Tournament, Match, Team
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from urllib import request, response
from uuid import uuid4
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from waiting import wait, TimeoutExpired
from os import mkdir
import loaders
import threading
import uvicorn
import udtsconfig
import PyQt5.QtGui as pygui
import sys
import json
import logging
import os.path
import requests



class Ui(QtWidgets.QMainWindow):
    def __init__(self, loaded_config):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('static/form.ui', self) # Load the .ui file
        self.show() # Show the GUI
        self.normalfont = QFont()
        self.boldfont = QFont()
        self.boldfont.setBold(True)
        self.strikefont = QFont()
        self.strikefont.setStrikeOut(True)
        self.italicfont = QFont()
        self.italicfont.setItalic(True)
        self.selected_team = None
        self.selected_match = None
        self.lock_matches = False
        self.lock_teams = False
        self.config = loaded_config
        self.swapstate = False
        self.setWindowIcon(pygui.QIcon('static/chhtv.ico'))


def setup():
    window.actionNew.triggered.connect(new)
    window.actionOpen.triggered.connect(open_file)
    window.actionOpenFromChallonge.triggered.connect(open_challonge)
    window.actionOpenfromFACEIT.triggered.connect(open_faceit)
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
    window.add_team_icon_button.clicked.connect(add_team_icon)
    window.add_team_hero_button.clicked.connect(add_team_hero)
    window.edit_team_button.clicked.connect(edit_team)
    window.edit_team_icon_button.clicked.connect(edit_team_icon)
    window.edit_team_hero_button.clicked.connect(edit_team_hero)
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
    window.undo_button.clicked.connect(undo_button)
    window.undo_button.setEnabled(False)
    window.update_from_challonge.clicked.connect(update_from_challonge)
    window.save_tournament_config_button.clicked.connect(edit_tournament_config)
    window.save_program_config_button.clicked.connect(edit_program_config)
    window.edit_tbd_team_icon_select_button.clicked.connect(add_tbd_icon)
    disable_move_buttons()
    populate_teams()
    populate_matches()
    update_schedule()
    update_standings()
    refresh_team_win_labels()
    set_button_states()
    set_config_ui()
    version_check()
    window.add_match_team1_dropdown.setCurrentIndex(-1)
    window.add_match_team2_dropdown.setCurrentIndex(-1)
    window.edit_match_team1_dropdown.setCurrentIndex(-1)
    window.edit_match_team2_dropdown.setCurrentIndex(-1)
    window.add_team_icon_label.filename = False
    window.add_team_hero_label.filename = False
    window.edit_team_icon_label.filename = False
    window.edit_team_hero_label.filename = False
    window.edit_tbd_team_icon_current_icon.filename = False
    window.team1_final_score_field.setEnabled(False)
    window.team2_final_score_field.setEnabled(False)


def set_config_ui():
    point_config = broadcast.get_points_config_all()
    window.points_on_win_spinbox.setValue(point_config["win"])
    window.points_on_tie_spinbox.setValue(point_config["tie"])
    window.points_on_loss_spinbox.setValue(point_config["loss"])
    placeholder = broadcast.get_placeholder_team()
    if placeholder.logo_small:
        head, tail = os.path.split(placeholder.logo_small)
        window.edit_tbd_team_icon_current_icon.setText(tail)


def open_github():
    url = QUrl('https://github.com/chhopsky/updatethestream')
    if not pygui.QDesktopServices.openUrl(url):
        pygui.QMessageBox.warning(window, 'Open Url', 'Could not open url')


def new():
    broadcast.clear_everything()
    populate_teams()
    populate_matches()
    update_schedule()
    update_standings()
    refresh_team_win_labels()
    set_button_states()
    set_config_ui()


def version_check():
    url = "https://raw.githubusercontent.com/chhopsky/updatethestream/main/config.cfg"
    response = requests.get(url)
    cdict = response.json()

    if response.ok:
        with open("config.cfg") as f:
            config = json.load(f)
            if not config.get("version_checked") and config.get("version") != cdict["version"]:
                show_error("CLIENT_OUT_OF_DATE")
                window.config["version_checked"] = True
                save_config(window.config)


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
        write_to_stream_if_enabled()


def open_faceit():
    text, ok = QtWidgets.QInputDialog.getText(window, "FACEIT Tournament ID", "Paste faceit.com tournament code")
    if text and ok:
        found_tournament = False
        try:
            faceit_data = loaders.poll_faceit(text)
            if not len(faceit_data.get("matches")) > 1 and not len(faceit_data.get["teams"]) > 1:
                raise Exception
            else:
                found_tournament = True
        except Exception as e:
            logger.error("Could not load JSON!")
            logger.error(e)
            show_error("FACEIT_LOAD_FAIL")
        if found_tournament:
            result = broadcast.load_from_faceit(faceit_data)
            window.config["use_faceit"] = True
            window.config["faceit_id"] = text
            force_refresh_ui()
            write_to_stream_if_enabled()
        else:
            show_error("FACEIT_LOAD_FAIL")


def open_challonge():
    text, ok = QtWidgets.QInputDialog.getText(window, "Challonge Tournament ID", "Paste Challonge.com tournament code")
    if text and ok and config.get("challonge_api_key"):
        found_tournament = False
        try:
            tournament_info = loaders.poll_challonge(text, config.get("challonge_api_key"))
            if not len(tournament_info["matches"]) > 1 or not len(tournament_info["participants"]) > 1:
                raise Exception
            else:
                found_tournament = True
        except Exception as e:
            logger.error("Could not load JSON!")
            logger.error(e)
            show_error("CHALLONGE_LOAD_FAIL")
        if found_tournament:
            result = broadcast.load_from_challonge(tournament_info)
            if result:                
                window.config["use_challonge"] = True
                window.config["challonge_id"] = text
                force_refresh_ui()
                write_to_stream_if_enabled()
                show_error("CHALLONGE_WARNING")
            else:
                show_error("CHALLONGE_PARSE_FAIL")


def show_error(error_code = "UNKNOWN", additional_info = None):
    if error_code not in udtsconfig.ERRORS.keys():
        additional_info = f"The code was {error_code}."
        error_code = "BAD_UNKNOWN"

    title = udtsconfig.ERRORS[error_code]["title"]
    message = udtsconfig.ERRORS[error_code]["message"]
    
    messagetext = f"{error_code}: {message}"
    if additional_info:
        messagetext += f"\n\n{additional_info}"

    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(messagetext)
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    logger.error(message)
    x = msg.exec_()


def update_from_challonge():
    tournament_info = loaders.poll_challonge(window.config["challonge_id"])
    broadcast.update_match_history_from_challonge(tournament_info)
    force_refresh_ui()
    write()


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


def edit_tournament_config():
    new_pts_config = {
        "win": int(window.points_on_win_spinbox.text()),
        "tie": int(window.points_on_tie_spinbox.text()),
        "loss": int(window.points_on_loss_spinbox.text())
    }
    broadcast.edit_points(new_pts_config)
    placeholder = broadcast.get_team(broadcast.placeholder_team.id)
    if window.edit_tbd_team_icon_current_icon.filename:
        placeholder.logo_small = window.edit_tbd_team_icon_current_icon.filename
    window.edit_tbd_team_icon_current_icon.filename = False
    broadcast.edit_team(placeholder)
    force_refresh_ui()


def edit_program_config():
    window.config["auto-write-changes-to-stream"] = window.autolive_changes_checkbox.isChecked()
    save_config(window.config)
    force_refresh_ui()


def exit_app():
    sys.exit()


def undo_button():
    broadcast.undo()
    write_to_stream_if_enabled()
    update_schedule()
    update_standings()
    refresh_team_win_labels()
    set_button_states()


def disable_move_buttons():
    window.match_move_up_button.setEnabled(False)
    window.match_move_down_button.setEnabled(False)


def match_move_up():
    match_reorder("up")


def match_move_down():
    match_reorder("down")


def match_reorder(direction):
    scheduleid = window.match_list_widget.currentRow()
    move_map = {"up": -1, "down": 1}
    result = broadcast.swap_matches(scheduleid, scheduleid + move_map[direction])
    if result:
        disable_move_buttons()
        populate_matches()
        update_schedule()
        set_button_states()
        refresh_team_win_labels()
        write_to_stream_if_enabled()
    else:
        show_error("REARRANGE_MIXED_FINISH_STATE")


def set_button_states():
    # rules for when to enable or disable buttons
    # undo button is disabled if at the first game
    if len(broadcast.game_history):
        window.undo_button.setEnabled(True)
        window.swap_button.setEnabled(True)
    else:
        window.undo_button.setEnabled(False)
        window.swap_button.setEnabled(False)

    # disable win buttons if there are no matches
    if len(broadcast.schedule):
        set_team_win_buttons_enabled(True)
    else:
        set_team_win_buttons_enabled(False)
        window.team1_win_button.setText("No Matches Configured")
        window.team2_win_button.setText("No Matches Configured")

    # disable win buttons if tournament is over
    if broadcast.current_match < len(broadcast.schedule):
        set_team_win_buttons_enabled(True)
        window.swap_button.setEnabled(True)
    else:
        set_team_win_buttons_enabled(False)
        window.swap_button.setEnabled(False)


def write_to_stream_if_enabled():
    if window.config.get("auto-write-changes-to-stream", True):
        force_refresh_stream()


def force_refresh_stream():
    x = threading.Thread(target=broadcast.write_to_stream)
    x.start()


def force_refresh_ui():
    window.update_from_challonge.setEnabled(config["use_challonge"])
    populate_teams()
    populate_matches()
    update_schedule()
    update_standings()
    refresh_team_win_labels()
    set_button_states()
    set_config_ui()

def refresh_main_page():
    populate_matches()
    update_schedule()
    update_standings()
    refresh_team_win_labels()
    set_button_states()


def from_api(func):
    def wrapper_from_api(*args, **kwargs):
        thread.request_started(args[0])
        func()
        thread.request_finished(args[0])
    return wrapper_from_api
 

@from_api    
def on_team1win_click():
    team_won(0)

@from_api
def on_team2win_click():
    team_won(1)


def team_won(team):
    logger.debug(f"team {team} won")
    match_in_progress = broadcast.current_match
    broadcast.game_complete(team)
    set_button_states()
    update_schedule()
    update_standings()
    if match_in_progress != broadcast.current_match:
        window.swapstate = False
        refresh_team_win_labels()
    broadcast.write_to_stream(window.swapstate)


def set_team_win_buttons_enabled(new_state = True):
    window.team1_win_button.setEnabled(new_state)
    window.team2_win_button.setEnabled(new_state)


def refresh_team_win_labels():
    if broadcast.current_match < len(broadcast.schedule):
        team1, team2 = broadcast.get_teams_from_scheduleid(broadcast.current_match)
        window.team1_win_button.setText(f"{team1.name} Win")
        window.team2_win_button.setText(f"{team2.name} Win")
        if window.swapstate:
            window.blue_label.setText(f"Blue: {team2.name}")
            window.red_label.setText(f"Red: {team1.name}")
        else:
            window.blue_label.setText(f"Blue: {team1.name}")
            window.red_label.setText(f"Red: {team2.name}")


def swap_red_blue():
    if window.swapstate == False:
        window.swapstate = True
        broadcast.write_to_stream(swap = True)
    else:
        window.swapstate = False
        broadcast.write_to_stream(swap = False)
    refresh_team_win_labels()


def add_team():
    name = window.add_team_name_field.text()
    tricode = window.add_team_tricode_field.text()
    points = window.add_team_points_field.text()
    if points == '':
        points = 0
    if name or tricode:
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
    if window.add_team_icon_label.filename:
        new_team.logo_small = window.add_team_icon_label.filename
    if window.add_team_hero_label.filename:
        new_team.logo_big = window.add_team_hero_label.filename
    window.add_team_icon_label.setText("No Logo.")
    window.add_team_icon_label.filename = False
    window.add_team_hero_label.setText("No Hero Icon.")
    window.add_team_hero_label.filename = False


def add_team_icon():
    set_team_icon(window.add_team_icon_label)


def add_team_hero():
    set_team_icon(window.add_team_hero_label)

def add_tbd_icon():
    set_team_icon(window.edit_tbd_team_icon_current_icon)

def set_team_icon(label):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseNativeDialog
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(window,"Select a team icon", "","Image Files (*.png *.jpg *.gif *.mp4 *.mov *.avi *.mkv);;All Files (*)", options=options)
    if filename:
        label.filename=filename
        head, tail = os.path.split(filename)
        label.setText(tail)


def edit_team():
    if window.team_list_widget.selectedItems():
        update = Team()
        update.id = window.selected_team
        update.name = window.edit_team_name_field.text()
        update.tricode = window.edit_team_tricode_field.text()
        if window.edit_team_icon_label.filename:
            update.logo_small = window.edit_team_icon_label.filename
        if window.edit_team_hero_label.filename: 
            update.logo_big = window.edit_team_hero_label.filename
        try:
            update.points = int(window.edit_team_points_field.text())
        except ValueError:
            update.points = 0
        broadcast.edit_team(update)
        window.edit_team_name_field.setText("")
        window.edit_team_tricode_field.setText("")
        window.edit_team_points_field.setText("")
        window.edit_match_button.setEnabled(False)
        populate_teams()
        populate_matches()
        update_schedule()
        update_standings()
        refresh_team_win_labels()
        write_to_stream_if_enabled()


def edit_team_icon():
    set_team_icon(window.edit_team_icon_label)


def edit_team_hero(label):
    set_team_icon(window.edit_team_hero_label)


def team_selected():
    if window.team_list_widget.selectedItems():
        selected_item = window.team_list_widget.selectedItems()[0]
        id = selected_item.id
        window.selected_team = id
        team_to_edit = broadcast.get_team(id)
        window.edit_team_tricode_field.setText(team_to_edit.tricode)
        window.edit_team_name_field.setText(team_to_edit.name)
        window.edit_team_points_field.setText(str(team_to_edit.points))
        window.edit_team_icon_button.setEnabled(True)
        window.edit_team_hero_button.setEnabled(True)
        window.edit_team_button.setEnabled(True)

        if team_to_edit.logo_small:
            window.edit_team_icon_label.filename = team_to_edit.logo_small
            head, tail = os.path.split(team_to_edit.logo_small)
            window.edit_team_icon_label.setText(tail)
        else:
            window.edit_team_icon_label.setText("No Logo.")
            window.edit_team_icon_label.filename = False
        if team_to_edit.logo_big:
            window.edit_team_hero_label.filename = team_to_edit.logo_big
            head, tail = os.path.split(team_to_edit.logo_big)
            window.edit_team_hero_label.setText(tail)
        else:
            window.edit_team_hero_label.setText("No Hero Icon.")
            window.edit_team_hero_label.filename = False



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
            write_to_stream_if_enabled()


def add_match():
    t1 = window.add_match_team1_dropdown.currentIndex()
    t2 = window.add_match_team2_dropdown.currentIndex()
    bo = window.add_match_bestof_dropdown.currentIndex()

    if t1 > -1 and t2 > -1 and bo > -1:
        new_match = Match()
        new_match.id = str(uuid4())
        widget1 = window.team_list_widget.item(t1)
        widget2 = window.team_list_widget.item(t2)
        new_match.teams.append(widget1.id)
        new_match.teams.append(widget2.id)
        new_match.best_of = int(window.add_match_bestof_dropdown.currentText())
        broadcast.add_match(new_match)
        if len(broadcast.matches) == 1:
            set_button_states()
        populate_matches()
        refresh_team_win_labels()
        write_to_stream_if_enabled()


def edit_match():
    selected_item_index = window.match_list_widget.currentRow()
    match_id = window.selected_match
    if selected_item_index > -1:
        match_data = Match()
        team1_index = window.edit_match_team1_dropdown.currentIndex()
        team2_index = window.edit_match_team2_dropdown.currentIndex()
        widget1 = window.team_list_widget.item(team1_index)
        widget2 = window.team_list_widget.item(team2_index)
        match_data.teams.append(widget1.id)
        match_data.teams.append(widget2.id)
        match_data.best_of = int(window.edit_match_bestof_dropdown.currentText())
        broadcast.edit_match(match_id, match_data)
        window.edit_match_button.setEnabled(False)
        populate_matches()
        update_schedule()
        update_standings()
        write_to_stream_if_enabled()


def confirm_delete_match():
    if window.delete_match_confirm_checkbox.isChecked():
        window.delete_match_button.setEnabled(True)
    else:
        window.delete_match_button.setEnabled(False)


def delete_match():
    selected_item_index = window.match_list_widget.currentRow()
    match_id = window.selected_match
    if selected_item_index > -1 and window.delete_match_confirm_checkbox.isChecked():
        window.delete_match_confirm_checkbox.setCheckState(False)
        window.delete_match_button.setEnabled(False)
        window.match_list_widget.takeItem(selected_item_index)
        broadcast.delete_match(match_id)
        
        if len(broadcast.matches):
            populate_matches()
        else:
            set_button_states()
            
        refresh_team_win_labels()
        update_schedule()
        update_standings()
        write_to_stream_if_enabled()


def match_selected():
    if window.match_list_widget.selectedItems():
        selected_item_index = window.match_list_widget.currentRow()
        selected_item = window.match_list_widget.selectedItems()[0]
        match_id = selected_item.id
        window.selected_match = match_id
        teams = broadcast.get_teams_from_match_id(match_id)
        window.edit_match_team1_dropdown.setCurrentText(teams[0].get_tricode())
        window.edit_match_team2_dropdown.setCurrentText(teams[1].get_tricode())
        window.edit_match_bestof_dropdown.setCurrentText(str(broadcast.matches[match_id].best_of))
        window.edit_match_button.setEnabled(True)
        if selected_item_index == 0:
            window.match_move_up_button.setEnabled(False)
            window.match_move_down_button.setEnabled(True)
        if selected_item_index > 0 and selected_item_index < len(broadcast.matches):
            window.match_move_up_button.setEnabled(True)
            window.match_move_down_button.setEnabled(True)
        if selected_item_index == len(broadcast.matches) - 1:
            window.match_move_up_button.setEnabled(True)
            window.match_move_down_button.setEnabled(False)
        if selected_item_index == -1:
            window.match_move_up_button.setEnabled(False)
            window.match_move_down_button.setEnabled(False)


def populate_teams():
    window.team_list_widget.clear()
    window.add_match_team1_dropdown.clear()
    window.add_match_team2_dropdown.clear()
    window.edit_match_team1_dropdown.clear()
    window.edit_match_team2_dropdown.clear()
    window.team_dropdown_map = []
    add_tbd = False
    for id, team in broadcast.teams.items():
        if team.id != "666":
            add_team_to_ui(team)
        else:
            add_tbd = True
    if add_tbd:
        add_team_to_ui(broadcast.placeholder_team, show_in_list=False)
    reset_dropdowns()


def add_team_to_ui(team, show_in_list=True):
    item = QtWidgets.QListWidgetItem(team.get_display_name())
    item.id = team.id
    if not show_in_list:
        item.setFont(window.italicfont)
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
    window.team_list_widget.addItem(item)
    window.add_match_team1_dropdown.addItem(team.get_tricode())
    window.add_match_team2_dropdown.addItem(team.get_tricode())
    window.edit_match_team1_dropdown.addItem(team.get_tricode())
    window.edit_match_team2_dropdown.addItem(team.get_tricode())


def populate_matches():
    window.match_list_widget.clear()
    window.schedule_list_widget.clear()
    for scheduleitem in broadcast.schedule:
        match = broadcast.get_match(scheduleitem)
        teams = broadcast.get_teams_from_match_id(scheduleitem)
        scores = f"{match.scores[0]}-{match.scores[1]}"
        item = QtWidgets.QListWidgetItem(f"{teams[0].get_name()} vs {teams[1].get_name()}, BO{match.best_of}")
        item.id = match.id
        item.team1id = teams[0].id
        item.team2id = teams[1].id
        item2 = QtWidgets.QListWidgetItem(f"{teams[0].get_name()} vs {teams[1].get_name()}, {scores}, BO{match.best_of}")
        item2.setFlags(item2.flags() & ~Qt.ItemIsSelectable)
        window.match_list_widget.addItem(item)
        window.schedule_list_widget.addItem(item2)
    reset_dropdowns()


def update_schedule():
    for i, scheduleitem in enumerate(broadcast.schedule):
        match = broadcast.matches[scheduleitem]
        team1 = broadcast.teams[match.teams[0]]
        team2 = broadcast.teams[match.teams[1]]
        scores = f"{match.scores[0]}-{match.scores[1]}"
        current_item = window.schedule_list_widget.item(i)
        current_item.setText(f"{team1.get_name()} vs {team2.get_name()}, {scores}, BO{match.best_of}")
        if i == broadcast.current_match:
            current_item.setFont(window.boldfont)
        elif match.finished:
            current_item.setFont(window.strikefont)
        else:
            current_item.setFont(window.normalfont)
    if broadcast.current_match < len(broadcast.schedule):
        match = broadcast.get_match_from_scheduleid(broadcast.current_match)
        window.best_of_count_label.setText(str(match.best_of))
        window.team1_score_label.setText(str(match.scores[0]))
        window.team2_score_label.setText(str(match.scores[1]))
    if broadcast.current_match < len(broadcast.schedule) - 1 and len(broadcast.schedule):
        teams = broadcast.get_teams_from_scheduleid(broadcast.current_match + 1)
        window.up_next_match.setText(f"{teams[0].get_tricode()} vs {teams[1].get_tricode()}")
    else:
        window.up_next_match.setText("nothing, go home")


def update_standings():
    window.standings_list_widget.clear()
    standings = broadcast.get_standings()
    if standings is not None:
        for result in standings:
            team = broadcast.teams[result[0]]
            item = QtWidgets.QListWidgetItem(f"{team.get_name()}: {result[1]}")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            window.standings_list_widget.addItem(item)

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

webservice = FastAPI()

def run_server():
    webservice.mount("/static", StaticFiles(directory="static"), name="static")
    uvicorn.run(webservice, host="0.0.0.0", port=8000)

@webservice.get("/", response_class=HTMLResponse)
def web_home(request: Request):
    return templates.TemplateResponse("web_controller.html", {"request": request, "status": broadcast.get_current_match_data_json()})

@webservice.get("/win/team1")
def web_win_team1(response: Response):
    request_id = uuid4()
    if window.team1_win_button.isEnabled():
        thread.web_team1_win.emit(request_id)
        thread.web_update_ui.emit()
        return {}
    response.status_code = 400
    return response

@webservice.get("/win/team2")
def web_win_team2(response: Response):
    request_id = uuid4()
    if window.team2_win_button.isEnabled():
        thread.web_team2_win.emit(request_id)
        thread.web_update_ui.emit()
        return {}
    response.status_code = 400
    return response


@webservice.get("/sideswap")
def web_sideswap(response: Response):
    request_id = uuid4()
    if window.swap_button.isEnabled():
        thread.web_swap_sides.emit(request_id)
        thread.web_update_ui.emit()
        return {}
    response.status_code = 400
    return response

@webservice.get("/undo")
async def web_undo(response: Response):
    request_id = uuid4()
    if window.undo_button.isEnabled():
        thread.web_undo.emit(request_id)
        thread.web_update_ui.emit()
        return {}
    response.status_code = 400
    return response

@webservice.get("/match/current")
async def get_current_match():
    if thread.requests_incomplete():
        try:
            wait(lambda: thread.requests_incomplete(), timeout_seconds=2, sleep_seconds=0.1, waiting_for="outstanding requests to be processed")
        except TimeoutExpired:
            response_value = broadcast.get_current_match_data_json()
            response_value["swap_state"] = window.swapstate
            return response_value
    response_value = broadcast.get_current_match_data_json()
    response_value["swap_state"] = window.swapstate
    return response_value

@webservice.get("/stream/refresh")
async def force_refresh():
    thread.web_refresh_stream.emit()

@webservice.get("/tournament/status")
async def get_current_match():
    try:
        wait(lambda: thread.requests_incomplete(), timeout_seconds=2, sleep_seconds=0.1, waiting_for="outstanding requests to be processed")
    except TimeoutExpired:
        return broadcast.get_schedule_standings_json()
    return broadcast.get_schedule_standings_json()

@webservice.get("/match/current/team/{team_index}/logo_small", response_class=FileResponse)
async def get_current_match_team1_logo_small(team_index):
    if team_index in ["0", "1"]:
        team_index = int(team_index)
        current_match = broadcast.get_current_match_data_json()
        if os.path.isfile(current_match["teams"][team_index]["logo_small"]):
            return current_match["teams"][team_index]["logo_small"]
    return broadcast.blank_image


class WebServerThread(QThread):
    web_update_ui = pyqtSignal()
    web_undo = pyqtSignal(object)
    web_team1_win = pyqtSignal(object)
    web_team2_win = pyqtSignal(object)
    web_swap_sides = pyqtSignal(object)
    web_refresh_stream = pyqtSignal()
    request_state = {}

    def requests_incomplete(self):
        if len(self.request_state):
            return False
        else:
            return True

    def is_request_finished(self, request_id):
        if self.request_state.get(request_id):
            return True
        return False

    def request_finished(self, request_id):
        self.request_state.pop(request_id)

    def request_started(self, request_id):
        self.request_state[request_id] = True

    def run(self):
        run_server()

if __name__ == "__main__":
    version = "0.3"
    LOGLEVEL = "DEBUG"
    try:
        with open("config.cfg") as f:
            config = json.load(f)
            config["version"] = "0.4"
            # if config.get("version") == version:
            #     TODO: config version mismatch
    except (json.JSONDecodeError, FileNotFoundError):
        config = { "openfile": "default-tournament.json",
            "use_challonge": False,
            "challonge_id": False,
            "challonge_api_key": None,
            "version": version,
            "auto-write-changes-to-stream": True
        }
        save_config(config)

    if not os.path.isdir("./logs"):
        mkdir("./logs")
    logger = logging.getLogger("udts_main")
    logging.basicConfig(filename="./logs/udts.log", filemode='a', level=LOGLEVEL, format='%(name)s - %(levelname)s - %(message)s')

    logger.info("====init====")
    broadcast = Tournament(version = version)
    loadfail = False
    foundfile = False
    if os.path.isfile(config.get("openfile")):
        foundfile = True
        result = broadcast.load_from(config["openfile"])
        if not result:
            loadfail = True
    else:
        save_file()

    challonge_api_key_path = config.get("challonge_api_key_location", "creds/challonge-api-key")

    if os.path.isfile(challonge_api_key_path) and not config.get("challonge_api_key"):
        with open(challonge_api_key_path) as file:
            config["challonge_api_key"] = file.read()
        save_config(config)

    if not config.get("challonge_api_key"):
        config["challonge_api_key"] = base64.b64decode("RDFmNjJaRERhT2NSTUltb25sV0pyM0NBOFB4Y2t3amI3WGNueldVSA==").decode()

    logger.debug(broadcast.__dict__)
    broadcast.write_to_stream()
    current_match = 0
    app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
    window = Ui(loaded_config = config) # Create an instance of our class
    if loadfail:
        show_error("SAVE_FILE_ERROR", config["openfile"])

    setup()
    templates = Jinja2Templates(directory="templates")
    thread = WebServerThread()
    thread.web_update_ui.connect(force_refresh_ui)
    thread.web_undo.connect(undo_button)
    thread.web_team1_win.connect(on_team1win_click)
    thread.web_team2_win.connect(on_team2win_click)
    thread.web_swap_sides.connect(swap_red_blue)
    thread.web_refresh_stream.connect(force_refresh_stream)
    thread.start()
    app.exec_() # Start the application
    
