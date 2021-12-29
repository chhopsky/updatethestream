A basic tournament schedule/standings stream tracker for broadcasting short-form multi-match esports tournaments.

config.cfg: stores basic config information
tournament-config.json: defines teams, matches
tourneydefs.py: core class interactions
udts.py: UI and control plane
Absolute MVP, no blah blah

Known bugs:
- You can edit parts of the schedule that have already occurred. Bad things happen if you delete teams or matches that are already recorded. I will not be fixing this, don't be stupid about it.
- Under unknown conditions, a match ending may not revert the red/blue team swap.
