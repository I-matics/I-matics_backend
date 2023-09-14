import math


def distance_based_risk(distance, exponential_indice=0.34):
    total_distance = distance
    if distance < 10:
        return math.exp(distance**exponential_indice) / 10
    distance_score = math.exp(distance**exponential_indice)
    # print(distance_score/total_distance)
    return distance_score / total_distance  # Normalize by total distance
