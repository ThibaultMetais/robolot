from enum import Enum
from random import randint, sample
import datetime

import pandas as pd

from robolot.models import Team, Player, Robolot, Deck, Pile, Value, Color, Card, CARD_POINTS, TRUMP_CARD_POINTS


class GameState(Enum):
    PLAYING = 0
    BIDDING = 1
    BETWEEN_ROUNDS = 2
    ENDED = 3
    BIDDING_READY = 4
    PLAYING_READY = 5


class CoincheEngine:
    def __init__(self, auto_fill: bool = True, target_score = 1000):
        """
        Engine of the game
        :param auto_fill: whether we want to automatically set the player and team names
        """
        # We set the teams and players
        self.teams = []
        self.players = []

        # We define the target score
        self.target_score = target_score

        # We setup the robots in a way that maximizes the number of human-robot interaction
        nb_robots = int(input(f"Enter the number of robots: "))
        robot_map = sample(range(4), nb_robots)

        for i in range(0, 4):
            if auto_fill:
                player_name = f"player{i + 1}"
            else:
                player_name = input(f"Enter the name of player{i + 1}: ")
            if i < 2:
                if auto_fill:
                    player_team_name = f"team{i + 1}"
                else:
                    player_team_name = input(f"Enter the team name for {player_name}: ")
                player_team = Team(player_team_name)

                if i in robot_map:
                    self.players.append(Robolot(player_name, player_team))
                else:
                    self.players.append(Player(player_name, player_team))

                self.teams.append(player_team)
            else:
                if i in robot_map:
                    self.players.append(Robolot(player_name, self.teams[i%2]))
                else:
                    self.players.append(Player(player_name, self.teams[i%2]))
        # We setup the cards
        self.deck = Deck()
        self.deck.shuffle()
        self.piles = [Pile(), Pile()]
        self.deal()
        self.pli = Pile()
        # We start the biddind phase
        self.starting_player_index = 0
        self.state = GameState.BIDDING_READY

    def _deal_round(self, nb_cards: int):
        """
        Distribute a given number of cards to each player around the table
        :param nb_cards: the number of cards to distribute to each player
        """
        # We iterate over the players
        for player in self.players:
            # We deal the given number of cards
            player.add_cards(self.deck.deal(nb_cards))
    
    def deal(self):
        """
        Distribute the cards between the players
        """
        # Decide when we will distribute 2 cards instead of 3
        # Example: method = 1 corresponds to 2, 3, 3 dealing method
        method = randint(1, 3)
        # We distribute the cards in 4 lists, one for each player
        for step in range(0, 3):
            # Step with two cards
            if method == (step + 1):
                self._deal_round(2)
            # Step with three cards
            else:
                self._deal_round(3)

    def _get_belotte_points(self):
        for player in self.players:
            if player.team.name == self.bidding_team.name:
                if (
                    any([(card.value == Value.KING and card.color == self.bid_color) for card in player.hand])
                    and any([(card.value == Value.QUEEN and card.color == self.bid_color) for card in player.hand])
                ):
                    return 20
        return 0

    @staticmethod
    def _check_bid_validity(
        memory: pd.DataFrame,
        player_bid_value: int,
        player_bid_color: Color,
        has_coinched: int,
        has_surcoinched: int
    ):            
        if has_coinched == 1:
            # If the player does a coinche, other fields must be None and surcoinche must be 0
            if player_bid_value or player_bid_color or has_surcoinched == 1:
                print("When doing a coinche, no other value can be defined")
                return False
            # If the player does a coinche, a previous bid must be available
            if pd.isnull(memory["bid_value"].max()):
                print("When doing a coinche, a previous bid must be available")
                return False
            # The coinche must not be done by the team with the highest bid
            if memory.shape[0] > 0:
                highest_bid_team_index = memory.sort_values(by=["bid_value"], ascending=False)["team_index"].values[0]
                if highest_bid_team_index != memory["team_index"].values[-1]:
                    print("The coinche must not be done by the team with the highest bid")
                    return False
            else:
                print("There must be a previous bid in order to coinche")
            # A coinche must not be done twice
            is_coinched = memory["has_coinched"].max()
            if not pd.isnull(is_coinched) and is_coinched == 1:
                print("A coinche must not be done twice")
                return False
            
        elif has_surcoinched == 1:
            # If the player does a surcoinche, other fields must be None and coinche must be 0
            if player_bid_value or player_bid_color or has_coinched or has_coinched == 1:
                print("When doing a surcoinche, no other value can be defined")
                return False
            # If the player does a surcoinche, a previous coinche must be available
            is_coinched = memory["has_coinched"].max()
            if pd.isnull(is_coinched) or is_coinched == 0:
                print("When doing a surcoinche, a previous coinche must be available")
                return False
            # The surcoinche must not be done by the team who coinched
            if memory.shape[0] > 0:
                highest_bid_team_index = memory.sort_values(by=["bid_value"], ascending=False)["team_index"].values[0]
                if highest_bid_team_index == memory["team_index"].values[-1]:
                    print("The surcoinche must be done by the team with the highest bid")
                    return False
            # The surcoinche must not be done twice
            is_surcoinched = memory["has_surcoinched"].max()
            if not pd.isnull(is_surcoinched) and is_surcoinched == 1:
                print("A surcoinche must not be done twice")
                return False

        else: 
            previous_bid = memory["bid_value"].max()

            if not player_bid_value or not player_bid_color:
                if (player_bid_value or player_bid_color):
                    print("If the player passes, both value and color must be empty")
                    return False

            # The bid has to be a valid value
            elif player_bid_value not in ([x * 10 for x in range(8, 17)] + [250, 500]):
                print("The bid has to be a valid value")
                return False
            
            # The bid has to be higher than the previous ones
            elif not pd.isnull(previous_bid):
                if player_bid_value <= previous_bid:
                    print("The bid has to be higher than the previous ones")
                    return False
            
        # Otherwise, it is a valid bid
        return True
    
    def start_bidding(self):
        # Setting up bidding variables
        self.is_bidding_closed = False
        self.bid_value = None
        self.bid_color = None
        self.bidding_team = None
        self.is_coinched = 0
        self.is_surcoinched = 0
        self.bidder_index = None
        self.pli_winners_memory = []
        self.current_player_index = self.starting_player_index
        self.bid_memory = pd.DataFrame(columns=["player_index", "team_index", "bid_value", "bid_color", "has_coinched", "has_surcoinched"])
        self.state = GameState.BIDDING
        return ["Starting bidding phase:", f"{self.players[self.current_player_index].name} has to bid"]

    def bid(
            self,
            player_bid_value,
            player_bid_color,
            has_coinched,
            has_surcoinched
        ):
        # We check whether the bid is valid
        is_bid_valid = self._check_bid_validity(
            self.bid_memory,
            player_bid_value,
            player_bid_color,
            has_coinched,
            has_surcoinched
        )
        if not is_bid_valid:
            return ["Your bid is unvalid, please try again"]
        # We add his bid to the memory
        self.bid_memory = pd.concat([
            self.bid_memory,
            pd.DataFrame({
                "player_index": [self.current_player_index],
                "team_index": [self.current_player_index % 2],
                "bid_value": [player_bid_value],
                "bid_color": [player_bid_color],
                "has_coinched": [has_coinched],
                "has_surcoinched": [has_surcoinched]
            })
        ], ignore_index=True, axis=0)
        # If the player raised the bid, we update the current bid
        if player_bid_value:
            self.bid_value = player_bid_value
            self.bid_color = player_bid_color
            self.bidding_team = self.players[self.current_player_index].team
            self.challenger_team = self.teams[(self.current_player_index + 1) % 2]
            self.bidder_index = self.current_player_index
        # If the player has surcoinched, we indicate it
        elif has_surcoinched:
            self.is_surcoinched = 1
            self.is_bidding_closed = True
        # If the player has coinched, we indicate it
        elif has_coinched:
            self.is_coinched = 1
            self.bidder_index = self.current_player_index

        # We build the return message with the necessary information
        message = []
        if has_coinched:
            message.append(f"{self.players[self.current_player_index].name} has coinched")
        elif has_surcoinched:
            message.append(f"{self.players[self.current_player_index].name} has surcoinched")
        elif player_bid_value is None:
            message.append(f"{self.players[self.current_player_index].name} passed")
        else:
            message.append(f"{self.players[self.current_player_index].name} bid: {player_bid_value} of {player_bid_color}")
            
        # We iterate over the players
        self.current_player_index += 1
        # If we arrive at the end of the players, we start again from the beginning
        if self.current_player_index == 4:
            self.current_player_index = 0
        # If there is no bidder and we are at the end of the table, this round is cancelled
        if self.bidder_index is None and self.current_player_index == self.starting_player_index:
            self.is_bidding_closed = True
            # We get beck the cards from the players and put them in a pile
            # The pile inquestion does not matter since it will be collected right after
            cards = []
            for player in self.players:
                cards += player.hand
                player.hand = [None] * 8
                player.top_hand_index = 7
            self.piles[0].add(cards)
            # We export the memory
            ts = str(datetime.datetime.now()).replace(" ", "_")
            self.bid_memory.to_parquet(f"memory/bid_{ts}.parquet")
            pd.DataFrame(columns=["player_index", "card_value", "card_color"]).to_parquet(f"memory/play_{ts}.parquet")
            pd.DataFrame({
                "team_index": [0, 1],
                "points": [0, 0]
            }).to_parquet(f"memory/result_{ts}.parquet")
            self.state = GameState.BETWEEN_ROUNDS
            message.append("This round is cancelled, everyone passed")
            return message
        # If the selected player is the current highest bidder, the bidding phase is over
        if self.bidder_index is not None and self.current_player_index == self.bidder_index:
            self.is_bidding_closed = True
        
        # We add the winning contract info if the bidding phase is over
        if self.is_bidding_closed:
            # We calculate whether or not the bidding team has a belotte
            self.belotte_points = self._get_belotte_points()
            message.append(f"This round is starting with a contract of")
            message.append(f"{self.bid_value} of {self.bid_color} for {self.bidding_team.name}")
            if self.is_coinched:
                message.append("The contract has been coinched")
            if self.is_surcoinched:
                message.append("The contract has been surcoinched")
            self.state = GameState.PLAYING_READY
        else:
            message.append(f"{self.players[self.current_player_index].name} has to bid")
        
        return message
            
    def between_rounds(self):
        """
        Prepare the game before starting a new round 
        """
        # We change the starting player
        self.starting_player_index += 1
        if self.starting_player_index > 3:
            self.starting_player_index = 0
        # We recreate the deck from the piles
        cards = []
        for pile in self.piles:
            cards += pile.pop_all()
        self.deck.add(cards)
        # We cut it
        self.deck.cut()
        # We deal the cards
        self.deal()
        self.pli_winners_memory = []
        self.state = GameState.BIDDING_READY

    def _get_pli_info(self):
        pli_points = 0
        highest_card_index = None
        highest_card_level = None
        is_highest_card_trump = None
        card_index = 0
        for card in list(reversed(self.pli.cards)):
            # We determine it is a trump card
            is_card_trump = card.color == self.bid_color
            # We get the corresponding card points
            if is_card_trump:
                card_level = list(TRUMP_CARD_POINTS).index(card.value)
            else:
                card_level = list(CARD_POINTS).index(card.value)
            if highest_card_index is None:
                asked_color = card.color
                highest_card_index = card_index
                highest_card_level = card_level
                is_highest_card_trump = is_card_trump
            else:
                if (
                    # Both are trump cards and the current card is stronger
                    (is_card_trump and is_highest_card_trump and card_level > highest_card_level)
                    # Both are not trump cards and the current card is stronger
                    or (not is_card_trump and not is_highest_card_trump and card.color == asked_color and card_level > highest_card_level)
                    # The current card is a trump one but not the highest card so far is not
                    or (is_card_trump and not is_highest_card_trump)
                ):
                    highest_card_index = card_index
                    highest_card_level = card_level
            # We add the card value to the pli points
            if is_card_trump:
                pli_points += TRUMP_CARD_POINTS[card.value]
            else:
                pli_points += CARD_POINTS[card.value]
            card_index += 1
        # We determine the team that played the winning card
        winning_player_index = (self.current_player_index + highest_card_index) % 4
        winning_team_index = (self.current_player_index + highest_card_index) % 2
        return winning_player_index, winning_team_index, pli_points
    
    def _check_card_validity(self, hand: list[Card], card: Card):
        """
        Check if the card can be played
        """
        # If it is not the first card played
        if len(self.pli.cards) > 0:
            asked_color = self.pli.cards[-1].color
            # If the player have the asked color in his hand, he has to play it
            if (
                any([c.color == asked_color for c in hand if c is not None])
                and card.color != asked_color
            ):
                print("You must play the asked color if you can")
                return False
            # If the player plays a trump card, it must be higher than the previous trump cards if possible
            if card.color == self.bid_color:
                trump_cards_pli = [c.value for c in self.pli.cards if c.color == self.bid_color]
                if len(trump_cards_pli) > 0:
                    highest_level_trump_card_pli = max([
                        list(TRUMP_CARD_POINTS).index(c.value) for c in self.pli.cards if c.color == self.bid_color
                    ])
                    highest_level_trump_card_hand = max([
                        list(TRUMP_CARD_POINTS).index(c.value) for c in [
                            x for x in hand if x is not None
                        ] if c.color == self.bid_color
                    ])
                    if (
                        list(TRUMP_CARD_POINTS).index(card.value) < highest_level_trump_card_pli
                        and highest_level_trump_card_hand > highest_level_trump_card_pli
                    ):
                        print("If you play a trump card, it should be higher than previous trump cards if possible")
                        return False
            # If the player has a trump card and no cards with the asked color, he has to play it
            # unless his partner is winning the pli
            if (
                all([c.color != asked_color for c in hand if c is not None])
                and card.color != self.bid_color
                and any([c.color == self.bid_color for c in hand if c is not None])
                and (
                    len(self.pli.cards) <= 2
                    or self.players[self.current_player_index].team != self.teams[self._get_pli_info()[1]])
            ):
                print(
                    "You have to play a trump card if you do not have the asked color, "
                    "unless your partner is winning the pli"
                )
                return False
        return True
    
    def start_playing(self):
        self.current_player_index = self.starting_player_index
        self.pli_counter = 0
        self.play_memory = pd.DataFrame(columns=["player_index", "card_value", "card_color"])
        self.state = GameState.PLAYING
        return [f"{self.players[self.current_player_index].name} has to play"]

    def play(self, card_index: int):
        # We ask the player to play until his card is valid
        is_card_valid = self._check_card_validity(
            self.players[self.current_player_index].hand,
            self.players[self.current_player_index].hand[card_index]
        )
        if not is_card_valid:
            return ["Your card is unvalid, please try again"]
        
        # When the card is valid, it is played
        played_card = self.players[self.current_player_index].play_card(card_index)
        self.pli.add([played_card])
        print(f"> {self.players[self.current_player_index].name} played a {played_card.value} of {played_card.color}\n")
        self.play_memory = pd.concat([
            self.play_memory,
            pd.DataFrame({
                "player_index": [self.current_player_index],
                "card_value": [played_card.value],
                "card_color": [played_card.color]
            })
        ], ignore_index=True, axis=0)

        # We change players
        self.current_player_index += 1
        if self.current_player_index == 4:
            self.current_player_index = 0

        message = []
        
        # When the pli is complete, it is added to the winning team pile and the points calculated
        if len(self.pli.cards) == 4:
            winning_player_index, winning_team_index, pli_points = self._get_pli_info()
            self.pli_winners_memory.append(winning_player_index)
            self.teams[winning_team_index].points += pli_points
            self.piles[winning_team_index].add(self.pli.pop_all())
            self.pli_counter += 1
            self.current_player_index = winning_player_index
            message.append(f"{self.players[winning_player_index].name} won the pli")
            message.append(f"for {self.teams[winning_team_index].name}")

            # When the round is complete, we determine the winner and distribute the points
            if self.pli_counter == 8:
                contract_fullfilled = False
                # If a generale has been announced
                if self.bid_value == 500:
                    if all([x == self.bidder_index for x in self.pli_winners_memory]):
                        contract_fullfilled = True
                # If a capot has been announced
                elif self.bid_value == 250:
                    if self.challenger_team.points == 0:
                        contract_fullfilled = True                        
                # Other contracts
                elif self.bidding_team.points + self.belotte_points >= self.bid_value:
                    contract_fullfilled = True
                
                if contract_fullfilled:
                    self.bidding_team.score += self.bid_value
                    message.append("The contract has been fullfilled")
                    message.append(f"{self.bid_value} points won by the team {self.bidding_team.name}")
                else:
                    self.challenger_team.score += self.bid_value
                    message.append("The contract has been failed")
                    message.append(f"{self.bid_value} points won by the team {self.challenger_team.name}")

                # We export the game memory
                ts = str(datetime.datetime.now()).replace(" ", "_")
                self.bid_memory.to_parquet(f"memory/bid_{ts}.parquet")
                self.play_memory.to_parquet(f"memory/play_{ts}.parquet")
                if (
                    (contract_fullfilled and self.bidding_team.name == self.teams[0].name)
                    or (not contract_fullfilled and self.bidding_team.name == self.teams[1].name)
                ):
                    pd.DataFrame({
                        "team_index": [0, 1],
                        "points": [self.bid_value, -self.bid_value]
                    }).to_parquet(f"memory/result_{ts}.parquet")
                else:
                    pd.DataFrame({
                        "team_index": [0, 1],
                        "points": [-self.bid_value, self.bid_value]
                    }).to_parquet(f"memory/result_{ts}.parquet")
                
                # We reset the point counters for each team
                for team in self.teams:
                    team.points = 0

                # We check if there is a winner
                for team in self.teams:
                    if team.score >= self.target_score:
                        message.append(f"Team {team.name} wins with a score of {team.score} !")
                        self.state = GameState.ENDED

                # Otherwise, we start another round
                if self.state != GameState.ENDED:
                    message.append("End of round, preparing next round")
                    self.state = GameState.BETWEEN_ROUNDS
        else:
            message.append(f"{self.players[self.current_player_index].name} has to play")

        return message

