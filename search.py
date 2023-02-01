from typing import List, Tuple, Self
from enum import Enum
import glob
from tqdm import tqdm
import numpy as np
import os
import copy
from itertools import combinations, permutations
from scipy import ndimage
import colorama  as cr

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rotation(Enum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3

    @classmethod
    def get_values(cls):
        return [i.value for i in cls]


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

    def get_pattern(self) -> np.ndarray:
        pattern = self.card.pattern
        for _ in range(int(self.rotation)):
            pattern = np.rot90(pattern)
        return pattern

    def __repr__(self):
        return f"<Card: {self.card.number}, {self.card.ink_spaces=}, {self.point.x=}, {self.point.y=}>"


class Stage:
    def __init__(self, number: int, name: str, pattern: np.ndarray):
        self.number = number
        self.name = name
        self.pattern = pattern
        self.init_pattern = pattern.copy()
        self.place_hist = list()

    def get_points(self):
        y, x = self.pattern.shape
        for y in range(y):
            for x in range(x):
                if not self.pattern[y, x]:
                    yield Point(x, y)

    def get_slice_indices(self, place: Placement, pattern: np.ndarray):
        pat_h, pat_w = pattern.shape
        return (place.point.y, place.point.y + pat_h,
                place.point.x, place.point.x + pat_w)

    def get_slice(self, place: Placement) -> np.ndarray:
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

        if np.any(card_pat & stage_pat):
            return False
        return True

    def neightbor_pattern(self, place: Placement) -> bool:
        kernel = ndimage.generate_binary_structure(2, 2)
        dilated = ndimage.binary_dilation(self.pattern, structure=kernel)
        neighbor = dilated - self.pattern
        neighbor_stage = Stage(0, "", neighbor)
        stage_pat = neighbor_stage.get_slice(place)
        card_pat = place.get_pattern()
        return np.any(card_pat & stage_pat)

    def put_card(self, place: Placement) -> Self:
        card_pat = place.get_pattern()
        new_stage = copy.deepcopy(self)
        stage_pat = new_stage.get_slice(place)
        stage_pat += card_pat

        new_stage.place_hist.append(place)
        return new_stage

    def eval(self) -> int:
        return self.fill_eval()

    def max_eval(self, cards: List[Card]) -> int:
        return self.pattern.sum() + sum([c.pattern.sum() for c in cards])

    def fill_eval(self) -> int:
        return self.pattern.sum()

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
        canvas[self.init_pattern == 1] = cr.Fore.YELLOW + "X"
        for i, p in enumerate(self.place_hist):
            card_pat = p.get_pattern()
            y_start, y_end, x_start, x_end = self.get_slice_indices(p, card_pat)
            canvas_pat = canvas[y_start:y_end, x_start:x_end]
            canvas_pat[card_pat == 1] = colormap[i]+"0"

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


class Solver:
    def __init__(self):
        pass

    def search_combo(self, n: int, stage: Stage, cards: List[Card]) -> Stage:
        best_combination = stage
        for c in combinations(cards, n):
            best_permutation = stage
            for p in permutations(c, n):
                ans = self.search(copy.deepcopy(stage), list(p))
                if ans.eval() > best_permutation.eval():
                    best_permutation = ans
            if best_permutation.eval() > best_combination.eval():
                best_combination = best_permutation
        return best_combination

    def search(self, stage: Stage, cards: List[Card]) -> Stage:
        if len(cards) == 0:
            return stage

        best_stage = stage
        sorted_cards = sorted(cards, key=lambda x: x.ink_spaces)
        max_eval = stage.max_eval(cards)
        for c in sorted_cards:
            if len(cards) == 6:
                print(f"card:{c}")
            for rotation in Rotation.get_values():
                if len(cards) == 6:
                    print(f"rotation:{rotation}")
                for point in stage.get_points():
                    placement = Placement(c, point, rotation)
                    if stage.can_be_put(placement) and stage.neightbor_pattern(placement):
                        new_stage = stage.put_card(placement)
                        new_cards = copy.copy(cards)
                        new_cards.remove(c)
                        child_best_stage = self.search(new_stage, new_cards)
                        if child_best_stage.eval() == max_eval:
                            return child_best_stage
                        if child_best_stage.eval() > best_stage.eval():
                            best_stage = child_best_stage
        return best_stage

def main():
    stage = Stage.load_text("stages/01.txt")
    # cards = Card.load_dir("cards/*.txt")
    cards = [
        Card.load_text(txt)
        for txt in ["cards/001.txt", "cards/002.txt", "cards/003.txt", "cards/004.txt", "cards/095.txt", "cards/144.txt",]
    ]
    print(cards)

    solver = Solver()
    return solver.search_combo(4, stage, cards)

if __name__ == "__main__":
    ans = main()
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
