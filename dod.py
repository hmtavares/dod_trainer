#!/usr/bin/env python

#import sys
import datetime
import logging
import random
import copy
#import shutil
#import json
#import re
#import time
import argparse
import cmd

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

log = None

def setup_logging(time_now, log_level, log_path, log_filename, mode):

    global log
    global root_logger
    global console_handler

    timestamp_now = time_now.strftime('%Y%m%d_%H%M%S')

    levels = {'ERROR'   :logging.ERROR,
              'WARNING' :logging.WARNING,
              'INFO'    :logging.INFO,
              'DEBUG'   :logging.DEBUG}

    #log_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(module)s.%(funcName)s] %(message)s')
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(levels[log_level])

    log_file = log_path + '/' + log_filename + '_' + timestamp_now + '.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    log = logging.getLogger(mode)
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
full_log_file = setup_logging(time_now, 'DEBUG', '.', args.log_file, 'UPGRADE_PREP')


# Cards per player
# 3 players - 8 cards
# 4 players - 6 cards
# 5 players - 5 cards
# 6 players - 4 cards
cards_per_player = {3:8,
                    4:6,
                    5:5,
                    6:4}

#Create deck of cards
suits = ['D', 'H', 'S']
ranks = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

def create_player_deck():
    deck = []
    for s in suits:
        for r in ranks:
            card = r + s
            deck.append(card)

    return deck

suit_idx = {'D' : 0,
            'H' : 1,
            'S' : 2}
initial_grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0], # Diamonds
                [0, 0, 0, 0, 0, 0, 0, 0, 0], # Hearts
                [0, 0, 0, 0, 0, 0, 0, 0, 0]] # Spades
    
def create_grid(hand):
    # Create an empty grid
    # 
    hand_grid = copy.deepcopy(initial_grid)

    # Fill the grid based on the hand
    for c in hand:
        #
        # The grid is accessed by suit(x) and rank(y)
        # Convert the suit char to an index (ignore case)
        #
        x = suit_idx[c[1].upper()]
        y = int(c[0]) - 1
        if hand_grid[x][y] != 0:
            raise Exception("Duplicate card in hand")

        hand_grid[x][y] = 1

    log.info("Hand Grid: {}".format(hand_grid))
    return hand_grid

#
#  Calculate 'least suit' for each player
#
def least_suit(player_grid):
    count_map = {}
    for s in suit_idx:
        count = player_grid[suit_idx[s]].count(1)
        if count_map.get(count):
            count_map[count].append(s)
        else:
            count_map[count] = [s]

    log.info("Count Map: {}".format(count_map))
    least = min(count_map.keys())
    log.info("least suit = {}/{}".format(least, count_map[least]))
    choice = random.choice(count_map[least])
    log.info("choice: {}".format(choice))
    return choice


log.info("Session Start: {players}".format(players=args.num_players))


player_deck = create_player_deck()
random.shuffle(player_deck)
question_deck = player_deck + create_player_deck()
discard_deck = []
random.shuffle(question_deck)

log.info("Player Deck: \n{}".format(player_deck))
log.info("Question Deck:\n{}".format(question_deck))

exposed = None
hands = []
grids = []
questions = []
#
# Evidence is the first two cards of the deck
#
evidence = player_deck[:2]
log.info("Evidence: {}".format(evidence))

#
# Create player hands with the rest of the deck
#
player_leasts = []
start = 2
num_players = int(args.num_players)
for p in range(num_players):
    end = start + cards_per_player[num_players]
    cur_hand = player_deck[start:end]
    start = end
    hands.append(cur_hand)
    grids.append(create_grid(cur_hand))
    log.info("Player Hand: {}".format(hands[p]))
    log.info("Player Grid: {}".format(grids[p]))
    player_leasts.append(least_suit(grids[p]))

#
# If one card is left over then expose it.
# This should happen for everything but 5 players
#
if end == 26:
    exposed = player_deck[-1:][0]
elif end != 27:
    message = "Too many cards left over: {}".format(end)
    log.error(message)
    raise Exception(message)

exposed_message = "Exposed: {}".format(exposed)
print exposed_message
log.info(exposed_message)

for p_idx in range(num_players):
    message = "Player {} least suit: {}".format(p_idx + 1, player_leasts[p_idx])
    print message
    log.info(message)

print "Your hand: {}".format(hands[0])
#
# Show the player the exposed card (if any)
# Show the player their hand (hand 0)
#
# Start the command processor. The processor should
# always have 3 cards from the question deck exposed.
#
# Commands:
#
# - Ask - Ask a question based on the question deck cards.
#         validate, answer and draw 3 new cards.
#
# - Reveal - Show the evidence cards and the hands of
#            the other players. Ends game
# 
# - Hand - Show the player hand and the exposed card if there is one,
#          and the current 3 cards off the question deck.
#
# - Report - Show all asked questions and answers
#

def draw_questions(q_deck, d_deck):
    question_cards = []
    for i in range (3):
        if not len(q_deck):
            #
            # The question deck ran out of cards.
            # shuffle over the discard deck
            #
            q_deck = d_deck
            random.shuffle(q_deck)
            d_deck = []
            log.info("Question Deck Shuffled")
            log.info("  Len: {}".format(len(q_deck)))
            log.info(q_deck)

        #
        # Draw on card from the question deck
        #
        question_cards.append(q_deck.pop())

    return (question_cards, q_deck, d_deck)

def count_range(grid, start, end, s_idx):
    player_suit = grid[s_idx]
    if start <= end:
        card_count = player_suit[start - 1:end].count(1)
    else:
        #
        #  Create a list made of the elements before and after
        #  the "proper" range made from the card ranks
        #
        card_count = (player_suit[:end] + player_suit[start-1:]).count(1)

    return card_count

class DodException(Exception):
    pass

class Deduce(cmd.Cmd):
    """Play Deduce or Die"""

    def __init__(self, question_deck, discard_deck):
        #
        # Setup initial question cards
        #
        (self.question_cards, self.question_deck, self.discard_deck) = draw_questions(question_deck, discard_deck)
        cmd.Cmd.__init__(self)
        self.prompt = str(self.question_cards) + ':'

    intro = "Deduce or Die"

    doc_header = 'doc_header'
    misc_header = 'misc_header'
    undoc_header = 'undoc_header'
    
    ruler = '-'

    def ask_validate(self, parms):
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
        s_idx = None
        if parm_len >= 4:
            suit = parms[3]
            try:
                s_idx = suit_idx[suit.upper()]
            except KeyError:
                raise DodException("Invalid suit")

        if player > num_players:
            raise DodException("Invalid player")

        if start < 1 or start > 9:
            raise DodException("Invalid start")

        if end < 1 or end > 9:
            raise DodException("Invalid end")

        return (player, start, end, suit, s_idx)

    def do_ask(self, line):
        #
        # ask player start_rank end_rank [suit]
        # If suit is not provided it is assumed all suits
        #
        parms = line.split()
        player = None
        start = None
        end = None
        suit = None
        s_idx = None
        try:
            (player, start, end, suit, s_idx) = self.ask_validate(parms)
        except DodException as e:
            print e.message
            return

        answer = None
        if suit:
            card_count = count_range(grids[player - 1], start, end, s_idx)
            answer = "Ask: Player {} | {}-{}:{} / Answer: {}".format(player, start, end, suit, card_count)
        else:
            card_count =  count_range(grids[player - 1], start, end, 0)
            card_count += count_range(grids[player - 1], start, end, 1)
            card_count += count_range(grids[player - 1], start, end, 2)
            answer = "Ask: Player {} | {}-{}:* / Answer: {}".format(player, start, end, card_count)

        print answer
        questions.append(answer)
        log.info(answer)

        #
        #  Discard the old question cards.
        #  Deal new question cards.
        #
        self.discard_deck += self.question_cards
        (self.question_cards, self.question_deck, self.discard_deck) = draw_questions(self.question_deck, self.discard_deck)
        self.prompt = str(self.question_cards) + ':'
        log.info(str(self.question_cards))
    
    def do_reveal(self, line):
        print "Evidence: {}".format(evidence)
        print "Exposed: {}".format(exposed)

        idx = 1
        for h in hands:
            print "Player {}: {}".format(idx, h)
            idx += 1

    def do_hand(self, line):
        print "Exposed: {}".format(exposed)
        for p_idx in range(num_players):
            print "Player {} least suit: {}".format(p_idx + 1, player_leasts[p_idx])
        print "Your hand: {}".format(hands[0])

    def do_report(self, line):
        for q in questions:
            print q

    def do_prompt(self, line):
        "Change the interactive prompt"
        self.prompt = line + ': '

    def do_EOF(self, line):
        return True

Deduce(question_deck, discard_deck).cmdloop()
