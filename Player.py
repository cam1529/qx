import pygame
from copy import deepcopy
from Line import Trail, Line
from Graphic import Colour


class Player:
    def __init__(self, image):
        self.img = image
        self.img_hit = pygame.image.load("icon01.png")
        self.half = 50//2   # PNG DIMENSIONS

        self.lives = 3      # HEALTH POINTS
        self.speed = 2

        self.x = 400        # INITIAL POSITION : BOTTOM CENTER
        self.y = 700
        self.change_horizontal = 0
        self.change_vertical = 0
        self.dir = ""
        self.trail = Trail()
        self.trail.add_endpoint((self.x, self.y))

        self.force_teleport = False
        self.is_hit = 0

    # ACCESSORS #

    def is_dead(self):
        return self.lives <= 0

    def get_trail(self):
        return self.trail

    def get_lives_str(self):
        return 'v'*self.lives

    # MAIN METHODS #

    def get_move(self):
        """
        Read and process user input
        :return: False to quit game
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:          # CLICK 'X' - QUIT
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:       # 'UP' - MOVE UP
                    self.change_up()
                elif event.key == pygame.K_DOWN:   # 'DOWN' - MOVE DOWN
                    self.change_down()
                elif event.key == pygame.K_RIGHT:  # 'RIGHT' - MOVE RIGHT
                    self.change_right()
                elif event.key == pygame.K_LEFT:   # 'LEFT' - MOVE LEFT
                    self.change_left()
                elif event.key == pygame.K_SPACE:  # 'SPACE' - TELEPORT TO RANDOM PART OF THE SCREEN
                    self.teleport()
                elif event.key == pygame.K_q:      # 'Q' - QUIT
                    return False
            if event.type == pygame.KEYUP:         # NO INPUT - STOP
                self.stop()
        return True

    def update_xy(self, border):
        """
        Updates player's x and y coordinate.
        :param border: Border object
        :return: True if player's x and y were updated/modified; False if they are the same
        """
        if self.force_teleport: # 1. CHECK FOR FORCED TELEPORT MOVEMENT (if user presses <SPACE>)
            self.force_teleport = False
            self.x, self.y = border.get_valid_position(20)
            return True

        if self.change_horizontal == 0 and self.change_vertical == 0:  # 2. CHECK FOR NO UPDATE NEEDED
            return False

        new_x = self.x + self.change_horizontal  # 3. ASSIGN UPDATES TO TEMPORARY VARIABLES
        new_y = self.y + self.change_vertical

        if border.is_valid_move(new_x, new_y):  # 4. CHECK THAT UPDATE IS VALID (within borders)
            self.x = new_x                      # 5. UPDATE INSTANCE VARIABLES
            self.y = new_y

            # 5a. CHECK FOR INVALID TRAIL (does not start on the borders)
            if not self.trail.is_empty():
                if border.is_valid_move(self.trail.get_first_point()[0], self.trail.get_first_point()[1], -1):
                    self.trail.empty_trail()
                    self.trail.add_endpoint((self.x, self.y))
                    self.dir = ""
                    return True

            # 5b. CHECK IF USER IS ON ONE OF THE EDGES -> TRY TO ADD TRAIL TO EDGES
            if border.is_on_the_edges(self.x, self.y):
                border.add_poly(self.trail, (self.x, self.y))
                self.dir = ""
                return True

            # 5c. CHECK FOR BACKTRACKING (current xy overlaps prev trail xy)
            if self.trail.contains(self.x, self.y):
                self.trail.backtrack_to_line_with(self.x, self.y)
            return True
        return False

    # ENEMY-RELATED METHODS #

    def check_collision(self, enemy, border, isSparc = False):
        """
        Checks if enemy has collided with the player or the player's trail.
        :param enemy: Qix or Sparx object
        :param border:
        :param isSparc: True if enemy is a Sparc
        :return:
        """
        # Part 1: CHECK FOR TRAIL COLLISION
        if self.check_trail_collision(enemy.x, enemy.y, isSparc):
            return True

        # PART 2: CHECK FOR DIRECT COLLISION
        epsilon = 25
        if abs(enemy.x - self.x) <= epsilon and abs(enemy.y - self.y) <= epsilon:
            if isSparc:
                enemy.teleport_me()
            else:   # is Qix
                enemy.choose_target(border, True)
            pygame.time.delay(300)
            self.reset_pos(not isSparc)
            return True
        return False

    def check_trail_collision(self, enemy_x, enemy_y, isSparc=False):
        """
        Checks if the enemy has collided with the player's trail.
        :param enemy_x: x position
        :param enemy_y: y position
        :param isSparc: False if enemy is a Qix object
        :return:
        """
        if self.trail.is_empty():  # Trail is empty -> Collision is impossible
            return False

        # Part 1: CREATE NEW TRAIL THAT CONSIDERS THE LINE THAT THE PLAYER IS CURRENTLY MAKING
        current_trail = Trail()
        if len(self.trail) == 1:  # ---> Create current Line
            current_line = Line(self.trail.get_first_point(), (self.x, self.y))
        else:
            current_line = Line(self.trail.get_last_line().endpoint1, (self.x, self.y))
        current_trail.lines = self.trail.get_lines()[:-1] + [current_line]  # ---> Add modified lines to new trail

        # Part 2: CHECK FOR TRAIL COLLISION
        if current_trail.contains(enemy_x, enemy_y, 25, False):
            if isSparc:
                pygame.time.delay(200)
                self.reset_pos(False)
            else:  # is Qix
                self.reset_pos(True, False)
            return True
        return False

    def reset_pos(self, isQix=True, lose_life=True):
        """
        Handles player object after a collision - resets position, empties trail, decreases life, etc.
        :param isQix: True if this function is called after a Qix collision; False if after a Sparc collision
        :param lose_life: False if player does not lose a life after the collision (ex. after Qix hits the trail)
        :return:
        """
        new_start_point = None
        if isQix:
            try:
                new_start_point = deepcopy(self.trail.get_first_point())
                self.x = new_start_point[0]
                self.y = new_start_point[1]
            except:    # Invalid trail (ex. empty)
                pass
        self.trail.empty_trail()
        if new_start_point is not None:
            self.trail.add_endpoint(new_start_point)
        if lose_life:
            self.lives -= 1

    # HELPER METHODS #

    def teleport(self):
        self.dir = ""
        self.trail.empty_trail()
        self.stop()
        self.force_teleport = True

    def change_left(self):
        if self.dir != "HOR":
            self.trail.add_endpoint((self.x, self.y))
        self.dir = "HOR"
        self.change_horizontal = -self.speed
        self.change_vertical = 0

    def change_right(self):
        if self.dir != "HOR":
            self.trail.add_endpoint((self.x, self.y))
        self.dir = "HOR"
        self.change_horizontal = self.speed
        self.change_vertical = 0

    def change_up(self):
        if self.dir != "VER":
            self.trail.add_endpoint((self.x, self.y))
        self.dir = "VER"
        self.change_vertical = -self.speed
        self.change_horizontal = 0

    def change_down(self):
        if self.dir != "VER":
            self.trail.add_endpoint((self.x, self.y))
        self.dir = "VER"
        self.change_vertical = self.speed
        self.change_horizontal = 0

    def stop(self):
        self.change_horizontal = 0
        self.change_vertical = 0

    # GRAPHIC METHODS #

    def draw(self, screen, is_hit = False):
        """
        Draws player object on the screen.
        :param is_hit: True if player has just experienced a collision
        """
        if is_hit:
            self.is_hit = 301    # Will display alternate image for 300 milliseconds
        if self.is_hit > 0:
            self.is_hit -= 1
            screen.blit(self.img_hit, (self.x - self.half, self.y - self.half))
        else:
            screen.blit(self.img, (self.x - self.half, self.y - self.half))

    def display_lives(self, screen, font):
        """
        Displays number of lives at the top-right corner of the game screen.
        """
        lives_text = font.render(self.get_lives_str(), True, Colour.pink, Colour.black)
        lives_text_rect = lives_text.get_rect()
        lives_text_rect.midright = (700, 50)
        screen.blit(lives_text, lives_text_rect)