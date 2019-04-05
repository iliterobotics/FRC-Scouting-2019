from FRCScouting2019.team import predict_match_score
from FRCScouting2019.team import Team
import FRCScouting2019.constants as Constants
from airtable import Airtable
import statistics
import csv
import re

teams = {}
matches = {}


def add_match_data(team_number, match_number, starting_location,
                                           line_crossed, hatches, cargo,
                                           sandstorm_attempt,
                                           sandstorm_success, end_game):
    if team_number not in teams.keys():
        teams[team_number] = Team(team_number)
    teams[team_number]._add_match_data(match_number, starting_location,
                                        line_crossed, hatches, cargo,
                                        sandstorm_attempt,
                                        sandstorm_success, end_game)

def add_match_to_schedule(match_number, team_numbers):
    matches[match_number-1] = team_numbers

def print_match_schedule():
    print('Match\tRed  \t\t\tBlue')
    for match_number in range(0, len(matches)):
        print('{:2}\t{:4}  {:4}  {:4}\t{:4}  {:4}  {:4}'.format(
            match_number+1,
            matches[match_number][0], 
            matches[match_number][1], 
            matches[match_number][2], 
            matches[match_number][3], 
            matches[match_number][4], 
            matches[match_number][5]))

def build_match_statistics_string(match_number):
    team_numbers = matches[match_number-1]
    red_teams = team_numbers[0:3]
    blue_teams = team_numbers[3:7]
    red_score, blue_score = predict_match_score(list(map(lambda x: teams[x], red_teams)), list(map(lambda x: teams[x], blue_teams)))
    red_score, blue_score = predict_match_score(list(map(lambda x: teams[x], red_teams)), list(map(lambda x: teams[x], blue_teams)))
    output = ''
    output += ('------RED: ' + str(red_score) + '---------\n')
    for team_num in red_teams: 
        output += ('Team: ' + str(team_num) + '\n')
        try: 
            team = teams[team_num]
        except KeyError:
            team = Team(0)
            team._add_match_data(0,0,0,0,0,0,0,0)
        running_hatch_avg = statistics.mean(team.hatches_scored[-4:])
        running_cargo_avg = statistics.mean(team.cargo_scored[-4:])
        running_end_game_avg = statistics.mean(team.end_game[-4:])
        output += ('\tHatches: ' + str(running_hatch_avg) + '\n')
        output += ('\tCargo: ' + str(running_cargo_avg) + '\n')
        output += ('\tClimb: ' + str(running_end_game_avg) + '\n')
    output += ('------BLUE: ' + str(blue_score) + '---------\n')
    for team_num in blue_teams: 
        output += ('Team: ' + str(team_num) + '\n')
        try: 
            team = teams[team_num]
        except KeyError:
            team = Team(0)
            team._add_match_data(0,0,0,0,0,0,0,0)
        running_hatch_avg = statistics.mean(team.hatches_scored[-4:])
        running_cargo_avg = statistics.mean(team.cargo_scored[-4:])
        running_end_game_avg = statistics.mean(team.end_game[-4:])
        output += ('\tHatches: ' + str(running_hatch_avg) + '\n')
        output += ('\tCargo: ' + str(running_cargo_avg) + '\n')
        output += ('\tClimb: ' + str(running_end_game_avg) + '\n')
    return output

# TODO: Tournament should just build string, let cli determine what to do with
def export_csv(output_path):
    """Export a CSV file with aggregate statistics for each team"""
    columns = list(
        filter(lambda x: not x.startswith('_'), Team.__dict__.keys()))
    with open(output_path, 'w+', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Team Number'] + columns)
        for number, team in teams.items():
            team._Team__filter_data(6)
            results = list(map(lambda x: Team.__dict__[x](team), columns))
            writer.writerow([number] + results)

def import_airtable():
    """Import scouting data directly from Airtable. Requires an internet connection."""
    # Team number in the match data table are record ids in the team data table. We'll build a dict so=
    # we can decode the id back to a team number
    airtable = Airtable(Constants.AIRTABLE_BASE_KEY, 'Team Data', api_key=Constants.AIRTABLE_API_KEY)
    team_records = airtable.get_all(fields=['Name'])
    id_to_team_number = {}
    for record in team_records: 
        try:
            id_to_team_number[record['id']] = int(record['fields']['Name'])
        except:
            pass
    
    # Get all the data from the match data table and parse into Team objects
    airtable = Airtable(Constants.AIRTABLE_BASE_KEY, 'Match Data', api_key=Constants.AIRTABLE_API_KEY)
    records = airtable.get_all()
    for record in sorted(records, key=lambda x: x['fields']['Match Number']):
        record = record['fields']
        team_id = record['Team Number'][0]
        team_number = id_to_team_number[team_id]
        match_number = record['Match Number']
        starting_location = record['Robot Starting Position']
        try:
            line_crossed = record['Cross Hab Line in Sandstorm']
        except:
            line_crossed = False
        sandstorm_attempt = record['Sandstorm - First game piece']
        sandstorm_success = record['Sandstorm - Placement of first game piece']
        try:
            hatches = record['Number of Hatches']
        except:
            hatches = 0
        try:
            cargo = record['Number of Cargo']
        except:
            cargo = 0
        end_game = int(re.search(r'\d+', record['End Game?']).group()) if re.search(r'\d+', record['End Game?']).group() else 0
        add_match_data(team_number, match_number, starting_location,
                                           line_crossed, hatches, cargo,
                                           sandstorm_attempt,
                                           sandstorm_success, end_game)
