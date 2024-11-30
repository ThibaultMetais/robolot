from enum import Enum
from random import randint, shuffle, choice

import pandas as pd
import pygame


# Dumb mode settings
DUMB_BID_RAISE_PROB = 0.2
DUMB_COINCHE_PROB = 0.05
DUMB_SURCOINCHE_PROB = 0.02

# Card points
CARD_POINTS = {
    "7": 0,
    "8": 0,
    "9": 0,
    "J": 2,
    "Q": 3,
    "K": 4,
    "10": 10,
    "A": 11
}
TRUMP_CARD_POINTS = {
    "7": 0,
    "8": 0,
    "Q": 3,
    "K": 4,
    "10": 10,
    "A": 11,
    "9": 14,
    "J": 20
}


class Value(Enum):
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    TEN = "10"
    ACE = "A"


class Color(Enum):
    HEARTS = "hearts"
    SPADES = "spades"
    CLUBS = "clubs"
    DIAMONDS = "diamonds"


class Card:
    def __init__(self, color: Color, value: Value):
        """
        A class that represents a single card in the game.

        :param color: the color of the card.
        :param value:the value of the card.
        :return: None
        """
        self.color = color
        self.value = value
        self.image = pygame.image.load('images/' + self.value + '_of_' + self.color + '.png')


class Deck:
    def __init__(self):
        self.cards = []
        for v in [x.value for x in Value]:
            for c in [x.value for x in Color]:
                self.cards.append(Card(c, v))

    def add(self, cards: list[Card]):
        self.cards = cards + self.cards

    def shuffle(self) -> None:
        # We shuffle the cards
        shuffle(self.cards)

    def cut(self) -> None:
        """
        Cut the deck at a random position
        """
        # The position where the deck is cut
        cut_pos = randint(1, len(self.cards) - 1)
        # The deck is cut then stacked again
        self.cards = self.cards[cut_pos:] + self.cards[:cut_pos]

    def deal(self, nb_cards: int) -> Card | list[Card]:
        """
        Deal a specific number of cards from the top of the deck
        """
        cards = []
        for _ in range(0, nb_cards):
            cards.append(self.cards.pop(0))
        return cards
    

class Pile:
    def __init__(self):
        """
        Class representing a pile of already played cards
        """
        self.cards = []

    def add(self, cards: list[Card]) -> None:
        """
        Add cards to the pile
        :param cards: list of Cards to add to the pile
        """
        self.cards = cards + self.cards

    def pop_all(self) -> list[Card]:
        """
        Pop all cards from the pile
        """
        cards = self.cards
        self.cards = []
        return cards
    

class Team:
    def __init__(self, name):
        """
        Class representing a team of players
        """
        self.name = name
        self.score = 0
        self.points = 0
    

class Player:
    def __init__(self, name: str, team: Team):
        """
        Class representing a player of the game
        :param name: name of the player
        """
        self.is_human = True
        self.name = name
        self.team = team
        self.hand = [None] * 8
        self.top_hand_index = 7
    
    def add_cards(self, cards: list[Card]) -> None:
        """
        Add some cards to the payers's hand
        :param cards: list of cards to add
        """
        for card in cards:
            self.hand[self.top_hand_index] = card
            self.top_hand_index -= 1

    def try_card(self, _1, _2):
        print(
            "Your cards are:\n" + "\n".join(
                [str(index + 1) + ' -> ' + card.value + ' of ' + card.color if card is not None else "EMPTY" for index, card in enumerate(self.hand)]
            ) + '\n'
        )
        card_index = int(input("Please enter the position of the card you want to play, starting at 1: ")) - 1
        return card_index
    
    def play_card(self, card_index: int) -> Card:
        """
        Play a card from the player's hand
        :param card_index: the position of the card to play
        :return: the requested card
        """
        # We get the value of the card and replace it to None in the cards
        card = self.hand[card_index]
        self.hand[card_index] = None
        # If the hand is empty, we reset the top_hand_index
        if all([c is None for c in self.hand]):
            self.top_hand_index = 7
        return card
    
    def bid(self, _):
        """
        Create a bid
        """
        print(
            "Your cards are:\n" + "\n".join(
                [str(index + 1) + ' -> ' + card.value + ' of ' + card.color for index, card in enumerate(self.hand)]
            ) + "\n"
        )
        bid_value = input("Please enter your bid value, or press Enter: ")
        bid_color = input("Please enter your bid color, or press Enter: ")
        bid_value = None if bid_value == "" else int(bid_value)
        bid_color = None if bid_color == "" else bid_color

        if bid_value is None and bid_color is None:
            is_coinched = int(input("Please enter 1 if you want to coinche, otherwise 0: "))
        else:
            is_coinched = 0

        if bid_value is None and bid_color is None and not is_coinched:
            is_surcoinched = int(input("Please enter 1 if you want to surcoinche, otherwise 0: "))
        else:
            is_surcoinched = 0

        return bid_value, bid_color, is_coinched, is_surcoinched


class Robolot(Player):
    def __init__(self, name: str, team: Team, smart_mode: bool = False):
        super().__init__(name, team)
        self.is_human = False
        self.smart_mode = smart_mode

    def try_card(self, pli: Pile, memory: pd.DataFrame):
        card_index = randint(0, 7)
        while self.hand[card_index] is None:
            card_index = randint(0, 7)
        return card_index

    def bid(self, memory: pd.DataFrame):
        """
        Create a bid
        """
        if self.smart_mode:
            raise NotImplementedError("Smart mode has not been implemented yet")
        else:
            rdm = (randint(1, 100) / 100)

            # Case 1: it raises the bid
            if rdm <= DUMB_BID_RAISE_PROB:
                current_bid = memory["bid_value"].max()
                all_possible_bid_values = ([x * 10 for x in range(8, 17)] + [250, 500])

                # We choose the bid value and color randomly in the possible values
                if pd.isnull(current_bid):
                    bid_value = choice(all_possible_bid_values)
                    bid_color = choice(list(Color)).value
                # We cannot exceed the bid limit
                elif current_bid == 500:
                    bid_value = None
                    bid_color = None
                else:
                    bid_value = choice([x for x in all_possible_bid_values if x > current_bid])
                    bid_color = choice(list(Color)).value
                
                return bid_value, bid_color, 0, 0

            # Case 2: it coinches
            elif rdm <= DUMB_BID_RAISE_PROB + DUMB_COINCHE_PROB:
                return None, None, 1, 0

            # Case 3: it surcoinches
            elif rdm <= DUMB_BID_RAISE_PROB + DUMB_COINCHE_PROB + DUMB_SURCOINCHE_PROB:
                return None, None, 0, 1

            # Case 4: it passes
            else:
                return None, None, 0, 0


    