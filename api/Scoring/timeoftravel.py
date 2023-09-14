from api.Scoring.helper_functions import parse_time
import math

time_ref = {
    '0': 0.8,
    '1': 0.8,
    '2': 0.8,
    '3': 0.9,
    '4': 0.9,
    '5': 0.7,
    '6': 0.7,
    '7': 0.6,
    '8': 0.6,
    '9': 0.4,
    '10': 0.4,
    '11': 0.3,
    '12': 0.3,
    '13': 0.3,
    '14': 0.3,
    '15': 0.4,
    '16': 0.4,
    '17': 0.6,
    '18': 0.6,
    '19': 0.7,
    '20': 0.7,
    '21': 0.5,
    '22': 0.5,
    '23': 0.4
}
def time_based_risk(timedata, exponential_indice=2):
    intial_time = parse_time(timedata[0])
    final_time = parse_time(timedata[len(timedata) - 1])
    totalhours = (final_time.hour - intial_time.hour)
    time_score = 0
    for i in range(totalhours+1):
        if totalhours == i:
            time_score += (time_ref[str(i+intial_time.hour)]+ math.exp(i**exponential_indice))*(final_time.minute - intial_time.minute)/60
        else:
            time_score += time_ref[str(i+intial_time.hour)]+ math.exp(i**exponential_indice)

    
    return time_score
