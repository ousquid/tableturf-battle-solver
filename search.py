from typing import List, Tuple, Self
import copy
from enum import Enum
from itertools import combinations, permutations

from score.fill import FillEval
from core import Stage, Card, Placement, Rotation

class Solver:
    def __init__(self):
        self.evaluator = FillEval()

    def search_combo(self, n: int, cards: List[Card]) -> Stage:
        best_permutation = Stage()
        for c in combinations(cards, n):
            print(f"combination: {c}")
            for head, *tail in permutations(c, n):
                print(f"permutation: {head}")
                ans = self.search(Stage.load_card(head), tail)
                if self.evaluator.eval(ans) > self.evaluator.eval(best_permutation):
                    best_permutation = ans
        return best_permutation

    def search(self, stage: Stage, cards: List[Card]) -> Stage:
        if len(cards) == 0:
            return stage

        best_stage = stage
        sorted_cards = sorted(cards, key=lambda x: x.ink_spaces)
        max_eval = self.evaluator.max_eval(stage, cards)
        for c in sorted_cards:
            for rotation in Rotation.get_values():
                for point in stage.get_points():
                    placement = Placement(c, point, rotation)
                    if stage.can_be_put(placement) and stage.neighbor_pattern(placement):
                        new_stage = stage.put_card(placement)
                        new_cards = copy.copy(cards)
                        new_cards.remove(c)
                        child_best_stage = self.search(new_stage, new_cards)
                        if self.evaluator.eval(child_best_stage) == max_eval:
                            return child_best_stage
                        if self.evaluator.eval(child_best_stage) > self.evaluator.eval(best_stage):
                            best_stage = child_best_stage
        return best_stage

def main():
    stage = Stage.load_text("stages/01.txt")
    # cards = Card.load_dir("cards/*.txt")
    cards = [
        Card.load_text(txt)
        for txt in ["cards/001.txt", "cards/002.txt", "cards/003.txt", "cards/004.txt", "cards/095.txt", "cards/144.txt",]
    ]
    solver = Solver()
    return solver.search_combo(6, cards)

if __name__ == "__main__":
    ans = main()
    ans.draw()
