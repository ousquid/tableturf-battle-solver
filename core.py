from typing import List, Tuple, Self, Set
import os
import glob
import copy
from enum import Enum
from scipy import ndimage
import colorama  as cr
import math

class Point:
    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y

    def __eq__(self, rhs:Self) -> bool:
        return (self.x == rhs.x) and (self.y == rhs.y)

    def __add__(self, rhs:Self) -> Self:
        return Point(self.x + rhs.x, self.y + rhs.y)

class Cell:
    def __init__(self, point:Point, sp:bool):
        self.point = point
        self.sp = sp

    def rot90(self) -> Self:
        return Cell(Point(self.point.y, -self.point.x), self.sp)

    def offset_y(self, y:int) -> Self:
        self.point.y += y

    def __eq__(self, rhs:Self) -> bool:
        return self.point == rhs.point # ignore sp!!

class Pattern:
    def __init__(self, cells=None):
        self.cells: Set[Cell] = cells if cells is not None else set()

    def add(self, cell:Cell):
        self.cells.add(cell)

    def rot90(self) -> Self:
        new_cells = {cell.rot90() for cell in self.cells}
        min_y = min(new_cells, key=lambda c: c.point.y)
        for cell in new_cells:
            cell.offset_y(-min_y)
        return Pattern(new_cells)

    def has(self, point:Point):
        return Cell(point, False) in self.cells

    @property
    def shape(self) -> Tuple[int, int]:
        y = max(self.cells, key=lambda c: c.point.y)
        x = max(self.cells, key=lambda c: c.point.x)
        return (y, x)

    def __getitem__(self, item):
        ys, xs = item
        new_pat = Pattern()
        for c in self.cells:
            if ((ys.start <= c.point.y and c.point.y < ys.stop) and
                (xs.start <= c.point.x and c.point.x < xs.stop)):
                new_pat.add(c)
        return new_pat

    def __and__(self, rhs: Self) -> Self:
        new_cells = self.cells & rhs.cells
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
        pattern: Set[Cell],
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

        max_width = max([len(line.rstrip()) for line in lines])
        max_height = len(lines)
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
        pattern = self.card.pattern
        for _ in range(int(self.rotation)):
            pattern = pattern.rot90()
        return pattern

    def __repr__(self):
        return f"<Card: {self.card.number}, {self.card.ink_spaces=}, {self.point.x=}, {self.point.y=}>"

class Stage:
    def __init__(self, number: int, name: str, pattern: Pattern):
        self.number = number
        self.name = name
        self.pattern: Pattern = pattern
        self.init_pattern = pattern.copy()
        self.place_hist = list()

    def get_points(self):
        y, x = self.pattern.shape
        for y in range(y):
            for x in range(x):
                if not self.pattern.has(Point(x, y)):
                    yield Point(x, y)

    def get_slice_indices(self, place: Placement, pattern: Pattern):
        pat_h, pat_w = pattern.shape
        return (place.point.y, place.point.y + pat_h,
                place.point.x, place.point.x + pat_w)

    def get_slice(self, place: Placement) -> Pattern:
        card_pat = place.get_pattern()
        y_start, y_end, x_start, x_end = self.get_slice_indices(place, card_pat)
        return self.pattern[y_start:y_end, x_start:x_end]

    def can_be_put(self, place: Placement) -> bool:
        card_pat = place.get_pattern()
        card_h, card_w = card_pat.shape
        stage_h, stage_w = self.pattern.shape
        # マップからはみ出ていないか
        if card_h + place.point.y > stage_h or card_w + place.point.x > stage_w:
            return False
        # 他のカードと重ならないか
        stage_pat = self.get_slice(place)

        if len(card_pat & stage_pat) > 0:
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
        return len((card_pat & expand_pat) > 0)

    def put_card(self, place: Placement) -> Self:
        card_pat = place.get_pattern()
        new_stage = copy.deepcopy(self)
        stage_pat = new_stage.get_slice(place)
        stage_pat += card_pat

        new_stage.place_hist.append(place)
        return new_stage

    # def evaluator(self) -> int:
    #     return FillEval.eval(self)

    # def max_eval(self, cards: List[Card]) -> int:
    #     return FillEval.max_eval(self, cards)

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

        canvas = np.full(self.pattern.shape, cr.Fore.WHITE + '.').astype(object)
        canvas[self.init_pattern == 1] = cr.Fore.YELLOW + "0"
        for i, p in enumerate(self.place_hist):
            card_pat = p.get_pattern()
            y_start, y_end, x_start, x_end = self.get_slice_indices(p, card_pat)
            canvas_pat = canvas[y_start:y_end, x_start:x_end]
            canvas_pat[card_pat == 1] = colormap[i]+"0"
            canvas_pat[card_pat == 2] = colormap[i]+"X"

        for r in canvas:
            print("".join(r))

    @staticmethod
    def load_text(path: str):
        with open(path, "r") as f:
            lines = f.readlines()

        max_width = max([len(line.rstrip()) for line in lines])
        max_height = len(lines)
        pattern = np.zeros((max_height, max_width)).astype(np.uint8)

        for y, line in enumerate(lines):
            for x, p in enumerate(line):
                if p == "x":
                    pattern[y, x] = 1

        number = int(os.path.splitext(os.path.basename(path))[0])
        name = "StraightStreet"
        return Stage(number, name, pattern)
