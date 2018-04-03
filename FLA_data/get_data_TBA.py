# get_data_TBA.py
# A component of FRC LookAhead, though I'm sure it's more than usable elsewhere.
# Copyright (c)2018 Logan Power.  Released under the terms of the BSD 3-clause license (included as LICENSE.txt)
# Written with the help, love, support, and occasional sarcasm of FRC Team 2039, Rockford Robotics.

# I'd rather not write a lot of code to do an HTTP GET so I'm using requests.
import requests

# YOU NEED AN AUTH KEY FROM THE BLUE ALLIANCE TO USE THIS APP.  You can get one on your account page.
XTBAAUTHKEY = "FH0wlE9QUe6ham1Y8gbF8N9AHelcrnSrPhngdlDm82nzV9G1oBU8hnDf3KnaE4un"


class TeamEntry(object):
    def __init__(self, tba_team_id, tba_event_id):
        """
        TeamEntry constructor.
        :param tba_team_id: Blue Alliance team ID.  Usually "frc####" where #### is your team number.
        :param tba_event_id: Blue Alliance event ID.  Usually the year followed by a four-letter identifier.
        """
        self.team_id = tba_team_id
        self.event_id = tba_event_id
        self.matches = None
        self.status = None

    def get_team_match_data(self):
        """
        Get all of a specified team's matches from the specified competition from the Blue Alliance.

        :return: List of matches.  Interpreted from JSON.
        """
        url = "https://www.thebluealliance.com/api/v3/team/" + self.team_id + "/event/" + self.event_id + "/matches"
        team_match_req = requests.get(url, {"X-TBA-Auth-Key": XTBAAUTHKEY})
        return team_match_req.json()

    def get_team_status_data(self):
        """
        Get a specified team's Blue Alliance status from the specified competition.

        :return: Team status, interpreted from JSON.
        """
        url = "https://www.thebluealliance.com/api/v3/team/" + self.team_id + "/event/" + self.event_id + "/status"
        team_status_req = requests.get(url, {"X-TBA-Auth-Key": XTBAAUTHKEY})
        return team_status_req.json()

    def get_next_prev_match(self, next_or_last="next"):
        """
        Get either a specified team's next match or last played match from the TBA JSON-derived list.

        :param next_or_last: Either "next" or "last" to denote which match you want.
        :return: The entry of the first un-played match or the last played one.  IF VALUE IS NONE THERE'S NO NEXT MATCH.
        """
        if next_or_last == "next" or next_or_last == "last":
            key_to_find = self.status[next_or_last + "_match_key"]
        else:
            raise ValueError("The value supplied to the function (\"" + next_or_last + "\") is not valid.")
        if key_to_find is None:
            return None
        for match in self.matches:
            if match["key"] == key_to_find:
                return match
        return None

    def update_data(self):
        """
        Query the Blue Alliance and store this team's data locally
            (so we don't have to query them more than once every update)

        :return: None
        """
        self.matches = self.get_team_match_data()
        self.status = self.get_team_status_data()
        return None

    def get_next_match_alliance(self):
        """
        Get info about the alliances for the next match.
        :return: A tuple of two lists [your_alliance, other_alliance] with the form [color, team_id1, team_id2, team_id3]
        """
        # Pre-initialize some lists.
        your_alliance = list()
        other_alliance = list()
        # Get the next match data.
        nextmatch = self.get_next_prev_match("next")
        # Get the two alliances from that match.
        next_red = nextmatch["alliances"]["red"]["team_keys"]
        next_blue = nextmatch["alliances"]["blue"]["team_keys"]
        # Find which one is yours.
        if self.team_id in next_red:
            your_alliance = ["red"] + next_red
            other_alliance = ["blue"] + next_blue
        elif self.team_id in next_blue:
            your_alliance = ["blue"] + next_blue
            other_alliance = ["red"] + next_red
        else:
            raise IndexError("This team is not in either of these alliances!  Something has gone wrong...")

        return your_alliance, other_alliance

    def get_next_match_number(self):
        """
        Get the number of this team's next match.
        :return: Next match string (NOT IDENTIFIER)
        """
        return str(self.get_next_prev_match("next")["match_number"])

    def get_team_status_stats(self):
        """
        Get a few stats from a team's status in an easier manner.
        :return: Tuple of strings: (ranking, total_teams, record_string)
        """
        ranking = self.status["qual"]["ranking"]["rank"]
        total_teams = self.status["qual"]["num_teams"]
        record_won = self.status["qual"]["ranking"]["record"]["wins"]
        record_losses = self.status["qual"]["ranking"]["record"]["losses"]
        record_ties = self.status["qual"]["ranking"]["record"]["ties"]
        record_string = str(record_won) + '-' + str(record_losses) + '-' + str(record_ties)
        return str(ranking), str(total_teams), record_string

    def get_last_match_alliance(self):
        """
        Get info about the alliances for the last match.
        :return: A tuple of two lists [your_alliance, other_alliance] with the form [color, team_id1, team_id2, team_id3]
        """
        # Pre-initialize some lists.
        your_alliance = list()
        other_alliance = list()
        # Get the next match data.
        nextmatch = self.get_next_prev_match("last")
        # Get the two alliances from that match.
        next_red = nextmatch["alliances"]["red"]["team_keys"]
        next_blue = nextmatch["alliances"]["blue"]["team_keys"]
        # Find which one is yours.
        if self.team_id in next_red:
            your_alliance = ["red"] + next_red
            other_alliance = ["blue"] + next_blue
        elif self.team_id in next_blue:
            your_alliance = ["blue"] + next_blue
            other_alliance = ["red"] + next_red
        else:
            raise IndexError("This team is not in either of these alliances!  Something has gone wrong...")

        return your_alliance, other_alliance

    @property
    def get_status(self):
        return self.status

    @property
    def get_matches(self):
        return self.matches
