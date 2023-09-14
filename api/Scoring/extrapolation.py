import numpy as np
from scipy.interpolate import CubicSpline


def create_smooth_curve2(speed_data, original_frequency, target_frequency):
    original_time = np.arange(0, len(speed_data)) / original_frequency
    target_time = np.arange(0, len(speed_data) - 1, 1 / target_frequency)
    interpolated_speed = np.interp(target_time, original_time, speed_data)
    return target_time, interpolated_speed


def create_smooth_curve(speed_data, original_frequency=1, target_frequency=50):
    original_time = np.arange(0, len(speed_data)) / original_frequency
    spline = CubicSpline(original_time, speed_data)
    target_time = np.arange(0, len(speed_data) - 1, 1 / target_frequency)
    interpolated_speed = spline(target_time)
    return target_time, interpolated_speed
