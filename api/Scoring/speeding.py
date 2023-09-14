from api.Scoring.helper_functions import overspeed_intervals
import pandas as pd
import math


def get_speed_from_interval(speed_data, interval):
    return speed_data[interval]


def get_average_speed(speed_data, intervals):
    total = 0
    for interval in intervals:
        total += get_speed_from_interval(speed_data, interval)
    return total / len(intervals)


def overspeed_score(speed_data, overspeeding_weight, speed_limit, speed_exponent):
    intervals = overspeed_intervals(speed_data, overspeed_limit=speed_limit)
    speeding_events = len(intervals)
    score = speeding_events * overspeeding_weight
    expscore = 0
    print("No of overspeeding events: ", speeding_events)
    for interval in intervals:
        avg_speed = get_average_speed(speed_data, interval)
        delta_speed = avg_speed - speed_limit
        print("Delta speed: ", delta_speed)
        expscore += math.exp(delta_speed**speed_exponent) / 100
    return score + expscore
