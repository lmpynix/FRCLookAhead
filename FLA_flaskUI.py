# FLA_flaskUI.py
# A component of FRC LookAhead, though I'm sure it's more than usable elsewhere.
# Copyright (c)2018 Logan Power.  Released under the terms of the BSD 3-clause license (included as LICENSE.md)
# Written with the help, love, support, and occasional sarcasm of FRC Team 2039, Rockford Robotics.

# Import what we need from Flask.
from flask import Flask, render_template, Markup

# Import the TBA data package
from FLA_data import get_data_TBA as TBAdata

# Version and application name constants.
VERSION = "0.1 ALPHA"
APPNAME = "FRC LookAhead (Alpha)"

# Define what flask's 'app' is.
flask_app = Flask(__name__)


# Define a quick and easy homepage.
@flask_app.route('/')
def version_page():
    output = \
        """ 
        {} version {}
        If you're looking for the web interface, you should check out /headsup!
        
        URL Syntax: http://<hostname>/headsup/<event ID>/<team ID>/
        
        The IDs are the ones used by The Blue Alliance.  Typically, team ID is "frc####" where the number is your team
        number, and event ID is usually the year followed by a four-letter competition identifier.
    
        """.format(VERSION, APPNAME)
    return output


# This is the actual page that will be displayed.
@flask_app.route('/headsup/<event_id>/<team_id>/')
def main_page(team_id, event_id):
    """
    Main page renderer for Flask
    :param team_id: The Blue Alliance team ID.  GIVEN IN URL.
    :param event_id: The Blue Alliance event ID.  GIVEN IN URL.
    :return: The rendered page.
    """
    # Initialize this team's data and begin to build what we need to display.
    tracked_team = TBAdata.TeamEntry(team_id, event_id)
    # Update the tracked team's data.
    tracked_team.update_data()
    # Assign a few variables that are displayed in the web UI.
    (tracked_ranking, total_teams, tracked_record) = tracked_team.get_team_status_stats()
    # We need to know the number of our next match.
    tracked_next_match = tracked_team.get_next_match_number()
    # Make the markup for RED and BLUE
    RED_MARKUP = Markup("<B class=\"red\"> RED </B>")
    BLUE_MARKUP = Markup("<B class=\"blue\"> BLUE </B>")
    # Get out next match's alliances and figure out which color our alliance is.
    your_alliance, other_alliance = tracked_team.get_next_match_alliance()
    if your_alliance[0] == "red":
        your_alliance_markup = RED_MARKUP
        other_alliance_markup = BLUE_MARKUP
    else:  # Your alliance is the blue one
        your_alliance_markup = BLUE_MARKUP
        other_alliance_markup = RED_MARKUP
    # Now build the tables of alliance data.
    your_alliance_table = list()
    other_alliance_table = list()
    for friendly_team in your_alliance[1:]:
        your_alliance_table.append(build_table_entry(friendly_team, event_id))
    for opposing_team in other_alliance[1:]:
        other_alliance_table.append(build_table_entry(opposing_team, event_id))
    # Finally, throw it all into the template rendering engine and output it.
    return render_template('mainpage.html',
                           APPNAME=APPNAME,
                           VERSION=VERSION,
                           your_team_number=team_id[3:],
                           your_ranking=tracked_ranking,
                           total_teams=total_teams,
                           next_match_number=tracked_next_match,
                           your_alliance_markup=your_alliance_markup,
                           your_alliance=your_alliance_table,
                           other_alliance_markup=other_alliance_markup,
                           other_alliance=other_alliance_table)


def build_table_entry(team_id, event_id):
    """
    Build the displayed table entry (needs to be a list in the right order) for a specified team.
    :param team_id: Blue Alliance team ID.
    :param event_id: Blue Alliance event ID.
    :return: A list that constitutes the table entry for the given team.
    """
    # Initialize a team object and get the data.
    team = TBAdata.TeamEntry(team_id, event_id)
    team.update_data()
    # Get the necessary status data.
    (ranking, total_teams, record) = team.get_team_status_stats()
    # Get the data from this team's last match and extract it.
    last_match = team.get_next_prev_match("last")
    # Figure out which robot this team was in that match since TBA only gives us "robot1", "robot2", etc.
    their_alliance, opponents = team.get_last_match_alliance()
    last_color = their_alliance[0]
    which_robot = their_alliance[1:].index(team_id) + 1
    # Get that alliance's score from the last match
    last_score = str(last_match["alliances"][last_color]["score"])
    # Find autoRun status
    auto_run = last_match["score_breakdown"][last_color]["autoRobot" + str(which_robot)]
    # Find endgame status
    endgame = last_match["score_breakdown"][last_color]["endgameRobot" + str(which_robot)]
    # See if they won or lost the last match
    if last_match["winning_alliance"] == last_color:
        winloss = 'W'
    else:
        winloss = 'L'

    # Get the team number.  This is a little hacky I know.
    team_number = team_id[3:]  # The 3: slices the 'frc' off of the front.

    # TODO: this should be retrieved from TBA, not just put here.
    team_name = "FIRST Robotics Competition Team " + str(team_number)

    # Great, now we have all the data.  Put it all together.
    return [ranking, team_number, team_name, record, auto_run, last_score, winloss, endgame]
