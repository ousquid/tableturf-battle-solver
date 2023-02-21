# マスを埋める数が多いと評価値が高い
from typing import List
import sys
sys.path.append('../')
from core import Stage, Card

class FillEval:
    def __init__(self):
        pass

    def max_eval(self, stage: Stage, cards: List[Card]) -> int:
        return stage.pattern.sum() + sum([c.pattern.sum() for c in cards])

    def eval(self, stage: Stage) -> int:
        return stage.pattern.sum()