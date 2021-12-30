# Update The Stream
A basic tournament schedule/standings stream tracker for broadcasting short-form multi-match esports tournaments.

<img src="https://chhopsky.github.io/UDTS-demo.png">

# How to use:
The program uses the teams and matches you configure to write out text files containing schedule, scores and standings. In OBS, or whatever broadcast program you use, add the text files from the "streamlabels" folder as text sources, and configure them however you want in your broadcast graphics.

# Demonstration:
Video demo: https://youtu.be/77kKceSTzgI

Step by step:  
1. Add teams to the teams tab.  
2. Add matches to the matches tab.  
3. (optional) On the main screen, click "Force refresh stream" to populate the broadcast.  
4. When a team wins, hit the button indicating that they won.  
5. Hit Swap Red/Blue if you want to swap red and blue side labels for "current match" text files  
6. "Undo last result" steps backwards through the results you recorded, and moves you back in time through the broadcast.  

Notes:
"Force refresh stream" will rewrite the text files, in case anything doesn't update for some reason.  
"Force UI Update" will redraw and reload the UI in case the editing rules get in a bad state.  

## Known bugs
- You can edit parts of the schedule that have already occurred. Bad things happen if you delete teams or matches that are already recorded. I will not be fixing this, don't be stupid about it.
- Under unknown conditions, a match ending may not revert the red/blue team swap.

## WIP
- Scores and standings are not yet implemented
- Scores per match are also not yet implemented
- The ability to lock in a tournament and thus lock you out of editing teams/matches is also not yet implemented

Go nuts, GLHF, let me know how you want it to work, or tell me what broke.

## Files
config.cfg: stores basic config information  
tournament-config.json: defines teams, matches  
tourneydefs.py: core class interactions  
udts.py: UI and control plane  
Absolute MVP

### Disclaimer
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
