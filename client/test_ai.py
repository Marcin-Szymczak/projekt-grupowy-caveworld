import unittest

import itertools
from uuid import uuid4

class Object:
    def __init__(self, traits=None, satisfaction=0):
        self.traits = traits or []
        self.satisfaction = satisfaction
        self.id = uuid4()

    def act_on(self, actor):
        actor.satisfy(self, self.satisfaction)
    
    def get_traits(self):
        return self.traits

class Knowledge:
    def __init__(self):
        self.wisdom = {}

    def learn(self, object, satisfaction):
        traits = frozenset(object.traits)
        
        self.wisdom[traits] = self.wisdom.get(traits, 0) + satisfaction

        for i in range(1, len(traits)):
            for t in itertools.combinations(traits, i):
                t = frozenset(t)
                self.wisdom[t] = self.wisdom.get(t, 0) + satisfaction*(i/len(traits))

    def rank(self, traits):
        traits = frozenset(traits)
        result = 0
        for wisdom, rank in self.wisdom.items():
            if wisdom <= traits:
                print(wisdom, "contributes", rank, "times", len(wisdom), "=", rank*len(wisdom))
                result += rank*len(wisdom)
            else:
                print(wisdom, "not in", traits)

        return result


class Actor:
    def __init__(self):
        self.satisfaction = 0
        self.knowledge = Knowledge()

    def satisfy(self, source, satisfaction):
        self.satisfaction += satisfaction
        self.knowledge.learn(source, satisfaction)        

class TestAI(unittest.TestCase):
    def test_ai(self):
        a = Actor()

        o_bad = Object(
            {"small", "hard"}, -10
        )
        
        o_good = Object(
            {"small", "squishy", "soft"}, 10
        )

        o_unknown = Object(
            {"small", "squishy", "wooden"}, -20
        )

        o_bad.act_on(a)
        o_bad.act_on(a)
        o_good.act_on(a)
        print(a.knowledge.wisdom)
        print('prediction for', o_unknown.traits, a.knowledge.rank(o_unknown.traits))