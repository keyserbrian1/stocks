from django.db import connection

import math

class HistoryFunction(object):
    def __init__(self, function, name, length=5, small_threshold=.01, medium_threshold=.05, large_threshold=.1):
        self.function = function
        self.length = length + 1
        self.small_threshold = small_threshold
        self.medium_threshold = medium_threshold
        self.large_threshold = large_threshold
        self.name = name
    def __call__(self, company):
        with connection.cursor() as c:
            c.execute("select orders.price from trading_order as orders where orders.company_id=%s and orders.open=false order by orders.created_at DESC limit %s",[company.id, self.length])
            data = c.fetchall()
        while len(data) < self.length:
            data.append((100,))
        diffs = []
        for i in range(self.length-1):  #Map diffs to [-4,4], based on direction and strength
            diff = data[i][0]-data[i+1][0]
            diff_value = 1
            diff_value += diff/data[i][0] > self.small_threshold
            diff_value += diff/data[i][0] > self.medium_threshold
            diff_value += diff/data[i][0] > self.large_threshold
            diff_value *= cmp(diff, 0)
            diffs.append(diff_value)
        return self.function(diffs, data)

def rising(diffs, data):
    return sum(diffs)/40 +.5
def slow_rising(diffs, data):
    res = 0
    for diff in diffs:
        res += diff-cmp(diff,0) #reduces magnitude of diffs by one
    return res/30+.5
def falling(diffs, data):
    return -(sum(diffs)/40) +.5
def slow_falling(diffs, data):
    res = 0
    for diff in diffs:
        res += diff-cmp(diff,0) #reduces magnitude of diffs by one
    return -(res/30)+.5
def now_rising(diffs, data):
    return -diffs[0] - diffs[1] + diffs[3] + diffs[4]
def now_falling(diffs, data):
    return diffs[0] + diffs[1] - diffs[3] - diffs[4]
def accelerating(diffs, data):
    return (diffs[4]-diffs[0])/8+.5
def decelerating(diffs, data):
    return (diffs[0]-diffs[4])/8+.5
def steady_growth(diffs, data):
    res = 0
    for diff in diffs:
        res += abs(diff-1)
    return 1-(res/25)


_func = [
    (rising, 4, "rising"),
    (slow_rising, 4, "slow_rising"),
    (falling, 1, "falling"),
    (slow_falling, 1, "slow_falling"),
    (now_rising, 5, "now_rising"),
    (now_falling, 1, "now_falling"),
    (accelerating, 3, "accelerating"),
    (decelerating, 1, "decelerating"),
    (steady_growth, 1, "steady_growth")
]

functions = []
for function in _func:
    functions.append((HistoryFunction(function[0], function[2]+"_normal"),function[1]+3))
    functions.append((HistoryFunction(function[0], function[2]+"_large", small_threshold = .02, medium_threshold = .1, large_threshold = .2),function[1]+1))
    functions.append((HistoryFunction(function[0], function[2]+"_small", small_threshold = .005, medium_threshold = .025, large_threshold = .05),function[1]+1))
