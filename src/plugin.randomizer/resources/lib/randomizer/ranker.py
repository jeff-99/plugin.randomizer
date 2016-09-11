import random


def normalize(value,min,maxVal):
    denominator = max([float(maxVal - min),1])

    return float(value - min) / denominator


def reversed_normalize(value,min,maxVal):
    return 1.0 - normalize(value,min,maxVal)


class AbstractRanker(object):
    def __init__(self, items):
        self.items = items

    def calculate(self):
        raise NotImplementedError("A Ranker needs to implement the calculate method")


class RandomRanker(AbstractRanker):
    def calculate(self):
        for episode in self.items:
            episode["score"] = random.randint(1,100)

        return self.items


class PlaycountRanker(AbstractRanker):
    def calculate(self):
        playcounts = [int(episode["playcount"]) for episode in self.items]
        minimum = min(playcounts)
        maximum = max(playcounts)

        for episode in self.items:
            reversed_normalization_factor = reversed_normalize(episode["playcount"], minimum, maximum)
            episode["score"] = int(episode["score"] * reversed_normalization_factor)

        return self.items

class LastPlayedRanker(AbstractRanker):
    def calculate(self):
        return self.items