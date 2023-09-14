import math


def calculate_acceleration_magnitude(ax, ay):
    return (ax**2 + ay**2) ** 0.5


def capture_peaks_and_differentiate(ax_data, ay_data, speed_data, threshold=15):
    events = []
    is_hard_braking = False
    is_hard_acceleration = False
    for i in range(len(ax_data)):
        ax = ax_data[i]
        ay = ay_data[i]
        acceleration_magnitude = calculate_acceleration_magnitude(ax, ay)
        speed_change = (
            speed_data[i + 1] - speed_data[i] if (i + 1) < len(speed_data) else 0
        )
        if acceleration_magnitude > threshold:
            if speed_change <= 0:
                is_hard_braking = True
            else:
                is_hard_acceleration = True
        else:
            if is_hard_braking:
                events.append("Hard Braking")
                is_hard_braking = False
            elif is_hard_acceleration:
                events.append("Hard Acceleration")
                is_hard_acceleration = False
    return events


def capture_peaks_and_differentiate2(
    ax_data,
    ay_data,
    speed_data,
    acc_exponent,
    brak_exponent,
    threshold=15,
    time=1.0,
    data_freq=50,
):
    time_interval = time * data_freq
    events = []
    acc_score = 0
    brak_score = 0
    is_hard_braking = False
    is_hard_acceleration = False
    time_since_last_event = 0.0

    for i in range(len(ax_data)):
        ax = ax_data[i]
        ay = ay_data[i]

        acceleration_magnitude = calculate_acceleration_magnitude(ax, ay)
        speed_change = (
            speed_data[i + 1] - speed_data[i] if (i + 1) < len(speed_data) else 0
        )

        if acceleration_magnitude > threshold:
            if speed_change <= 0:
                is_hard_braking = True
                acc_dif = acceleration_magnitude - threshold
                acc_score += math.exp(acc_dif**brak_exponent) / 100
            else:
                is_hard_acceleration = True
                acc_dif = acceleration_magnitude - threshold
                brak_score += math.exp(acc_dif**acc_exponent) / 100
            time_since_last_event = 0.0
        else:
            time_since_last_event += 1.0

            if time_since_last_event >= time_interval:
                if is_hard_braking:
                    events.append("Hard Braking")
                elif is_hard_acceleration:
                    events.append("Hard Acceleration")
                is_hard_braking = False
                is_hard_acceleration = False
    return events, acc_score, brak_score
