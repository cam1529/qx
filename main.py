import pygame
from Border import Border
from Enemy import Qix, Sparx
from Player import Player
from copy import deepcopy

# ============
#   SCREENS
# ============

def start_game():
    draw_screen_image("screen000.png")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True, False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return True, True
    return False, True

def run_game_level(level):
    clock = pygame.time.Clock()
    screen.fill((0, 0, 0))
    running = True

    if player.is_dead():       # PLAYER DIED
        return True, running

    if not player.get_move():  # PLAYER PRESSED QUIT
        running = False

    player.update_xy(border)   # DISPLAY UPDATES
    border.draw(screen)
    player.get_trail().draw(screen, (player.x, player.y))
    qix.draw(screen, border)
    if level == 2:             # LEVEL 2 - EXCLUSIVE UPDATES
        sparc.draw(screen, border)
        player.draw(screen, player.check_collision(qix, border) or player.check_collision(sparc, border, True))
    else:                      # LEVEL 1 - EXCLUSIVE UPDATES
        player.draw(screen, player.check_collision(qix, border))

    if player.is_hit == 300 and not player.is_dead():  # COLLISION SOUND EFFECTS
        play_sound("sfx_bad.mp3")
        pygame.time.delay(200)

    player.display_lives(screen, font)
    border.display_score(screen, font)

    pygame.display.update()
    clock.tick(10000)
    return False, running

def end_game_(image_name):
    draw_screen_image(image_name)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True

# ===================
#   PYGAME HELPERS
# ===================

def draw_screen_image(image_name):
    image = pygame.image.load(image_name)
    image = pygame.transform.scale(image, (800, 800))
    screen.blit(image, (0, 0))
    pygame.display.update()

def play_sound(sound_name):
    pygame.mixer.music.load(sound_name)
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play()

# ===================
#   INITIALIZATION
# ===================

pygame.init()
pygame.mixer.init()

# GLOBAl VARIABLES
screen = pygame.display.set_mode((800, 800))
font = pygame.font.Font('slkscrb.ttf', 40)
player_image = pygame.image.load("icon00.png")
qix_image = pygame.image.load("icon10.png")
sparc_image = pygame.image.load("icon20.png")

player = Player(player_image)
border = Border()
qix = Qix(qix_image)
sparc = Sparx(sparc_image)
level = 1

game_start = False
running_end = False
game_over = False
running = True

# =============================
#   MAIN FUNCTION STARTS HERE
# =============================

while running:
    # START SCREEN
    if not game_start:
        game_start, running = start_game()

    # GAME SCREEN
    elif game_start and not game_over:

        if level == 2 and int(border.get_score()) > 75:     # WIN GAME
            running = False
            running_end = True

        elif int(border.get_score()) > 75 and level != 2:   # LEVEL UP
            play_sound("sfx_good.mp3")
            level = 2
            draw_screen_image("screen001.png")
            pygame.time.delay(1000)
            player.x, player.y = 400, 700                    # Reset
            border.edge_points = deepcopy(border.init_grid)  # Reset
            game_over, running = run_game_level(level)

        else:
            game_over, running = run_game_level(level)

    # GAME OVER SCREEN
    elif game_over:
        running_end = True
        running = False

if not game_over:  # DISPLAY WIN SCREEN
    play_sound("sfx_win.mp3")
    while running_end:
        running_end = end_game_("screen002.png")

else:  # DISPLAY LOSE SCREEN
    play_sound("sfx_bad.mp3")
    while running_end:
        running_end = end_game_("screen003.png")

