import statistics

class Team:
    """ Class to represent all the data about a specific team over the course of a
        tournament.

        Public methods are automatically turned into columns on a CSV export.
    """

    def __init__(self, team_number):
        self.team_number = team_number
        self.match_numbers = []
        self.starting_locations = []
        self.line_crossed = []
        self.hatches_scored = []
        self.cargo_scored = []
        self.sandstorm_attempts = []
        self.sandstorm_successes = []
        self.end_game = []

    def _add_match_data(self, match_number, starting_location, line_crossed,
                        hatches_scored, cargo_scored, sandstorm_attempt,
                        sandstorm_success, end_game):
        if match_number in self.match_numbers:
            return
        self.match_numbers.append(match_number)
        self.starting_locations.append(starting_location)
        self.line_crossed.append(line_crossed)
        self.hatches_scored.append(hatches_scored)
        self.cargo_scored.append(cargo_scored)
        self.sandstorm_attempts.append(sandstorm_attempt)
        self.sandstorm_successes.append(sandstorm_success)
        self.end_game.append(end_game)

    def hatch_scored_mean(self):
        return statistics.mean(self.hatches_scored)

    def cargo_scored_mean(self):
        return statistics.mean(self.cargo_scored)

    def hatch_scored_variance(self):
        return statistics.pvariance(self.hatches_scored)

    def cargo_scored_variance(self):
        return statistics.pvariance(self.cargo_scored)

    def hab_1_percentage(self):
        return self.end_game.count(3) / len(self.end_game)

    def hab_2_percentage(self):
        return self.end_game.count(6) / len(self.end_game)

    def hab_3_percentage(self):
        return self.end_game.count(12) / len(self.end_game)

    def end_game_score_mean(self):
        return statistics.mean(self.end_game)

    def end_game_score_variance(self):
        return statistics.pvariance(self.end_game)

    def __sandstorm_success_rate(self, location):
        attempts = 0
        successes = 0
        for i in range(0, len(self.sandstorm_attempts)):
            if self.sandstorm_attempts[i] is not 'Nothing attempted':
                attempts += 1
                if self.sandstorm_successes is location:
                    successes += 1
        return successes / attempts

    def sandstorm_rocket_success_rate(self):
        return self.__sandstorm_success_rate('Rocket')

    def sandstorm_ship_success_rate(self):
        return self.__sandstorm_success_rate('Cargoship')

    def sandstorm_all_success_rate(self):
        return self.sandstorm_rocket_success_rate() + self.sandstorm_ship_success_rate()

    def _total_contribution_without_climb(self, matchIndex):
        score = 0
        if self.line_crossed[matchIndex]:
            if self.starting_locations[matchIndex] is 'Hab':
                score += 3
            else:  # Started on HAB 2
                score += 6
        if self.sandstorm_successes is not 'Failed to score':
            if self.sandstorm_attempts is 'Cargo':
                score += 3
            else:  # Scored a hatch
                if self.sandstorm_successes is 'Cargoship':
                    # Assuming they placed it on the front,
                    # effectively scoring 5 pts
                    score += 5
                else:
                    score += 2
        score += self.hatches_scored[matchIndex] * 2
        score += self.cargo_scored[matchIndex] * 3
        return score

    def _total_contribution(self, match_index):
        return self._total_contribution_without_climb(match_index) + self.end_game[match_index]

    def total_contribution_without_climb_mean(self):
        contributions = []
        for i in range(0, len(self.match_numbers)):
            contributions.append(self._total_contribution_without_climb(i))
        return statistics.mean(contributions)

    def total_contribution_without_climb_variance(self):
        contributions = []
        for i in range(0, len(self.match_numbers)):
            contributions.append(self._total_contribution_without_climb(i))
        return statistics.pvariance(contributions)

    def total_contribution_mean(self):
        contributions = []
        for i in range(0, len(self.match_numbers)):
            contributions.append(self._total_contribution(i))
        return statistics.mean(contributions)

    def total_contribution_variance(self):
        contributions = []
        for i in range(0, len(self.match_numbers)):
            contributions.append(self._total_contribution(i))
        return statistics.pvariance(contributions)

    def left_start_percentage(self):
        return self.starting_locations.count('Left Mid level') / len(self.starting_locations)

    def right_start_percentage(self):
        return self.starting_locations.count('Right Mid level') / len(self.starting_locations)

    def low_start_percentage(self):
        return self.starting_locations.count('Hab') / len(self.starting_locations)


def predict_match_score(red_teams, blue_teams):
    """ Given a hypothetical match with these six teams, predict what the
        final score will be.
    """
    if len(red_teams) != 3:
        raise ValueError("Must have 3 teams on the red alliance")
    if len(blue_teams) != 3:
        raise ValueError("Must have 3 teams on the red alliance")
    red_score = 0
    blue_score = 0

    # TODO: Deal with the fact that only one robot can climb onto HAB 3
    # TODO: Consider that only two teams can start on HAB 2
    # TODO: Use variance to create a confidence interval of which alliance
    # will win the match
    for team in red_teams:
        red_score += team.total_contribution_mean()
    for team in blue_teams:
        blue_score += team.total_contribution_mean()
    return (red_score, blue_score)
