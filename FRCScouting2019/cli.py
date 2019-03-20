from click_shell import shell
import click
import pyfiglet
import csv
import re
import sys
from pprint import pprint
from FRCScouting2019.team import Team
from FRCScouting2019.team import predict_match_score
import statistics
import tbapy
import FRCScouting2019.constants as Constants

teams = {}
matches = []


@shell(prompt=' > ', intro=pyfiglet.figlet_format("ILITE Scouting"))
def cli():
    pass

@cli.command()
def clear_team_data():
    teams = {}

@cli.command
def clear_schedule():
    matches = {}

@cli.command()
@click.argument('input_path', type=click.File())
def import_csv(input_path):
    """Import a CSV file downloaded from Airtable"""
    next(input_path)  # Skip header row
    reader = csv.reader(input_path)
    for row in reader:
        match_number = int(row[0])
        team_number = int(row[1])
        starting_location = row[2]
        line_crossed = row[3] is 'checked'
        sandstorm_attempt = row[8]
        sandstorm_success = row[9]
        hatches = int(row[4]) if row[4] else 0
        cargo = int(row[5]) if row[5] else 0
        end_game = int(re.search(r'\d+', row[13]).group()) if re.search(r'\d+', row[13]).group() else 0
        if team_number not in teams.keys():
            teams[team_number] = Team(team_number)
        teams[team_number]._add_match_data(match_number, starting_location,
                                           line_crossed, hatches, cargo,
                                           sandstorm_attempt,
                                           sandstorm_success, end_game)


@cli.command()
@click.argument('output_path', type=click.Path(exists=False))
def export_csv(output_path):
    """Export a CSV file with aggregate statistics for each team"""
    columns = list(
        filter(lambda x: not x.startswith('_'), Team.__dict__.keys()))
    with open(output_path, 'w+', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Team Number'] + columns)
        for number, team in teams.items():
            results = list(map(lambda x: Team.__dict__[x](team), columns))
            writer.writerow([number] + results)

@cli.command()
@click.argument('input_path', type=click.File())
def import_match_schedule_csv(input_path):
    next(input_path)
    reader = csv.reader(input_path)
    for row in reader:
        match_number = int(row[0])
        team_numbers = list(map(lambda x: int(x), row[1:7]))
        matches[match_number-1] = team_numbers

@cli.command()
def import_match_schedule_tba():
    """Import the match schedule from The Blue Alliance. Requires an internet connection."""
    tba = tbapy.TBA(Constants.TBA_API_KEY)

    # Get match schedule
    tba_matches = tba.event_matches(Constants.EVENT_KEY, simple=True)
    for match in tba_matches:
        if match.comp_level == 'qm':
            team_numbers = []
            team_numbers = team_numbers + list(map(lambda x: int(x[3:]), match.alliances['red']['team_keys']))
            team_numbers = team_numbers + list(map(lambda x: int(x[3:]), match.alliances['red']['surrogate_team_keys']))
            team_numbers = team_numbers + list(map(lambda x: int(x[3:]), match.alliances['blue']['team_keys']))
            team_numbers = team_numbers + list(map(lambda x: int(x[3:]), match.alliances['blue']['surrogate_team_keys']))
            matches[match.match_number-1] = team_numbers

    # Print match schedule
    view = input('Successfully imported {num_qual_matches} matches. View schedule (Y\\N)? ')
    if (view == 'Y'):
        # TODO: Make this prettier
        for match_number in range(0, num_qual_matches):
            print(match_number+1, 
                matches[match_number][0], 
                matches[match_number][1], 
                matches[match_number][2], 
                matches[match_number][3], 
                matches[match_number][4], 
                matches[match_number][5])

@cli.command()
@click.argument('match_number', type=click.INT)
def get_match_statistics(match_number):
    team_numbers = matches[match_number-1]
    red_teams = team_numbers[0:3]
    blue_teams = team_numbers[3:7]
    # red_score, blue_score = predict_match_score(red_teams, blue_teams)
    print('------RED:---------')
    for team_num in red_teams: 
        print('Team: ' + str(team_num))
        try: 
            team = teams[team_num]
        except KeyError:
            team = Team(0)
            team._add_match_data(0,0,0,0,0,0,0,0)
        running_hatch_avg = statistics.mean(team.hatches_scored[-4:])
        running_cargo_avg = statistics.mean(team.cargo_scored[-4:])
        running_end_game_avg = statistics.mean(team.end_game[-4:])
        print('\tHatches: ' + str(running_hatch_avg))
        print('\tCargo: ' + str(running_cargo_avg))
        print('\tClimb: ' + str(running_end_game_avg))
    print('------BLUE:---------')
    for team_num in blue_teams: 
        print('Team: ' + str(team_num))
        try: 
            team = teams[team_num]
        except KeyError:
            team = Team(0)
            team._add_match_data(0,0,0,0,0,0,0,0)
        running_hatch_avg = statistics.mean(team.hatches_scored[-4:])
        running_cargo_avg = statistics.mean(team.cargo_scored[-4:])
        running_end_game_avg = statistics.mean(team.end_game[-4:])
        print('\tHatches: ' + str(running_hatch_avg))
        print('\tCargo: ' + str(running_cargo_avg))
        print('\tClimb: ' + str(running_end_game_avg))
        
