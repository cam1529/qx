import pygame
from copy import deepcopy
from Graphic import Colour


class Line:
    def __init__(self, endpoint1, endpoint2=None):
        self.endpoint1 = endpoint1
        self.endpoint2 = endpoint2

    # ACCESSORS #

    def x1(self):
        return self.endpoint1[0]

    def y1(self):
        return self.endpoint1[1]

    def x2(self):
        return self.endpoint2[0]

    def y2(self):
        return self.endpoint2[1]

    def get_distance(self):
        """
        :return: line length (float)
        """
        return (((self.x2() - self.x1())**2) + ((self.y2() - self.y1())**2))**0.5

    # METHODS RELATED TO INTERSECTION #

    def contains(self, point, epsilon=0):
        """
        Checks if the given point is on this line
        :return: True if point is on the line/False otherwise
        """
        try:
            x, y = point[0], point[1]
            x1, y1 = self.x1(), self.y1()
            x2, y2 = self.x2(), self.y2()
            return ((x1-epsilon) <= x <= (x2+epsilon) or (x2-epsilon) <= x <= (x1+epsilon)) and ((y1-epsilon) <= y <= (y2+epsilon) or (y2-epsilon) <= y <= (y1+epsilon))
        except:
            return False  # ex. if Point is not a tuple/list

    def intersects(self, line):
        """
        Checks if the given line intersects this line
        :return: True if intersects/False otherwise
        """
        return self.get_POI(line) is not None

    def get_POI(self, line):
        """
        Finds the point of intersection (POI) of the given line and this line
        :return: Tuple of POI; None if no POI
        """
        x = line.x1()
        y = line.y1()

        while line.contains((x, y)):  # Iterate through given line
            if self.contains((x, y)):  # Check if point is on this line
                return (x, y)
            x = line.get_next_x(x)
            y = line.get_next_y(y)
        return None  # No point of intersection

    def compare_POIs(self, point1, point2):
        """
        Checks that point1 appears on this line before point2
        :param point1: tuple that is on this line
        :param point2: tuple
        :return: False if point2 occurs before point1
        """
        same_x = (point1[0] == point2[0])
        same_y = (point1[1] == point2[1])
        if same_x:
            return abs(point1[1] - self.y1()) <= abs(point2[1] - self.y1())
        elif same_y:
            return abs(point1[0] - self.x1()) <= abs(point2[0] - self.x1())

    # GENERAL HELPER METHODS #

    def get_reverse(self):
        """
        Gets the Line that goes in the opposite direction
        :return: Line object
        """
        return Line(self.endpoint2, self.endpoint1)

    def get_next_x(self, current_x):    # iteration method
        return Line.get_next(current_x, self.x1(), self.x2())

    def get_next_y(self, current_y):    # iteration method
        return Line.get_next(current_y, self.y1(), self.y2())

    def get_next(current, min, max): # static
        """
        Gets next value of the line (to help with iterating through the line)
        :return: int
        """
        if min == max:
            return current
        elif min < max:   # max is max
            if current >= max:
                return None     # cannot iterate
            return current+1
        elif min > max:   # min is max
            if current <= max:
                return None     # cannot iterate
            return current-1

    def __str__(self):
        return "<Line:"+str(self.endpoint1)+"->"+str(self.endpoint2)+">"

    # GRAPHICS METHOD #

    def draw(self, screen, colour = Colour.blue, thickness = 5):
        """
        Draws line object on the screen
        """
        pygame.draw.line(screen, colour, self.endpoint1, self.endpoint2, thickness)

class Trail:
    def __init__(self):
        self.lines = []

    # ACCESSOR METHODS #

    def is_empty(self):
        return len(self) <= 0

    def get_lines(self):
        return deepcopy(self.lines)

    def get_last_line(self):
        return self.lines[-1]

    def get_first_point(self):
        return self.lines[0].endpoint1

    def get_last_point(self):
        return self.get_last_line().endpoint2

    def get_distance(self):
        """
        :return: sum of trail line lengths (float)
        """
        distance = 0
        for line in self.get_lines():
            distance += line.get_distance()
        return distance

    # SIMPLE MUTATOR METHODS #

    def add_line(self, line):
        self.lines.append(line)

    def empty_trail(self):
        self.lines = []
    
    def set_last_point(self, last_point):
        self.get_last_line().endpoint2 = last_point

    # METHODS RELATED TO MODIFYING THE TRAIL (in real time) #

    def add_endpoint(self, endpoint):
        """
        Adds a point to the trail when changing directions
        :param endpoint: tuple
        """
        if len(self) > 0:
            self.set_last_point(endpoint)
        self.add_line(Line(endpoint))

    def add_endpoints(self, points):
        """
        Adds a list of points to the trail (ex. for initializing a trail via points)
        :param points: list of tuples
        """
        for point in points:
            if point is not None:
                x = point[0]
                y = point[1]
                if self.contains(x, y):     # Check for backtracking
                    self.backtrack_to_line_with(x, y)
                self.add_endpoint((x, y))
        self.lines.pop()                    # Remove last line (ex. the Line(last_point->NONE))

    def backtrack_to_line_with(self, x, y):
        """
        Updates self.lines so that any overlapping movement results in backtracking
        :param x: x-coordinate
        :param y: y-coordinate
        :return: True if backtracking was done; False if no backtracking needed
        """
        lines = []                          # All lines that occur in the trail before the backtracking point
        for line in self.get_lines():
            if line.contains((x, y)):       # Backtracking needed
                modified_line = Line(line.endpoint1, (x,y))
                lines.append(modified_line)
                self.lines = lines          # Update => Successfully backtracked!
                self.add_endpoint((x, y))   # Create a new point at this backtracking point
                return True
            else:
                lines.append(line)
        return False

    # METHODS RELATED TO MODIFYING THE TRAIL (once last point has been reached)

    def fix_trail(self):
        """
        Modifies trail lines to remove invalid lines
        :return: False if trail cannot be fixed; True if it was fixed
        """
        if self.get_distance() < 4:
            return False

        true_points = [self.get_first_point()]
        for line in self.get_lines():
            if line.endpoint1 != line.endpoint2:    # Ignore lines that are points (= invalid)
                true_points.append(line.endpoint2)

        if len(true_points) < 2:
            return False

        self.empty_trail()                      # Remake the whole trail using only the true_points
        self.add_endpoints(true_points[::-1])   # Reverse ([::-1]) to remove the bugged lines
        return True

    # METHODS RELATED TO INTERSECTION #

    def contains(self, x, y, epsilon=0, ignore_last_line=True):
        """
        Checks whether a given point is already in the trail
        :return: True if point occurs in the trail/False otherwise
        """
        temp_lines = deepcopy(self.lines)
        if ignore_last_line:
            temp_lines = temp_lines[:-1]  # don't include last line of trail?
        for line in temp_lines:
            if line.contains((x, y, epsilon)):
                return True
        return False

    def compare_POIs(self, edges, point1, point2):
        """
        Finds the line that contains both point1 and point2, then compares which of them occurs first (for direction)
        :param edges: list of Line objects
        :return: True if point1 is first on the line
        """
        for edge in edges:
            if edge.contains(point1) and edge.contains(point2):
                return edge.compare_POIs(point1, point2)

    # CONVERSION HELPER METHODS #

    def get_trail_points(self):
        """
        Converts trail lines to trail points
        :return: list of points of the trail
        """
        points = [self.get_first_point()]
        for line in self.lines:
            points.append(line.endpoint2)
        return points

    # GENERAL HELPER METHODS #

    def get_reverse(lines):
        """
        Gets the trail that moves from last point to first point
        :return: list of Line objects
        """
        temp = deepcopy(lines)
        temp.reverse() # reverse the list
        rev_lines = []
        for line in temp:
            rev_lines.append(line.get_reverse())
        return rev_lines

    def __len__(self):
        return len(self.lines)

    def __str__(self):
        string = "Trail: lines"
        for line in self.lines:
            string += " -> "+str(line)
        return string+"]"

    # GRAPHICS METHOD #

    def draw(self, screen, endpoint):
        """
        Draws trail object on the screen
        :param endpoint: player's current coordinate (line still in progress; not yet added to the trail)
        """
        for line in self.lines:
            if line.endpoint2 is None:
                current_line = Line(line.endpoint1, endpoint)
                current_line.draw(screen)
            else:
                line.draw(screen)
