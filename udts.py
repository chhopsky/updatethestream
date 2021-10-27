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
    
def on_team1win_click():
    team_won(0)

def on_team2win_click():
    team_won(1)

def team_won(team):
    print(f"team {team} won")
    broadcast.game_complete(broadcast.current_match, team)
    broadcast.write_to_stream()
    if broadcast.current_match > len(broadcast.matches) - 1:
        window.team1_win_button.setEnabled(False)
        window.team2_win_button.setEnabled(False)
    else:
        window.team1_win_button.setText(broadcast.matches[broadcast.current_match].teams[0])
        window.team2_win_button.setText(broadcast.matches[broadcast.current_match].teams[1])


broadcast = Tournament()
broadcast.load_from()
broadcast.write_to_stream()
current_match = 0
app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
window = Ui() # Create an instance of our class
setup()
app.exec_() # Start the application