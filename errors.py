class MatchScheduleDesync(Exception):
    """Raised when match list doesn't match the schedule length."""
    def __init__(self, matches, schedule, message="Adding match created a desync between match storage and schedule."):
        self.matches = matches
        self.schedule = schedule
        super().__init__(self.message)

    def __str__(self):
        return f'Matches: {self.matches}\nSchedule{self.schedule}\n{self.message}'