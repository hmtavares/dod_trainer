#!/usr/bin/env python
"""A UI session for a game of Deduce or DIe
"""
import datetime
import logging
import random
import copy
import argparse
import cmd
from dod_game import *

# Shuffle the Motive deck well and place two cards face down to the side, making
# sure that no one sees what they are. These cards are called the Evidence cards.
# Then deal the following number of cards to each player face down:
# 3 players - 8 cards
# 4 players - 6 cards
# 5 players - 5 cards
# 6 players - 4 cards
# All the cards are dealt out in a I've player game. Otherwise, there will be one
# card left over. Expose this card, let everyone take note of it, and then place it
# aside, out of the game. The players can now secretly look at the cards dealt to
# them and make any notes they like on their deduction sheets.
# Shuffle the Interrogation deck and place it in the center of the table.
# Randomly choose one player to go first.

DEFAULT_LOGFILE = 'dod'
DEFAULT_LOG_LEVEL = 'INFO'

def setup_logging(time_now, log_level, log_path, log_filename):

    global log
    global root_logger
    global console_handler

    timestamp_now = time_now.strftime('%Y%m%d_%H%M%S')

    levels = {'ERROR'   :logging.ERROR,
              'WARNING' :logging.WARNING,
              'INFO'    :logging.INFO,
              'DEBUG'   :logging.DEBUG}

    log_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(module)s.%(name)s.%(funcName)s] %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(levels[log_level])

    log_file = log_path + '/' + log_filename + '_' + timestamp_now + '.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    log = logging.getLogger()
    return log_file

parser = argparse.ArgumentParser(description='Play a practice session of Deduce or Die')

parser.add_argument('--logfile', dest='log_file', default=DEFAULT_LOGFILE,
                        help='The name of the log file. Default={}_<timestamp>.log'.format(DEFAULT_LOGFILE))
parser.add_argument('--level', dest='log_level', default=DEFAULT_LOG_LEVEL,
                        help='Set the log level for the application log. ' \
                             '[ERROR, WARN, INFO, DEBUG] Default={}'.format(DEFAULT_LOG_LEVEL))
parser.add_argument( 'num_players', help='Number of players (3-6)')


args = parser.parse_args()

time_now = datetime.datetime.now()
full_log_file = setup_logging(time_now, args.log_level, '.', args.log_file)


log.info("Session Start: {players}".format(players=args.num_players))

class DeduceCommands(cmd.Cmd):
    """Command processor for Deduce or Die"""

    def __init__(self, num_players):
        """Create a command processor for Deduce or Die

        Create a Deduce or Die session for the number of indicated
        players. Initilize the startup messages.

        Args:
            num_players : The number of players for the session

        Returns:
            An initilized command processor for Deduce or Die

        Raises:
            ValueError: An invalid number of players.
        """


        self.log = logging.getLogger(self.__class__.__name__)

        cmd.Cmd.__init__(self)
        self.dod = DodSession(num_players)
        least_msg = ""   
        for h in self.dod.hands:
            least_msg += "Player {} least suit: {}\n".format(h.player, h.least)
        self.intro = '''
Exposed: {}
{}
Your hand: {}
'''.format(self.dod.exposed, least_msg, self.dod.hands[0])

        self.question_cards = self.dod.draw_questions()
        self.prompt = str(self.dod.question_cards) + ':'
        self.questions = []

    doc_header = 'doc_header'
    misc_header = 'misc_header'
    undoc_header = 'undoc_header'
    
    ruler = '-'

    #
    # Validate the ask command line
    # * There must be at least 3 parameters
    # * start and end must be integers
    # * Return the parsed parameters: player, start, end, suit
    #
    def __ask_validate(self, parms):
        parm_len = len(parms)
        if parm_len < 3:
            raise DodException("Not enough parameters")
        if parm_len > 4:
            print "ignoring extra parameters"
        
        (player, start, end) = parms[:3]
        try:
            player = int(player)
            start = int(start)
            end = int(end)
        except ValueError:
            raise DodException("Non-numeric value for player, start or end")

        suit = None
        if parm_len >= 4:
            suit = parms[3]

        return (player, start, end, suit)

    def do_ask(self, line):
        """Ask a player for the number of cards in a range

        Command Format:
        > ask <player #> <start #> <end #> [Suit char]
        player, start and end are required. Suit is optional.
        If a suit is not provided then all suits will be counted.

        * Parse and validate the command parameters.
        * Get the count from the DoD session.
        * Print the number of cards that match the question.
        * Remember the question so it can be reported later
        * Discard the current question cards
        * Draw 3 new question cards
        * Update the prompt

        Args:
            line: The string that contains the paramaters after "ask"
        """

        parms = line.split()
        player = None
        start = None
        end = None
        suit = None
        s_idx = None
        try:
            (player, start, end, suit) = self.__ask_validate(parms)
            card_count = self.dod.count_suit(player, start, end, suit)
        except DodException as e:
            print e.message
            return

        answer = None
        if not suit:
            suit = "*"

        answer = "Ask: Player {} | {}-{}:{} / Answer: {}".format(
            player, start, end, suit, card_count)

        print answer
        self.questions.append(answer)
        log.info(answer)

        #
        #  Discard the old question cards.
        #  Deal new question cards.
        #
        self.dod.discard_questions()
        self.prompt = str(self.dod.draw_questions()) + ":"
        log.info(str(self.prompt))
    
    def do_reveal(self, line):
        """Show the evidence cards and the hands of all players"""

        print "Evidence: {}".format(self.dod.evidence)
        print "Exposed: {}".format(self.dod.exposed)

        idx = 1
        for h in self.dod.hands:
            print "Player {}: {}".format(h.player, h)

    def do_hand(self, line):
        """Show the player hand and other starting known information"""

        print self.intro

    def do_report(self, line):
        """Show all asked questions and answers"""

        for q in self.questions:
            print q

    def do_EOF(self, line):
        return True

DeduceCommands(int(args.num_players)).cmdloop()
