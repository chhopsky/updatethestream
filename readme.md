# Update The Stream
A tournament scores/schedule/standings management tool for esports tournament broadcasts.

<img src="https://chhopsky.github.io/UDTS-demo.png">

# How to use:
Download the latest release: https://github.com/chhopsky/updatethestream/releases  

The program uses the teams and matches you configure to write out text files and images containing schedule, scores and standings. In OBS, or whatever broadcast program you use, add files from the "streamlabels" folder as sources, and configure them however you want in your broadcast graphics.

# Demonstration:
Video demo: https://youtu.be/77kKceSTzgI

Step by step:  
1. Add teams to the teams tab.  
2. Add matches to the matches tab.  
3. (optional) On the main screen, click "Force refresh stream" to populate the broadcast.  
4. When a team wins, hit the button indicating that they won.  
5. Hit Swap Red/Blue if you want to swap red and blue side labels for "current match" text files  
6. "Undo last result" steps backwards through the results you recorded, and moves you back in time through the broadcast.  

<img src="https://chhopsky.github.io/UDTS-screenshot.png">

Notes:
"Force refresh stream" will rewrite the files, if you have auto-update disabled, or if you've edited a source.  
"Force UI Update" will redraw and reload the UI in case the editing rules get in a bad state.  

## Known bugs
- None, please report some.

Go nuts, GLHF, let me know how you want it to work, or tell me what broke.

## Files
config.cfg: stores basic config information  
tournament-config.json: defines teams, matches  
tourneydefs.py: core class interactions  
udts.py: UI and control plane  
static/: Built-in additional files

### Disclaimer
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
