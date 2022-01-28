# Update The Stream
A tournament scores/schedule/standings management tool for esports tournament broadcasts.

<img src="https://chhopsky.github.io/UDTS-demo-0.3.png">

# How to use:
Download the latest release: https://github.com/chhopsky/updatethestream/releases  

The program uses the teams and matches you configure to write out text files and images containing schedule, scores and standings. In OBS, or whatever broadcast program you use, add files from the "streamlabels" folder as sources, and configure them however you want in your broadcast program.

<img src="https://chhopsky.github.io/udts-in-obs.png">

# Demonstration:
Video demo: https://www.youtube.com/watch?v=o-WJ5P9WSGo

Step by step:
1. Populate the broadcast. Either:  
- add teams to the teams tab, and matches to the matches tab  
- or hit File, open from challonge, put in your tournament code to load from challonge
- or open a previously saved tournament file  
2. When a team wins, hit the button indicating that they won.  
3. Hit Swap Red/Blue if you want to swap red and blue side labels for "current match" text files  
4. "Undo last result" steps backwards through the results you recorded, and moves you back in time through the broadcast.  

<img src="https://chhopsky.github.io/UDTS-screenshot-0.3.png">

Notes:  
"Force refresh stream" will rewrite the files, if you have auto-update disabled, or if you've edited a source.  
"Force UI Update" will redraw and reload the UI.

## Known bugs
- TBD placeholder team edits may not save with tournament.  
- TBD placeholder team may not show up in team list if not loading from Challonge  
- Loading from Challonge, then progressing matches out of order on the web site, then updating in the program, can cause the match history to become corrupted. If this happens, save your file and reload it.

Go nuts, GLHF, let me know how you want it to work, or tell me what broke.

## Files
udts.py: UI and control plane  
tourneydefs.py: core class interactions  
config.cfg: stores basic config information  
tournament-config.json: defines teams, matches  
tests.py: pytest validation of backend
static/: Built-in additional files
streamlabels/: Output folder for stream assets  
tests/: fixtures for unit tests

## Other Links
- [Patch Notes](patchnotes.md)  
- [Roadmap](roadmap.md)
- [Credits](credits.md)  
- [How To Contribute](how-to-contribute.md)  

### Disclaimer
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
