from typing import List, Tuple
from enum import Enum
import glob
import numpy as np
import os


class Point:
    pass


class Rotation(Enum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


class Card:
    def __init__(
        self,
        number: int,
        name: str,
        pattern: np.ndarray,
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
        pattern = np.zeros((max_height, max_width)).astype(np.uint8)

        for y, line in enumerate(lines):
            for x, p in enumerate(line):
                if p == "o" or p == "x":
                    pattern[y, x] = 1

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


class Solver:
    def search() -> Tuple[List[Card], List[Point]]:
        pass


class Stage:
    def __init__(self, number: int, name: str, pattern: np.ndarray):
        self.number = number
        self.name = name
        self.pattern = pattern

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


def fill_eval(stage: Stage) -> int:
    pass


def can_be_put(stage: Stage, card: Card) -> bool:
    # マップからはみ出ていないか
    # 他のカードと重ならないか
    pass


def rotate() -> Card:
    pass


if __name__ == "__main__":
    stage = Stage.load_text("stages/01.txt")
    cards = Card.load_dir("cards/*.txt")
    print(cards)

    solver = Solver.new()
    ans = solver.search(stage, cards)

#
# ________
# ________
# ________
# ________
# ________
# ________
# ________
#
# ________
# _*____*_
# ___*____
# *****_**
# _*__*___
# __*_____
# ********
#
# ________
# ________
# ________
# _____*__
# _____**_
# ********
# ********
# ********
#
