import random

class Qix:

    def __init__(self, image):
        self.img = image
        self.half = 50//2  # HALF SIZE

        self.x = random.randrange(100, 700, 1)  # INITIAL POSITION : RANDOM
        self.y = random.randrange(100, 700, 1)
        self.speed = 1

        self.target = self.x, self.y  # INITIAL TARGET (Reached)

    # GRAPHIC METHODS #

    def draw(self, screen, border):
        """
        Moves Qix toward target and draws it on the screen.
        """
        # CHANGE TARGET IF REACHED OR IF TARGET NO LONGER IN BOUNDS
        if self.target == (self.x, self.y) or not border.is_valid_move(self.target[0], self.target[1]):
            self.choose_target(border)

        # HORIZONTAL SHIFT
        if self.target[0] > self.x:
            self.x += self.speed
        elif self.target[0] < self.x:
            self.x -=  self.speed
        screen.blit(self.img, (self.x - self.half, self.y - self.half))

        # VERTICAL SHIFT TOWARD TARGET
        if self.target[1] > self.y:
            self.y += self.speed
        elif self.target[1] < self.y:
            self.y -= self.speed
        screen.blit(self.img, (self.x - self.half, self.y - self.half))

    def choose_target(self, border, teleport=False):
        """
        Changes the Qix' target location.
        """
        self.target = border.get_valid_position()
        if teleport:
            self.x, self.y = self.target

class Sparx:
    
    def __init__(self, image):
        self.img = image
        self.half = 50//2   # PNG DIMENSIONS

        self.x = 400   # INITIAL POSITION : TOP CENTER
        self.y = 100
        self.speed = 1

        self.teleport = False   # FORCE TELEPORT

    def draw(self, screen, border):
        """
        Moves Sparc as needed and draws it on the screen.
        """
        if self.teleport:
            self.teleport = False
            self.x, self.y = border.get_valid_position_sparx()
        else:
            self.x, self.y = border.get_next_sparx_position(self.x, self.y)
        screen.blit(self.img, (self.x - self.half, self.y - self.half))

    def teleport_me(self):
        """
        Allows Sparc to be teleported (ex. if the edge it is traversing has become invalid)
        """
        self.teleport = True

