import pygame
from copy import deepcopy
from shapely.geometry import Polygon, Point
from Line import Trail, Line
from Graphic import Colour
import random

class Border:

    def __init__(self):
        self.left = 100     # CORNERS
        self.top = 100
        self.right = 700
        self.bottom = 700

        self.init_grid = [(self.left, self.top), (self.right, self.top),
                          (self.right, self.bottom), (self.left, self.bottom)]  # INITIAL GRID/EDGES - NEVER MODIFIED
        self.edge_points = deepcopy(self.init_grid)                 # POINTS THAT MAKE THE EDGES - FREQUENTLY MODIFIED

        self.must_reverse_dir = False

    # ACCESSORS #

    def get_edge_points(self):
        return deepcopy(self.edge_points)

    def get_edges(self):
        return Border.convert_points_to_lines(self.get_edge_points())

    def get_init_grid(self):
        return deepcopy(self.init_grid)

    def get_init_gridlines(self):
        return Border.convert_points_to_lines(self.get_init_grid())

    # MAIN METHODS (public) #

    def is_valid_move(self, x, y, buffer_amt=1):
        """
        Checks if a given coordinate is in bounds
        :return: True if in bounds / False if out of bounds
        """
        point = Point(x, y)
        edges = Polygon(self.get_edge_points())   # Make into Polygon object here
        return edges.buffer(buffer_amt).contains(point)    # buffer(-1) to account for EDGES!!!!! (not "contained")

    def add_poly(self, trail, endpoint2):
        """
        Tries to add player's trail to the edges
        :return: True if successfully added / False if unable to add
        """
        if len(trail) < 1:
            trail.add_endpoint(endpoint2)
            return False  # too short - cannot add trail

        trail.set_last_point(endpoint2)      # Part 1) Fix Trail (set the final point)
        if not trail.fix_trail():            # -----> HELPER: Remove invalid lines of the trail (aka points)
            trail.empty_trail()
            return False  # cannot add trail

        edges = self.get_fixed_edges(trail)   # Part 2) HELPER: Reorder edges; Make sure it's in the right direction
        return self.update_edges(trail, edges)  # Part 3) HELPER: Use fixed trail and edges to perform update

    # MAIN HELPER FUNCTIONS #

    def get_fixed_edges(self, trail):
        """
        Creates edges that go in the same direction as the trail & whose first line contains the 1st point of the trail
        :param trail: "fixed" Trail object (as in, it has no invalid lines)
        :return: "fixed" edges (as in, goes in same direction as tr and has the correct starting edge)
        """
        self.must_reverse_dir = True
        edges = self.get_edges()
        starting_point = trail.get_first_point()

        if not self.is_same_direction_as_edges(deepcopy(trail)):  # HELPER: Check direction to grab the right area
            edges = Trail.get_reverse(deepcopy(edges))            # HELPER: Reverse edges with static Trail method
            self.must_reverse_dir = False

        return Border.get_reordered_edges(deepcopy(edges), starting_point)  # HELPER: Edges must start on starting point

    def update_edges(self, trail, edges):
        """
        Updates the edge points so that trail is considered.
        :param trail: "fixed" Trail object
        :param edges: list of Line objects ("fixed" edges)
        :return: True if successful in updating the edge_points instance variable
        """
        new_edge_points = self.get_new_edge_points(trail, edges)  # HELPER: appends trail to the right section of edges
        if new_edge_points is None:
            trail.empty_trail()
            return False

        new_edge_lines = Trail()                                  # Make into temp Trail obj to benefit from its methods
        new_edge_lines.add_endpoints(new_edge_points)             # -> HELPER: removes overlap
        new_edge_lines.fix_trail()                                # -> HELPER: removes invalid lines (aka points)

        if len(new_edge_lines) < 1:
            trail.empty_trail()
            return False

        fixed_new_edge_points = new_edge_lines.get_trail_points()  # -> HELPER: convert Trail obj back into points

        if self.must_reverse_dir:               # REVERSE EDGES
            fixed_new_edge_points.reverse()

        self.edge_points = fixed_new_edge_points     # FINALLY: do the update
        trail.empty_trail()
        return True  # success

    # HELPER FUNCTIONS #

    def get_new_edge_points(self, trail, edges):
        """
        Appends the trail to the appropriate edge (but does so roughly... may result in duplicate points/overlap)
        :param trail: Trail object
        :param edges: List of Lines wherein its first Line contains the first point of the trail
        :return: List of tuples
        """
        trail_points = trail.get_trail_points()

        try:
            p1_edge_index = Border.get_index_of(edges, trail.get_first_point())  # Line whr edges intsct 1st pt of trail
            p2_edge_index = Border.get_index_of(edges, trail.get_last_point())  # Line whr edges intsct last pt of trail
            first_edge_points = Border.convert_lines_to_points(edges[0:p1_edge_index+1])  # 1st edge pts -> 1st pt of tr
            last_edge_points = Border.convert_lines_to_points(edges[p2_edge_index+1:])   # Last pt of tr -> Last edg pts

            new_edge_points = first_edge_points + trail_points + last_edge_points  # Concatenate points
            return new_edge_points

        except:
            return None  # ex. if unable to identify the index of first or last point of the trail

    def is_same_direction_as_edges(self, trail):
        """
        Checks that the direction of the trail (from firstpt1 to lastpt) matches the direction of the edges
        :param trail: Trail object
        :return: False if the path from lastpt to firstpt is shorter and thus trail is in a different direction
        """
        first_point = trail.get_first_point()
        last_point = trail.get_last_point()

        try:
            first_to_last = self.get_distance_between(first_point, last_point)  # HELPER: Number of turns between 2 points
            last_to_first = self.get_distance_between(last_point, first_point)
            if first_to_last == last_to_first:
                return trail.compare_POIs(self.get_edges(), first_point, last_point)
            return first_to_last <= last_to_first  # Assume that edges are going in the direction with the least turns

        except:
            return None  # ex. Either first_to_last or last_to_first returned None and thus cannot be compared with <=

    def get_distance_between(self, point1, point2): #MODIFIED TO RETURN DISTANCE
        """
        Calculates the distance between two given points when traversing edges
        :param point1: tuple
        :param point2: tuple
        :return: integer
        """
        edges = Border.get_reordered_edges(self.get_edges(), point1)  # Reorder edges st POINT 1 IS AT INDEX 0

        try:
            index_2 = Border.get_index_of(edges, point2)              # POINT 2 IS AT INDEX index_2

            if index_2 == 0:  # CASE A: points are on the same edge
                modified_first_edge = Line(point1, point2)
                distance = modified_first_edge.get_distance()
                return distance

            # CASE B: points are on different edges
            modified_first_edge = Line(point1, edges[0].endpoint2)          # make modified edges
            modified_last_edge = Line(edges[index_2].endpoint1, point2)

            modified_edges = Trail()  # make into trail (bc we have a function to calc distance)
            modified_edges.lines = [modified_first_edge] + edges[1:index_2] + [modified_last_edge] #   get disance
            distance = modified_edges.get_distance()
            return distance                                          # = NUMBER OF LINES BTWN PT 1 AND 2; (+1 bc idx 0)

        except:  # index error, value error
            return None  # ex. If it is unable to find point2 for some reason and thus cannot do index2+1

    # POSITION GENERATORS + HELPERS #

    def get_valid_position(self, step=1):
        """
        Generates a RANDOM valid coordinate for a Player/enemy object (ex. for teleportation)
        :return: Tuple
        """
        random_x = random.randrange(100, 700, step)
        random_y = random.randrange(100, 700, step)
        while not self.is_valid_move(random_x, random_y):
            random_x = random.randrange(100, 700, step)  # any number
            random_y = random.randrange(100, 700, step)  # any number
        return random_x, random_y

    def get_next_sparx_position(self, curr_x, curr_y):
        """
        Finds the NEXT valid coordinate that a Sparc will move to (ex. traverses along the edges in a CW direction)
        :param curr_x: x position of the Sparc
        :param curr_y: y position of the Sparc
        :return: Tuple
        """
        for edge in Border.get_reordered_edges(self.get_edges(), (curr_x, curr_y)):
            if edge.contains((curr_x, curr_y)):
                x = edge.get_next_x(curr_x)
                y = edge.get_next_y(curr_y)
                if x is None or y is None: #next point is invalid
                    pass
                else:
                    return x,y
        return self.get_valid_position_sparx()

    def get_valid_position_sparx(self, step=1):
        """
        Generates a RANDOM valid coordinate for a Sparc object (ex. for teleportation)
        :return: Tuple
        """
        random_x = random.randrange(100, 700, step)
        random_y = random.randrange(100, 700, step)
        while not self.is_on_the_edges(random_x, random_y):
            random_x = random.randrange(100, 700, step)  # any number
            random_y = random.randrange(100, 700, step)  # any number
        return random_x, random_y

    # STATIC METHODS - CONVERSIONS & OTHER #

    def convert_points_to_lines(points):
        """
        Converts a List of points (tuples) to a list of Line objects
        :return: list of Lines created by these points
        """
        points.append(points[0])    # Make into a circuit; bc last line goes from last point -> first point
        lines = []
        for i in range(len(points) - 1):
            line = Line(points[i], points[i + 1])  # Make points into line objects
            lines.append(line)
        return lines

    def convert_lines_to_points(lines):
        """
        Converts a List of Line objects to a List of points (tuples)
        :return: list of points (tuples) that form these lines
        """
        t = Trail()
        t.lines = lines
        return t.get_trail_points()[:-1]  # HELPER defd in Trail class; [:-1] to remove final point

    def get_index_of(lines, point):
        """
        Finds the index of a point in a list of Line objects
        :param point: tuple
        :return: index (integer)
        """
        for i in range(len(lines)):
            line = lines[i]
            if line.contains(point):  # HELPER defd in Line class
                return i
        return None  # If point does not exist within any of the lines

    def get_reordered_edges(edges, starting_point):
        """
        Reorders a list of Line objects such that the first Line contains the given point
        :param edges: list of Line objects
        :param starting_point: tuple, ideally the first point of a Trail object
        :return: reordered edges (List of Lines)
        """
        try:
            starting_index = Border.get_index_of(edges, starting_point)
            return edges[starting_index:]+edges[:starting_index]
        except ValueError:
            return None  # ex. if it cannot find the index of the starting_point

    def is_on_the_edges(self, x, y, epsilon=0):
        """
        Checks if the given coordinate occurs in the border edges.
        :param x: x coordinate
        :param y: y coordinate
        :return: True/False
        """
        for edge in self.get_edges():
            if edge.contains((x, y, epsilon)):
                return True
        return False

    def get_score(self):
        """
        Calculates user's score
        :return: STRING of % of screen that has been consumed
        """
        grid = Polygon(self.get_init_grid())
        max_area = grid.area
        field = Polygon(self.get_edge_points())
        field_area = field.area
        score = round((max_area - field_area) / max_area * 100.0)
        return str(score)

    # GRAPHIC METHODS #

    def draw(self, screen):
        """
        Draws polygons and borders on the screen
        :param screen:
        :return:
        """
        pygame.draw.polygon(screen, Colour.white, self.get_init_grid())   # EATEN AREA

        pygame.draw.polygon(screen, Colour.purple, self.get_edge_points())   # REMAINING AREA (boundaries)

        for gridline in self.get_init_gridlines():  # 4 SIDES OF THE GRID
            gridline.draw(screen, Colour.white, 5)

    def display_score(self, screen, font):
        """
        Displays score at the top-left corner of the game screen.
        """
        score_text = font.render(self.get_score() + " percent", True, Colour.white, Colour.black)
        score_text_rect = score_text.get_rect()
        score_text_rect.midleft = (100, 50)
        screen.blit(score_text, score_text_rect)
