
# Built-ins
import csv
import re
import sys

import time
from pprint import pprint
from multiprocessing import Process

# 3rd party packages
import tbapy
import click
import pyfiglet
from click_shell import shell

# 1st party packages
import FRCScouting2019.constants as Constants
import FRCScouting2019.tournament as Tournament
from FRCScouting2019.team import Team

from FRCScouting2019.slackbot import start_slack_bot


@shell(prompt=' > ', intro=pyfiglet.figlet_format("ILITE Scouting"))
def cli():
    pass

@cli.command()
def clear_team_data():
    teams = {}

@cli.command()
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
        Tournament.add_match_data(team_number, match_number, starting_location,
                                           line_crossed, hatches, cargo,
                                           sandstorm_attempt,
                                           sandstorm_success, end_game)

@cli.command()
def import_airtable():
    """Import scouting data directly from Airtable. Requires an internet connection."""
    Tournament.import_airtable()

@cli.command()
@click.argument('output_path', type=click.Path(exists=False))
def export_csv(output_path):
    """Export a CSV file with aggregate statistics for each team"""
    Tournament.export_csv(output_path)

@cli.command()
@click.argument('input_path', type=click.File())
def import_match_schedule_csv(input_path):
    """Import match schedule from a csv file. 
    Each row should have the match number, the three red teams, then the three blue teams"""
    next(input_path)
    reader = csv.reader(input_path)
    for row in reader:
        match_number = int(row[0])
        team_numbers = list(map(lambda x: int(x), row[1:7]))
        Tournament.add_match_to_schedule(match_number, team_numbers)

@cli.command()
def import_match_schedule_tba():
    """Import the match schedule from The Blue Alliance. Requires an internet connection."""
    tba = tbapy.TBA(Constants.TBA_API_KEY)

    # Get match schedule
    num_qual_matches = 0
    tba_matches = tba.event_matches(Constants.EVENT_KEY, simple=True)
    for match in tba_matches:
        if match.comp_level == 'qm':
            team_numbers = []
            # Team keys come in the format 'frcXXXX', so we'll parse just the number out
            team_numbers += list(map(lambda x: int(x[3:]), match.alliances['red']['team_keys']))
            team_numbers += list(map(lambda x: int(x[3:]), match.alliances['red']['surrogate_team_keys']))
            team_numbers += list(map(lambda x: int(x[3:]), match.alliances['blue']['team_keys']))
            team_numbers += list(map(lambda x: int(x[3:]), match.alliances['blue']['surrogate_team_keys']))
            Tournament.add_match_to_schedule(match.match_number, team_numbers)
            num_qual_matches += 1

    # Print match schedule
    view = input('\tSuccessfully imported %d matches. View schedule (Y\\N)? ' % num_qual_matches)
    if (view == 'Y'):
        Tournament.print_match_schedule()


@cli.command()
@click.argument('match_number', type=click.INT)
def get_match_statistics(match_number):
    """Get statistics for a specific match"""
    output = Tournament.build_match_statistics_string(match_number)
    print(output)

@cli.command()
def start_slack_bot_server():
    start_slack_bot()
        
