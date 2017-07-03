# Deduce or Die trainer
A solitaire trainer for Deduce or Die

Deduce or Die is a deductive card game where players each have a hand of cards and try and figure out who has a specific card.

Some handy references
* [Rules for Deduce or Die](http://www.thegamesjournal.com/rules/DeduceOrDie.shtml)
* [Deduce or Die Boardgame Geek page](https://boardgamegeek.com/boardgame/19765/deduce-or-die)

# Origin
I was introduced to the game by some friends and was terrible at it. I decided I needed to "practice". I cobbled together this solitaire version of DoD to facilitate practicing.

The core game mechanics are completly formalized and don't require any human interaction. You "ask" another player a formal question using one of the following forms:
* How many cards do you have between X & Y of any suit
* How many cards do you have between X & Y of a specific suit

Normally this would rotate around the table, each player asking a question. In this solitaire format the single player asks all the questions of the other (computer) players. Not as fun but definitly aids in figuring out what kinds of questions to ask, how to record the question and the response and how to use the information to deduce the final answer.

# Requirements
* Python 2.7


# Starting a game
```
./dod.py -h
usage: dod.py [-h] [--logfile LOG_FILE] [--level LOG_LEVEL] num_players

Play a practice session of Deduce or Die

positional arguments:
  num_players         Number of players

optional arguments:
  -h, --help          show this help message and exit
  --logfile LOG_FILE  The name of the log file. Default=dod.log
  --level LOG_LEVEL   Set the log level for the application log. [ERROR, WARN,
                      INFO, DEBUG] Default=INFO
```

So to start a 4 player game you would do something like:
```
./dod.py 4
```
This would start a 4 player game and use defaults for everything else. It would produce a logfile called something like dod_20170703_140844.log

# Very Brief Rules Overview
This document assumes you're familiar with the rules of Deduce or Die. Please refer to the rules link above. A few highlights just in case you decided to skip the rules:
* 3-6 players
* Player Deck: One Deck of cards made up of 1-9, Diamonds, Hearts, Spades (27 cards)
* Question Deck: One deck of cards made up two setups like the Player Deck (54 cards)
* Deal from the Player Deck
   * Deal two secret cards called "Evidence". Set them aside.
   * Deal each player an equal number of cards using as many cards as possible.
   * For all but 5 players this will leave one card left over. Expose this card to all players.
* Each player states which suit they have the least number of cards.
* Deal from the Question Deck
   * Expose the top 3 cards from the question deck.
   * The current player (always player 1 in this solitaire game) asks another player about thier hand based on these 3 cards.
   * Repeat.


# The Game

## Start

Let's start a 4 player game
```
./dod.py 4
```

The game starts by presenting the initial information for the game and then providing a prompt for further commands:
```
Exposed: 3S
Player 1 least suit: H
Player 2 least suit: S
Player 3 least suit: H
Player 4 least suit: D
Your hand: ['1D', '7D', '1H', '1S', '4S', '6D']
Deduce or Die
['2D', '9S', '9S']:

```
In the above example we see that our hand has 6 cards (a 4 player game gives each player 6 cards)
* 1 Diamonds
* 7 Diamonds
* 1 Hearts
* 1 Spades
* 4 Spades
* 6 Diamonds

We also see that the "3 Spades" has been exposed. (In a 4 player game one card is exposed).

Additionally we know which suit each player has the least of. This is all the information we know at the start of the game.

## The Prompt
Following the initial information discussed above there is a prompt that looks like this:
```
['2D', '9S', '9S']:
```

This shows the 3 cards drawn from the question deck and is waiting for a command.

## Commands
### hand
* parameters
   * None.

Display the players hand and other information known at the start of the game.

```
['2D', '9S', '9S']:hand
Exposed: 3S
Player 1 least suit: H
Player 2 least suit: S
Player 3 least suit: H
Player 4 least suit: D
Your hand: ['1D', '7D', '1H', '1S', '4S', '6D']
```

### report
* Parameters
   * None.

Display all the questions asked and the responses

```
Ask: Player 3 | 2-9:* / Answer: 6
Ask: Player 2 | 8-1:h / Answer: 2
...
```

### reveal
* Parameters
   * None.

Display all the secret information for the game.
* Each Players hands
* The "evidence" cards
* The exposed card

```
['2D', '9S', '9S']:reveal
Evidence: ['6S', '3D']
Exposed: 3S
Player 1: ['1D', '7D', '1H', '1S', '4S', '6D']
Player 2: ['3H', '4D', '8D', '2H', '8H', '9H']
Player 3: ['2D', '5H', '5S', '5D', '9S', '7H']
Player 4: ['7S', '2S', '8S', '9D', '4H', '6H']
```
This command is used when you think you have deduced the hidden cards or if you're giving up.

### ask
* Parameters
   * player number
   * start of range (inclusive)
   * end of range (inclusive)
   * suit (optional)

Display the number of cards the indicated player has in the range requested. If a suit is provided then the count will only include cards of that suit. If no suit is provided then the count will be for all suits.

A new set of 3 cards will be dealt from the Question Deck

```
['2D', '9S', '9S']:ask 3 2 9
Ask: Player 3 | 2-9:* / Answer: 6
['1H', '3D', '8H']:
```
Above we can see the question asked is "Player 3, how many cards do you have of all suits from 2 through 9?". The answer is "6 cards"

```
['1H', '3D', '8H']:ask 2 8 1 h
Ask: Player 2 | 8-1:h / Answer: 2
['5H', '9H', '7H']:
```
Above we see the question asked is "Player 2, how many cards do you have of Hearts, 8 through 1". The answer is "2 cards". Note that the range wraps around so the range 8-1 would be [8, 9, 1]

Note that there is no validation so any range can always be asked. Don't cheat.

The rules allow for a special condition when an identical set of two cards are drawn, such as the set of 9s in the example above. This allows a player to ask for "all Spades". This can be done by simply asking for the entire range, i.e. ```ask 3 1 9 s```
