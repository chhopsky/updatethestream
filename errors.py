class MatchScheduleDesync(Exception):
    """Raised when match list doesn't match the schedule length."""
    def __init__(self, broadcast):
        self.matches = broadcast.matches
        self.schedule = broadcast.schedule
        self.error_code = "MATCH_SCHEDULE_DESYNC"
        super().__init__(self.message)

    def __str__(self):
        return "Adding match created a desync between match storage and schedule."
        #return f'Matches: {self.matches}\nSchedule{self.schedule}\n{self.message}'

class TournamentProviderFail(Exception):
    def __init__(self, actiontype, tournament_provider, tournament_id):
        self.tournament_provider = tournament_provider
        self.tournament_id = tournament_id
        self.actiontype = actiontype
        self.descriptions = {
            "access": "Unable to contact the tournament server.",
            "parse": "The data was downloaded but wasn't in a format we were expecting.",
            "load": "The data was downloaded and was in the correct format but did not contain matches or teams."
        }

    def __str__(self):
        return f"Error attempting to {self.actiontype} {self.tournament_id} from {self.tournament_provider}.\n\n{self.descriptions[self.actiontype]}"