"""Components for a training game of Deduce or Die

"""

import logging
import random
import copy


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


class DodException(Exception):
    """ A simple exception to represent Deduce or Die exceptions"""
    pass

class Card():
    """A card consists of a rank and suit

    Cards can have a rank of [1-9]
    Cards have a suit of ['D', 'H', 'S'] which correspond to Diamonds,
    Hearts and Spades
    """

    suits = ['D', 'H', 'S']
    # Ranks are 1-9
    ranks = range(1, 10)

    def __init__(self, rank, suit):
        """Create a single card of the given suit and rank

        Args:
            rank : The rank of the card [1-9]
            Suit : The suit of the card ['D', 'H', 'S'] 

        Returns : A Card object initilzied according to the parameters

        Raises : ValueError: The rank or suit are not valid
        """

        if rank in Card.ranks:
            self.rank = rank
        else:
            raise ValueError("Card creation error. Bad Rank:{}", format(rank))

        if suit in Card.suits:
            self.suit = suit
        else:
            raise ValueError("Card creation error. Bad Suit:{}", format(suit))

    def __repr__(self):
        return "{}{}".format(self.rank, self.suit)


class Deck:
    """A deck represents a collection of cards

    A Deck will have both a collection of cards that can be drawn
    and a seperate collection of cards that have been discarded.
    """

    def __init__(self, name=None):
        """Create a deck of cards with the given name.

        A full deck of Cards will be produced (all suits, all ranks) and then
        shuffled. The discards will be empty.

        Args:
            name : The name of the deck. This is primarily used for logging.
                   The name is optional and will be 'None' if not set

        Returns:
            A fully initialized instance of Deck.
        """

        self.log = logging.getLogger(self.__class__.__name__)
        if name:
            self.name = name
        else:
            self.name = str(id(self))

        self.discards = []
        self.cards = []
        for s in Card.suits:
            for r in Card.ranks:
                card = Card(r, s)
                self.cards.append(card)

    def draw(self, num_cards=1):
        """Draw the indicated number of cards from the deck.

        Cards are removed from the deck and will not be drawn again.
        If the deck is empty discards will be shuffled into the
        deck to produce the required cards.

        Args:
            num_cards : Number of cards to draw. Default = 1

        Returns:
            A list with the cards drawn

        Raises:
            IndexError : If a draw is attempted on an empty deck.
                         This can happen if the deck cards are empty
                         as well as the discards.
        """

        cards_drawn = []
        for i in range(num_cards):
            if not len(self.cards):
                #
                # The deck ran out of cards.
                # shuffle over the discard deck
                #
                self.cards = self.discards
                random.shuffle(self.cards)
                self.discards = []
                self.log.info("Deck Shuffled: {}".format(self.name))
                if len(self.cards):
                    self.log.info(self.cards)
                else:
                    self.log.warn("{} Deck Empty!".format(self.name))

            cards_drawn.append(self.cards.pop())

        return cards_drawn

    def discard_cards(self, d_cards):
        """ Put a set of cards on the discard pile for this deck.

        Args:
            d_cards : A list of cards to take as discards
        """

        # TODO: Would it be a good idea to add a "deck"
        # attribute to Card and throw an exception
        # if a card was discarded into the wrong deck?
        self.discards += d_cards

    def combine(self, other):
        """ Combine another deck with this deck.

        The contents of the other deck are added to this deck.

        Args:
            other : The deck to add to this one.

        Raises:
            ValueError if the object passed in is not a Deck

        """

        if not isinstance(other, Deck):
            raise ValueError("A Deck can only be combined with another deck")

        self.cards += other.cards

    def __repr__(self):
        out_string = ""
        for idx, c in enumerate(self.cards[:-1], start = 1):
            
            if idx % 9 == 0:
                out_string += "{}\n".format(c)
            else:
                out_string +=  "{}, ".format(c)

        # Add the last card without a newline, space or comma
        out_string += "{}".format(self.cards[idx])
        return out_string


class Hand():
    """ A hand is a collection of cards for a Deduce or Die player

    A hand contains the cards used by a Deduce or Die player. A Hand is
    used during the game to count the cards the player has across suits
    and ranges.
    """

    __suit_idx = {'D' : 0,
                  'H' : 1,
                  'S' : 2}

    __initial_grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0], # Diamonds
                      [0, 0, 0, 0, 0, 0, 0, 0, 0], # Hearts
                      [0, 0, 0, 0, 0, 0, 0, 0, 0]] # Spades

    def __init__(self, player, hand_size, deck):
        """Create a player hand of cards

        Draw a hand of cards with a set number from the indicated deck.
        The hand will be identified with a specific player.

        Args:
            player : The name of the player that the hand belongs to
            hand_size : The number of cards to draw for the hand
            deck : The deck from which the hand will be drawn.

        Returns:
            An instance of Hand with the appropriate number of cards.
        """
        self.log = logging.getLogger(self.__class__.__name__)        
        self.player = player
        self.cards = deck.draw(hand_size)
        self.__create_grid()
        self.__least_suit()
        self.log.info("Player {} Hand: {}".format(self.player, self.cards))
        self.log.info("Player {} Grid: {}".format(self.player, self.grid))

    def __create_grid(self):
        # Create an empty grid
        # 
        self.grid = copy.deepcopy(Hand.__initial_grid)

        # Fill the grid based on the hand
        for c in self.cards:
            #
            # The grid is accessed by suit(x) and rank(y)
            # Convert the suit char to an index (ignore case)
            #
            x = Hand.__suit_idx[c.suit]
            y = c.rank - 1
            if self.grid[x][y] != 0:
                raise Exception("Duplicate card in hand")

            self.grid[x][y] = 1

    #
    #  Calculate 'least suit' for the hand
    #
    def __least_suit(self):
        count_map = {}
        for s in self.__suit_idx:
            count = self.grid[self.__suit_idx[s]].count(1)
            if count_map.get(count):
                count_map[count].append(s)
            else:
                count_map[count] = [s]

        least_set = min(count_map.keys())
        self.least = random.choice(count_map[least_set])

        self.log.info("Player {} least suit = {}/{}: Choice: {}".format(
            self.player, least_set, count_map[least_set], self.least))

    #
    #  Use the grid to count the number of cards for the suit
    #
    def __count_range(self, start, end, s_idx):
        player_suit = self.grid[s_idx]
        if start <= end:
            card_count = player_suit[start - 1:end].count(1)
        else:
            #
            #  Create a list made of the elements before and after
            #  the "proper" range made from the card ranks
            #
            card_count = (player_suit[:end] + player_suit[start-1:]).count(1)

        return card_count

    def count_suit(self, start, end, suit):
        """Count the number of cards in the hand over the indicated range

        Count the cards in the hand that are within the range given.
        If a suit is given the count will only include cards of that suit.
        If no suit is given the count will include all suits.

        The inputs will be validated for proper ranks and suit identifiers.

        Args:
            start, end : Integers. Describe the start and end of the range
                         inclusive. The range "wraps".
                         start=1, end=7 : [1, 2, 3, 4, 5, 6, 7]
                         start=7, end=1 : [7, 8, 9, 1]
            suit : A letter indicating the suit. Case insensitive.
                   if suit is None then all suits will be counted.                         

        returns:
            An integer count of the number of cards in the range.

        raises:
            DodException : If the suit is not valid. 
                            i.e. not [d, h, s, D, H, S]
        """
        if start < 1 or start > 9:
            raise DodException("Invalid start")

        if end < 1 or end > 9:
            raise DodException("Invalid end")

        card_count = 0
        if suit:
            try:
                s_idx = self.__suit_idx[suit.upper()]
                card_count = self.__count_range(start, end, s_idx)
            except KeyError:
                raise DodException("Invalid suit")
        else:                
            card_count =  self.__count_range(start, end, 0)
            card_count += self.__count_range(start, end, 1)
            card_count += self.__count_range(start, end, 2)

        return card_count


    def __repr__(self):
        return str(self.cards)


class DodSession():
    """Play a session of Deduce or Die

    Shuffle the player deck and deal two hidden cards as evidence.
    Each player draws the following number of cards
     3 players - 8 cards
     4 players - 6 cards
     5 players - 5 cards
     6 players - 4 cards
    All the cards are dealt out in a 5. Otherwise, there will be one
    card left over. Expose this card.
    Shuffle the question deck
    Player one is the "human" player.
    """

    __cards_per_player = {3:8,
                        4:6,
                        5:5,
                        6:4}


    #
    # Initialize the basic setup for DoD
    # * Validate game paramaters
    # ** Valid number of players
    # * 2 Evidence cards
    # * Deal cards to each player
    # * Identify the exposed card, if any.
    #
    def __init__(self, num_players):
        """Initialize the basic setup for DoD
        * Validate game paramaters
        ** Valid number of players
        * 2 Evidence cards
        * Deal cards to each player
        * Identify the exposed card, if any.

        Args:
            num_players : The number of players to setup

        Returns:
            An instance of Deduce or Die ready for questions

        Raises:
            DodException : If the deal doesn't add up.
        """

        self.log = logging.getLogger(self.__class__.__name__)

        if num_players < 3 or num_players > 6:
            raise ValueError("Too many players ({}). There must be 3-6 players".format(num_players))
        self.num_players = num_players

        #
        # Create the player deck
        #
        self.player_deck = Deck('Player')

        #  The question deck is made of two decks
        #
        self.question_deck = Deck('Question')
        self.question_deck.combine(Deck())

        self.log.info("Player Deck: \n{}".format(self.player_deck))
        self.log.info("Question Deck:\n{}".format(self.question_deck))

        self.exposed = None
        self.hands = []
        self.questions = []
        #
        # Evidence is the first two cards of the deck
        #
        self.evidence = self.player_deck.draw(2)
        self.log.info("Evidence: {}".format(self.evidence))

        num_cards = DodSession.__cards_per_player[num_players]
        # Hand numbering starts with player 1
        for p in range(1, num_players+1):
            self.hands.append(Hand(str(p), num_cards, self.player_deck))

        try:
            self.exposed = self.player_deck.draw()
        except IndexError:
            #
            # Deck is empty.
            # That's OK if the number of players is 5
            #
            if not num_players == 5:
                raise DodException("Bad Deal")

        self.log.info("Exposed: {}".format(self.exposed))

    def draw_questions(self):
        """Draw 3 question cards from the question deck

        Returns:
            A list with the 3 question cards
        """

        self.question_cards = self.question_deck.draw(3)
        return self.question_cards

    def discard_questions(self):
        """Return the question cards to the question deck

        The question cards are put into the question deck
        discard pile
        """

        self.question_deck.discard_cards(self.question_cards)

    def count_suit(self, player, start, end, suit):
        """Count the cards in the give range for the indicated player

        Validate that the player exists.
        Count the number of cards in the players hand for the range indicated.
        If a suit is provided then the count will only include cards of that
        suit. A suit of None will cause cards of all suits to be counted.

        Args:
            player : Integer indicating the player. Player indexes start at 1
                     Player 1 is the human player.
            start : Integer for the start of the range [1-9] inclusive.
            end : Integer for the end of the range [1-9] inclusive.
            suit : Suit for the range [D, H, S] case insensitive.
                   None if cards of all suits will be counted.

        returns:
            An integer count of the number of cards in the range.

        raises:
            DodException : If the suit is not valid. 
                            i.e. not [d, h, s, D, H, S] 
        """

        if player <= 0 or player > self.num_players:
            raise DodException("Invalid player")

        return self.hands[player-1].count_suit(start, end, suit)