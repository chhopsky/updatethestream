# Version History

### v0.4-alpha: Coming Soon
## Features
Added: 
- Mac version now available
- Support for loading tournaments from FACEIT  
- Web-based remote controller  
- Elgato Stream Deck plugin  
- Built-in web server for self-hosting HTML, Javascript and CSS overlays  
- Resizeable window layouts
- New error protection handling
- Logging, for when you need to contact support (files in /logs)
- Package is now signed on Windows (less panicking about untrusted code!)
- Option to clear all matches
- Best-of defaults
- Many new outputs

Removed:
- "Refresh from Challonge" removed until it can be done safely

## Bug Fixes
- Tonnes of bug fixes around edge cases
- The program now appears normally on high-dpi screens

### v0.3-alpha: 27/01/2022
## Features
Added:
- Support for loading and updating from challonge.com round robin & community tournaments.
- Support for team logos and hero images.
- Configurable points per win, loss, and ties.
- Many new additional output files, for faster low-effort setup.
- Warning when importing from Challonge that incomplete Best-of matches are not populated.
- Warning/error messages when you try to do something you shouldn't.

## Bug Fixes
- Fixed a bug where editing a team wouldn't be reflected in the match UI.
- Fixed a bug where editing a team didn't update the win/swap UI.
- Fixed a bug where an error was shown trying to load the default tournament on first run.
- Fixed a bug where BO2s from Challonge could cause the match history to progress incorrectly.
- Fixed a bug where registering a win would reset Red/Blue swap state.
- Fixed a bug where deleting a match that had already occurred could cause a crash if the tournament had progressed to the last match.
- Fixed a bug where deleting a team that still had matches scheduled could cause a crash.
- Fixed a bug where moving a match that was in progress or completed could cause a crash.
- Fixed a bug where attempting to load a draft tournament preview could cause a crash.
- Fixed a bug where progressing a match added from the UI could cause a crash.

### v0.2.1-alpha: 08/01/2022
## Features
Added support for loading and updating from challonge.com playoff bracket tournaments.
Added win-count standings.
Added invisible "TBD" team to support matches scheduled with unfinalized participants.
Added additional output text files.  
Removed requirement for participants to have tricodes.  
Safer loading and saving of files.  
Added error messages for loading, saving and parsing.

## Bug Fixes
Fixed a bug where attempting to edit a match or team without selecting one would cause a crash.
Fixed a bug where adding a match would overwrite previous matches.


### v0.1.1-alpha: 29/12/2021
## Bug fixes:
Fixed a bug where editing a team would swap team name and tricode.  
Fixed a bug where editing a team would not update the schedule on the live window.  
Fixed a bug that caused the chhopsky.tv logo to not appear.  

### v0.1-alpha: 29/12/2021
Initial release
