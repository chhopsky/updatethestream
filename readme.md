A basic tournament schedule/standings stream tracker for broadcasting short-form multi-match esports tournaments.

config.cfg: stores basic config information
tournament-config.json: defines the teams and matches
tourneydefs.py: classes etc
udts.py: WIP full featured but probably jank-filled UI
Absolute MVP, no blah blah

Known bugs:
- You can edit parts of the schedule that have already occurred. Bad things happen if you delete teams or matches that are already recorded. I will not be fixing this, don't be stupid about it.
- A crash can occur when attempting to refresh the stream for the first time when tournament config file does not exist.