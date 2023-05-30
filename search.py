from typing import List, Tuple, Dict
from typing_extensions import Self
import copy
from enum import Enum
from itertools import combinations, permutations
import tqdm
#from score.fill import FillEval
from score.space import SpaceEval
from core import Stage, Card, Placement, Rotation
import time

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds to execute.")
        return result
    return wrapper

class Solver:
    def __init__(self):
        self.evaluator = SpaceEval()

    def search_combo(self, n: int, cards: List[Card]) -> Stage:
        best_permutation = Stage()
        for c in combinations(cards, n):
            for head, *tail in tqdm.tqdm(list(permutations(c, n))):
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
        top_n = 2
        for c in sorted_cards:
            point_evals: Dict(Placement, float) = {}
            for rotation in Rotation.get_values():
                for point in stage.get_points():
                    placement = Placement(c, point, rotation)
                    if not (stage.can_be_put(placement) and stage.neighbor_pattern(placement)):
                        continue
                    curval = self.evaluator.eval_put(stage, placement)
                    if len(point_evals) < top_n:
                        point_evals[placement] = curval
                    elif curval > min(point_evals.values()):
                        min_eval_key = min(point_evals, key=point_evals.get)
                        del point_evals[min_eval_key]
                        point_evals[placement] = curval

        best = (Stage(), self.evaluator.eval(Stage()))  # (stage, eval)
        for placement in point_evals.keys():
            new_stage = stage.put_card(placement)
            new_cards = copy.copy(cards)
            new_cards.remove(c)
            child_best_stage = self.search(new_stage, new_cards)
            if self.evaluator.eval(child_best_stage) > best[1]:
                best = (child_best_stage, self.evaluator.eval(child_best_stage))
        return best[0]

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
