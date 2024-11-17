import music
import pgzrun
from random import randint
from pgzero.builtins import Actor
import pygame

# screen dimensions and center points
WIDTH = 800
HEIGHT = 600
CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2

# game variables
player_scores = [0, 0]
current_move = 0
current_player = 0  # 0 for Player 1, 1 for Player 2
count = 4
dance_length = 4
say_dance = False
show_countdown = False
game_over = False
dot_color_toggle = True
turn_displayed = True
play_again_box_displayed = False
winner_message = ""

# animations
heart_scale = 1.0
heart_growing = True

# dancer and controls
dancer = Actor("dancer-start", (CENTER_X, CENTER_Y - 40))
up = Actor("up", (CENTER_X, CENTER_Y + 110))
right = Actor("right", (CENTER_X + 60, CENTER_Y + 170))
down = Actor("down", (CENTER_X, CENTER_Y + 230))
left = Actor("left", (CENTER_X - 60, CENTER_Y + 170))

# dot positions for blinking hearts
left_heart_dot_positions = [
    (CENTER_X - 250 - 20, CENTER_Y - 130),
    (CENTER_X - 250 + 120, CENTER_Y - 130),
    (CENTER_X - 250 - 20, CENTER_Y - 70),
    (CENTER_X - 250 + 120, CENTER_Y - 70),
]
right_heart_dot_positions = [
    (CENTER_X + 150 - 20, CENTER_Y - 130),
    (CENTER_X + 150 + 120, CENTER_Y - 130),
    (CENTER_X + 150 - 20, CENTER_Y - 70),
    (CENTER_X + 150 + 120, CENTER_Y - 70),
]

# heart settings
square_width, square_height = 100, 100

# sequences
move_list = []
display_list = []

# button positions for "Play Again?" box
yes_button = Rect((CENTER_X - 90, CENTER_Y + 50), (80, 40))
no_button = Rect((CENTER_X + 10, CENTER_Y + 50), (80, 40))


def generate_moves():
    """Generate dance moves."""
    global move_list, display_list, count, say_dance, current_move, show_countdown, turn_displayed
    count = 4
    move_list = [randint(0, 3) for _ in range(dance_length)]
    display_list = move_list[:]
    current_move = 0
    say_dance = False
    show_countdown = True
    turn_displayed = True
    countdown()


def countdown():
    """Countdown before the dance routine."""
    global count, show_countdown, turn_displayed
    if count > 1:
        count -= 1
        clock.schedule(countdown, 1)
    else:
        count = 0
        show_countdown = False
        turn_displayed = False
        display_moves()


def display_moves():
    """Display the dancer's routine."""
    global display_list, say_dance
    if display_list:
        move = display_list.pop(0)
        update_dancer(move)
        clock.schedule(display_moves, 1)
    else:
        say_dance = True


def update_dancer(move):
    """Update dancer's image based on the move."""
    if move == 0:
        dancer.image = "dancer-up"
        up.image = "up-lit"
    elif move == 1:
        dancer.image = "dancer-right"
        right.image = "right-lit"
    elif move == 2:
        dancer.image = "dancer-down"
        down.image = "down-lit"
    elif move == 3:
        dancer.image = "dancer-left"
        left.image = "left-lit"
    clock.schedule(reset_dancer, 0.5)


def reset_dancer():
    """Reset dancer and arrow images."""
    dancer.image = "dancer-start"
    up.image = "up"
    right.image = "right"
    down.image = "down"
    left.image = "left"


def on_key_up(key):
    """Handle player's input."""
    global current_move, player_scores, current_player, game_over, winner_message
    if game_over or not say_dance:
        return

    if current_move < len(move_list):
        correct_move = (
            (key == keys.UP and move_list[current_move] == 0)
            or (key == keys.RIGHT and move_list[current_move] == 1)
            or (key == keys.DOWN and move_list[current_move] == 2)
            or (key == keys.LEFT and move_list[current_move] == 3)
        )

        if correct_move:
            player_scores[current_player] += 1
            update_dancer(move_list[current_move])
            current_move += 1
        else:
            handle_player_loss()
    elif current_move == len(move_list):
        generate_moves()


def handle_player_loss():
    """Handle when a player loses."""
    global current_player, game_over, winner_message, play_again_box_displayed
    if current_player == 0:
        current_player = 1
        generate_moves()
    else:
        game_over = True
        winner_message = (
            "Player 2 Wins!" if player_scores[1] > player_scores[0] else "Player 1 Wins!"
        )
        clock.schedule(show_play_again_box, 2)


def show_play_again_box():
    """Show the play again box."""
    global play_again_box_displayed
    play_again_box_displayed = True


def draw():
    """Draw the game screen."""
    global show_countdown, say_dance, game_over, turn_displayed, play_again_box_displayed

    screen.clear()
    screen.blit("stage_with_notes_output", (0, 0))
    dancer.draw()
    up.draw()
    right.draw()
    down.draw()
    left.draw()

    screen.draw.text(f"Player 1 Score: {player_scores[0]}", color="black", topleft=(10, 10))
    screen.draw.text(f"Player 2 Score: {player_scores[1]}", color="black", topleft=(10, 40))

    heart_color = (128, 0, 128) if (player_scores[current_player] // 5) % 2 == 1 else (255, 0, 0)
    draw_filled_heart(screen.surface, CENTER_X - 250 + square_width // 2, CENTER_Y - 130, int(40 * heart_scale), heart_color)
    draw_filled_heart(screen.surface, CENTER_X + 150 + square_width // 2, CENTER_Y - 130, int(40 * heart_scale), heart_color)

    dot_color = (0, 0, 255) if dot_color_toggle else (255, 0, 0)
    for pos in left_heart_dot_positions:
        screen.draw.filled_circle(pos, 10, dot_color)
    for pos in right_heart_dot_positions:
        screen.draw.filled_circle(pos, 10, dot_color)

    if turn_displayed:
        screen.draw.filled_rect(Rect((CENTER_X - 150, CENTER_Y - 50), (300, 100)), "white")
        screen.draw.text(f"Player {current_player + 1}'s Turn", color="black", center=(CENTER_X, CENTER_Y), fontsize=40)

    elif not game_over:
        if show_countdown:
            screen.draw.text(str(count), color="black", center=(CENTER_X, 150), fontsize=40)
        elif say_dance:
            screen.draw.text("Dance!", color="black", center=(CENTER_X, 100), fontsize=40)

    if game_over:
        if not play_again_box_displayed:
            screen.draw.filled_rect(Rect((CENTER_X - 150, CENTER_Y - 50), (300, 100)), "white")
            screen.draw.text(winner_message, color="black", center=(CENTER_X, CENTER_Y), fontsize=40)
        else:
            screen.draw.filled_rect(Rect((CENTER_X - 150, CENTER_Y - 50), (300, 100)), "white")
            screen.draw.text("Do you want to play again?", color="black", center=(CENTER_X, CENTER_Y - 10), fontsize=30)
            screen.draw.text("Yes", color="white", center=yes_button.center, fontsize=30)
            screen.draw.text("No", color="white", center=no_button.center, fontsize=30)


def draw_filled_heart(surface, x, y, size, color):
    """Draw a pulsating heart."""
    pygame.draw.circle(surface, color, (x - size // 2, y), size // 2)
    pygame.draw.circle(surface, color, (x + size // 2, y), size // 2)
    pygame.draw.polygon(surface, color, [(x - size, y), (x + size, y), (x, y + size)])


def on_mouse_down(pos):
    """Handle mouse clicks for the play again box."""
    global game_over, play_again_box_displayed, player_scores, current_player
    if game_over and play_again_box_displayed:
        if yes_button.collidepoint(pos):  # Yes
            game_over = False
            play_again_box_displayed = False
            player_scores = [0, 0]
            current_player = 0
            generate_moves()
            music.play("dynamite")
        elif no_button.collidepoint(pos):  # No
            exit()


def update():
    """Update game state for animations."""
    global heart_scale, heart_growing, dot_color_toggle

    if heart_growing:
        heart_scale += 0.02
        if heart_scale >= 1.2:
            heart_growing = False
    else:
        heart_scale -= 0.02
        if heart_scale <= 0.8:
            heart_growing = True

    dot_color_toggle = not dot_color_toggle


# Start the game with music
generate_moves()
music.play("dynamite")  # Play music using the music module
pgzrun.go()
