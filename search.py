from typing import List, Tuple, Self
import copy
from enum import Enum
from itertools import combinations, permutations
import numpy as np

from score.fill import FillEval
from core import Stage, Card, Placement, Rotation

class Solver:
    def __init__(self):
        self.evaluator = FillEval()

    def search_combo(self, n: int, stage: Stage, cards: List[Card]) -> Stage:
        best_combination = stage
        for c in combinations(cards, n):
            best_permutation = stage
            for p in permutations(c, n):
                ans = self.search(copy.deepcopy(stage), list(p))
                if self.evaluator.eval(ans) > self.evaluator.eval(best_permutation):
                    best_permutation = ans
            if self.evaluator.eval(best_permutation) > self.evaluator.eval(best_combination):
                best_combination = best_permutation
        return best_combination

    def search(self, stage: Stage, cards: List[Card]) -> Stage:
        if len(cards) == 0:
            return stage

        best_stage = stage
        sorted_cards = sorted(cards, key=lambda x: x.ink_spaces)
        max_eval = self.evaluator.max_eval(stage, cards)
        for c in sorted_cards:
            if len(cards) == 2:
                print(f"card:{c}")
            for rotation in Rotation.get_values():
                if len(cards) == 2:
                    print(f"rotation:{rotation}")
                for point in stage.get_points():
                    placement = Placement(c, point, rotation)
                    if stage.can_be_put(placement) and stage.neighbor_pattern(placement):
                        new_stage = stage.put_card(placement)
                        new_cards = copy.copy(cards)
                        new_cards.remove(c)
                        child_best_stage = self.search(new_stage, new_cards)
                        if self.evaluator.eval(child_best_stage) == max_eval:
                            return child_best_stage
                        #print(self.evaluator.eval(child_best_stage))
                        if self.evaluator.eval(child_best_stage) > self.evaluator.eval(best_stage):
                            best_stage = child_best_stage
                            #print(best_stage.place_hist)
        return best_stage

def main():
    stage = Stage.load_text("stages/01.txt")
    # cards = Card.load_dir("cards/*.txt")
    cards = [
        Card.load_text(txt)
        for txt in ["cards/001.txt", "cards/002.txt", "cards/003.txt", "cards/004.txt", "cards/095.txt", "cards/144.txt",]
        # for txt in ["cards/001.txt", "cards/002.txt"]
    ]
    solver = Solver()
    return solver.search_combo(6, stage, cards)

if __name__ == "__main__":
    ans = main()
    ans.draw()
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
