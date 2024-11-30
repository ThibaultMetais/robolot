import pygame

from robolot.models import Card
from robolot.engine import CoincheEngine, GameState


FAST_PLAY = True
TARGET_SCORE = 1000
BASE_CARDBACK = pygame.image.load('images/back_card.png')
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')


def blitRotateCenter(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect)


def render_pli(cards: list[Card]):
    for i in range(0, len(cards)):
        window.blit(
           pygame.transform.scale(cards[len(cards) - (i + 1)].image, (int(238*0.5), int(332*0.5))),
           (375 + i * 50, 300)
        )


def render_player(cards: list[Card], x, y, angle, display_indicators):
    if angle == 90:
       vertical = -1
       horizontal = 0
       padding_card_indicators = -60
    elif angle == 180:
       vertical = 0
       horizontal = -1
       padding_card_indicators = 175
    elif angle == 270:
       vertical = 1
       horizontal = 0
       padding_card_indicators = 150
    else:
       vertical = 0
       horizontal = 1
       padding_card_indicators = -40

    for i in range(0, 8):
        if cards[7 - i] is not None:
            blitRotateCenter(
                window,
                pygame.transform.scale(cards[7 - i].image, (int(238*0.5), int(332*0.5))),
                (x - i * 50 * horizontal, y - i * 50 * vertical),
                angle
            )
            if display_indicators:
                blitRotateCenter(
                    window,
                    pygame.transform.scale(
                        pygame.image.load(f"images/{8-i}.png"),
                        (int(30), int(30))
                    ),
                    (
                        x + 50 * abs(horizontal) + padding_card_indicators * abs(vertical) - i * 50 * horizontal,
                        y + 65 * abs(vertical) + padding_card_indicators * abs(horizontal) - i * 50 * vertical
                    ),
                    angle
                )
   

def renderGame(window, game_engine, message):
    window.fill((39, 174, 96))
    font = pygame.font.SysFont('comicsans',20, True)

    render_pli(game_engine.pli.cards)
    render_player(game_engine.players[0].hand, 625, 575, 0, game_engine.current_player_index==0 and game_engine.state==GameState.PLAYING)
    render_player(game_engine.players[1].hand, 850, 125, 90, game_engine.current_player_index==1 and game_engine.state==GameState.PLAYING)
    render_player(game_engine.players[2].hand, 275, 25, 180, game_engine.current_player_index==2 and game_engine.state==GameState.PLAYING)
    render_player(game_engine.players[3].hand, 50, 475, 270, game_engine.current_player_index==3 and game_engine.state==GameState.PLAYING)

    if message:
        padding = 0
        for sub_message in message:
            text = font.render(sub_message, True, (255,255,255))
            window.blit(text, (300, 250 + padding))
            padding += 30


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.font = pygame.font.Font(None, 32)
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    text = self.text
                    self.text = ''
                    return text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


pygame.init()
bounds = (1024, 768)
window = pygame.display.set_mode(bounds)
pygame.display.set_caption("Robolot")

input_box = None
bid_messages = [
            ["Please enter your bid value, or press Enter: "],
            ["Please enter your bid color, or press Enter: "],
            ["Please enter 1 if you want to coinche, or press Enter: "],
            ["Please enter 1 if you want to surcoinche, or press Enter: "]
        ]
bid_values = [None] * 4
game_engine = CoincheEngine(target_score=TARGET_SCORE)

run = True
while run:
    key = None
    input_value = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            key = event.key
        if input_box:
            input_value = input_box.handle_event(event)

    if input_box:
        input_box.update()
    message = None
    delay_s = 1

    if game_engine.state == GameState.BIDDING_READY:
        message = game_engine.start_bidding()
        delay_s = 3
    elif game_engine.state == GameState.PLAYING_READY:
        message = game_engine.start_playing()
        delay_s = 3
    elif game_engine.state == GameState.BIDDING:
        if not game_engine.players[game_engine.current_player_index].is_human:
            (
                bid_value,
                bid_color,
                is_coinched,
                is_surcoinched
            ) = game_engine.players[game_engine.current_player_index].bid(game_engine.bid_memory)
            message = game_engine.bid(
                bid_value,
                bid_color,
                is_coinched,
                is_surcoinched
            )
            bid_values = [None] * 4
            delay_s = 1
        else:
            for i in range(0, 4):
                if i == 2 and bid_values[0] is not None and bid_values[1] is not None and bid_values[0] != "" and bid_values[1] != "":
                    bid_values[2] = ""
                    bid_values[3] = ""
                    break
                elif i == 3 and bid_values[2] == 1:
                    bid_values[3] = ""
                    break
                elif bid_values[i] is None and not input_box:
                    message = bid_messages[i]
                    input_box = InputBox(300, 300, 140, 32)
                    delay_s = 1
                    break
                elif bid_values[i] is None and input_value is not None:
                    bid_values[i] = input_value
                    input_box = None
                    input_value = None
                    break        

            if all([x is not None for x in bid_values]):
                bid_value = None if bid_values[0] == "" else int(bid_values[0])
                bid_color = None if bid_values[1] == "" else bid_values[1]
                is_coinched = 0 if bid_values[2] == "" else 1
                is_surcoinched = 0 if bid_values[3] == "" else 1

                message = game_engine.bid(
                    bid_value,
                    bid_color,
                    is_coinched,
                    is_surcoinched
                )
                bid_values = [None] * 4
                delay_s = 2
    elif game_engine.state == GameState.PLAYING:
        if not game_engine.players[game_engine.current_player_index].is_human:
            card_index = game_engine.players[game_engine.current_player_index].try_card(game_engine.pli, game_engine.play_memory)
            message = game_engine.play(card_index)
            delay_s = 1
        elif key:
            if key >= 49 and key <= 56:
                message = game_engine.play(key - 49)
                delay_s = 1
    elif game_engine.state == GameState.BETWEEN_ROUNDS:
        game_engine.between_rounds()
    elif game_engine.state == GameState.ENDED:
        pass
    else:
        raise NotImplementedError("This game state doesn't exist")

    renderGame(window, game_engine, message)
    if input_box:
        input_box.draw(window)
    pygame.display.update()
    if message and not FAST_PLAY:
        pygame.time.delay(delay_s * 1000)