#from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
import json
from tourneydefs import Tournament, Match, Team

broadcast = Tournament()
broadcast.load_from()
broadcast.write_to_stream()
current_match = 0
print(broadcast.matches)

def draw_window(tournament_data):
    layout = QVBoxLayout()
    layout.addWidget(QLabel("Someone Update The Stream"))
    layout.addWidget(QPushButton('Team 1 win'))
    layout.addWidget(QPushButton('Team 2 win'))
    window.setLayout(layout)

def on_team1win_click():
    team_won(0)

def on_team2win_click():
    team_won(1)

def team_won(team):
    print(f"team {team} won")
    broadcast.game_complete(broadcast.current_match, team)
    broadcast.write_to_stream()
    if broadcast.current_match > len(broadcast.matches) - 1:
        team1win.setEnabled(False)
        team2win.setEnabled(False)
        label.setText("show's over, go home")
    else:
        team1win.setText(broadcast.matches[broadcast.current_match].teams[0])
        team2win.setText(broadcast.matches[broadcast.current_match].teams[1])

app = QApplication([])
window = QWidget()

team1win = QPushButton(broadcast.matches[broadcast.current_match].teams[0])
team2win = QPushButton(broadcast.matches[broadcast.current_match].teams[1])
team1win.clicked.connect(on_team1win_click)
team2win.clicked.connect(on_team2win_click)
label = QLabel("Someone Update The Stream")

layout = QVBoxLayout()
layout.addWidget(label)
layout.addWidget(team1win)
layout.addWidget(team2win)
window.setLayout(layout)

window.show()
app.exec()