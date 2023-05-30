# マスが密集するほど評価値が高い
from typing import List
import sys
sys.path.append('../')
from core import Stage, Card, Placement, Point

class SpaceEval:
    def __init__(self):
        pass

    def max_eval(self, stage: Stage, cards: List[Card]) -> int:
        return len(stage.pattern.cells) + sum([len(c.patterns[0].cells) for c in cards])

    def eval(self, stage: Stage) -> float:
        if len(stage.pattern.cells) == 0:
            return 0

        neighbors = stage.get_neighbor_pattern().cells
        neighbor_score = 0
        for neighbor in neighbors:
            for ox in [-1, 0, 1]:
                for oy in [-1, 0, 1]:
                    offset = Point(ox, oy)
                    new_point = neighbor.point + offset
                    if not stage.pattern.has(new_point):
                        neighbor_score += 1

        return len(stage.pattern.cells) / neighbor_score

    def get_score_of_empty_cell(self, stage: Stage, point: Point) -> float:
        score_sum = 0
        length = 3
        for y in range(-length, length+1):
            for x in range(-length, length+1):
                m = abs(y) + abs(x)
                if m == 1:
                    score = 10
                elif m == 2:
                    score = 5
                elif m == 3:
                    score = 3
                else:
                    break

                new_point = point + Point(x, y)
                if stage.pattern.has(new_point):
                    score_sum += score

        return score_sum

    def eval_put(self, stage: Stage, placement: Placement) -> float:
        return sum([self.get_score_of_empty_cell(stage, cell.point) for cell in placement.get_pattern().cells])
