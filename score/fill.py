# マスを埋める数が多いと評価値が高い
from typing import List
import sys
sys.path.append('../')
from core import Stage, Card, Placement

class FillEval:
    def __init__(self):
        pass

    def max_eval(self, stage: Stage, cards: List[Card]) -> int:
        return len(stage.pattern.cells) + sum([len(c.patterns[0].cells) for c in cards])

    def eval(self, stage: Stage, placement: Placement) -> int:
        return len(stage.pattern.cells) + len(placement.get_pattern().cells)
