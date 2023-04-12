from typing import List, Tuple, Self, Set
import os
import glob
import copy
from enum import Enum
import colorama  as cr
import math

class Point:
    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y

    def __eq__(self, rhs:Self) -> bool:
        return (self.x == rhs.x) and (self.y == rhs.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __add__(self, rhs:Self) -> Self:
        return Point(self.x + rhs.x, self.y + rhs.y)

class Cell:
    def __init__(self, point:Point, sp:bool = False):
        self.point = point
        self.sp = sp

    def rot90(self) -> Self:
        return Cell(Point(self.point.y, -self.point.x), self.sp)

    def offset_x(self, x:int) -> Self:
        return Cell(Point(self.point.x + x, self.point.y), self.sp)

    def offset_y(self, y:int) -> Self:
        return Cell(Point(self.point.x, self.point.y + y), self.sp)

    def __eq__(self, rhs:Self) -> bool:
        return self.point == rhs.point # ignore sp!!

    def __hash__(self):
        return hash(self.point)

    def __repr__(self):
        return f"({self.point.x}, {self.point.y})"

class Pattern:
    def __init__(self, cells=None):
        self.cells: Set[Cell] = copy.deepcopy(cells) if cells is not None else set()

    def add(self, cell:Cell):
        self.cells.add(cell)

    def offset(self, point: Point):
        new_cells = set()
        for cell in self.cells:
            new_cell = cell.offset_x(point.x)
            new_cell = new_cell.offset_y(point.y)
            new_cells.add(new_cell)
        self.cells = new_cells

    def rot90(self) -> Self:
        rotated_cells = {cell.rot90() for cell in self.cells}
        min_y = min([c.point.y for c in rotated_cells])
        new_cells = set()
        for cell in rotated_cells:
            new_cells.add(cell.offset_y(-min_y))
        return Pattern(new_cells)

    def has(self, point:Point):
        return Cell(point, False) in self.cells

    def __len__(self):
        return len(self.cells)

    @property
    def shape(self) -> Tuple[int, int]:
        y = max([c.point.y for c in self.cells])
        x = max([c.point.x for c in self.cells])
        return (y, x)

    def __getitem__(self, item):
        ys, xs = item
        new_pat = Pattern()
        for c in self.cells:
            if ((ys.start <= c.point.y and c.point.y < ys.stop) and
                (xs.start <= c.point.x and c.point.x < xs.stop)):
                new_pat.add(Cell(Point(c.point.x, c.point.y), c.sp))
        return new_pat

    def __and__(self, rhs: Self) -> Self:
        new_cells = self.cells & rhs.cells
        return Pattern(new_cells)

    def __or__(self, rhs: Self) -> Self:
        new_cells = self.cells | rhs.cells
        return Pattern(new_cells)

    def empty(self) -> bool:
        return len(self.cells) == 0

class Rotation(Enum):
    RIGHT = 0
    BOTTOM = 1
    LEFT = 2
    TOP = 3

    @classmethod
    def get_values(cls):
        return [i.value for i in cls]

class Card:
    def __init__(
        self,
        number: int,
        name: str,
        pattern: Pattern,
        ink_spaces: int,
        sp_attack_cost: int,
    ):
        self.number = number
        self.name = name
        self.pattern = pattern
        self.ink_spaces = ink_spaces
        self.sp_attack_cost = sp_attack_cost

    @staticmethod
    def load_text(path: str):
        with open(path, "r") as f:
            lines = f.readlines()

        pattern = Pattern()

        for y, line in enumerate(lines):
            for x, p in enumerate(line):
                if p == "x":
                    pattern.add(Cell(Point(x, y), False))
                elif p == "o":
                    pattern.add(Cell(Point(x, y), True))

        number = int(os.path.splitext(os.path.basename(path))[0])
        name = "Kojake"
        ink_spaces = 1
        sp_attack_cost = 1
        return Card(number, name, pattern, ink_spaces, sp_attack_cost)

    @staticmethod
    def load_dir(path: str):
        return [Card.load_text(f) for f in glob.glob(path)]

class Placement:
    def __init__(self, card: Card, point: Point, rotation: Rotation):
        self.card = card
        self.point = point
        self.rotation = rotation

    def get_pattern(self) -> Pattern:
        pattern = copy.deepcopy(self.card.pattern)
        for _ in range(int(self.rotation)):
            pattern = pattern.rot90()
        pattern.offset(self.point)
        return pattern

    def __repr__(self):
        return f"<Card: {self.card.number}, {self.card.ink_spaces=}, {self.point.x=}, {self.point.y=}>"

class Stage:
    def __init__(self, number: int, name: str, pattern: Pattern, width:int, height:int):
        self.number = number
        self.name = name
        self.pattern: Pattern = pattern
        self.init_pattern = copy.deepcopy(pattern)
        self.place_hist = list()
        self.width = width
        self.height = height

    def get_points(self):
        for y in range(self.height):
            for x in range(self.width):
                if not self.pattern.has(Point(x, y)):
                    yield Point(x, y)

    def can_be_put(self, place: Placement) -> bool:
        card_pat = place.get_pattern()
        card_y, card_x = card_pat.shape
        # マップからはみ出ていないか
        if card_y >= self.height or card_x >= self.width:
            return False

        # 他のカードと重ならないか
        if len(card_pat & self.pattern) > 0:
            return False
        return True

    def neighbor_pattern(self, place: Placement) -> bool:
        expand_pat = Pattern()
        for c in self.pattern.cells:
            for ox in [-1, 0, 1]:
                for oy in [-1, 0, 1]:
                    offset = Point(ox, oy)
                    expand_pat.add(Cell(c.point + offset))

        card_pat = place.get_pattern()
        return len(card_pat & expand_pat) > 0

    def put_card(self, place: Placement) -> Self:
        card_pat = place.get_pattern()
        new_stage = copy.deepcopy(self)
        new_stage.pattern |= card_pat

        new_stage.place_hist.append(place)
        return new_stage

    def draw(self):
        colormap = [
            cr.Fore.BLUE,
            cr.Fore.CYAN,
            cr.Fore.GREEN,
            cr.Fore.LIGHTBLACK_EX,
            cr.Fore.LIGHTBLUE_EX,
            cr.Fore.LIGHTCYAN_EX,
            cr.Fore.LIGHTGREEN_EX,
            cr.Fore.LIGHTMAGENTA_EX,
            cr.Fore.LIGHTRED_EX,
            cr.Fore.LIGHTWHITE_EX,
            cr.Fore.LIGHTYELLOW_EX,
            cr.Fore.MAGENTA,
            cr.Fore.RED,
            cr.Fore.RESET,
            cr.Fore.WHITE,
            cr.Fore.YELLOW]

        canvas = np.full((self.height, self.width), cr.Fore.WHITE + '.').astype(object)
        for cell in self.init_pattern.cells:
            canvas[cell.point.y, cell.point.x] = cr.Fore.YELLOW + "0"
        for i, p in enumerate(self.place_hist):
            for cell in p.get_pattern().cells:
                canvas[cell.point.y, cell.point.x] = colormap[i] + ("X" if cell.sp else "0")

        for r in canvas:
            print("".join(r))

    @staticmethod
    def load_text(path: str):
        with open(path, "r") as f:
            lines = f.readlines()

        width = max([len(line.rstrip()) for line in lines])
        height = len(lines)
        pattern = Pattern()

        for y, line in enumerate(lines):
            for x, p in enumerate(line):
                if p == "x":
                    pattern.add(Cell(Point(x, y)))

        number = int(os.path.splitext(os.path.basename(path))[0])
        name = "StraightStreet"
        return Stage(number, name, pattern, width, height)
