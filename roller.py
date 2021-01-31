import numpy as np

class SuccessResult:
    def __init__(self, rolls, successes, bonus, negations, min_success=0):
        self.rolls     = rolls
        self.successes = int(successes)
        self.bonus     = int(bonus)
        self.negations = int(negations)
        self.raw_total = int(successes + bonus - negations)
        self.min       = int(min_success)
        self.total     = int(max(self.raw_total, self.min))

# success roller
def roll(attr, bonus, n, min_success=0):
    """ Roll dice and calculate successes and returns a SuccessResult object
    attr -- attribute score
    bonus -- bonus success count
    n -- number of dice to roll
    """

    rolls = sorted(np.random.randint(1, high=11, size=n))
    successes = 0
    negations = 0
    for roll in rolls:
        if roll == 10:
            negations += 1
        elif roll <= attr:
            successes += 1

    return SuccessResult(rolls, successes, bonus, negations, min_success)
