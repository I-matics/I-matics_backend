import numpy as np
from scipy import signal
from ahrs.filters import ekf
import webbrowser
from datetime import datetime
import re

def fir_filter(doc, fir_cutoff=5, sampling_freq = 50, filter_order=25):
    oax, oay, oaz, ogx , ogy, ogz, omx, omy, omz = doc['ax'], doc['ay'], doc['az'], doc['gx'], doc['gy'], doc['gz'], doc['mx'], doc['my'], doc['mz']
    cutoff_frequency = fir_cutoff 
    sampling_frequency = sampling_freq  
    filter_order = filter_order  
    nyquist_frequency = 0.5 * sampling_frequency
    fir_coefficients = signal.firwin(filter_order, cutoff=cutoff_frequency / nyquist_frequency)

    ax = np.convolve(oax, fir_coefficients, mode='same')
    ay = np.convolve(oay, fir_coefficients, mode='same')
    az = np.convolve(oaz, fir_coefficients, mode='same')
    gx = np.convolve(ogx, fir_coefficients, mode='same')
    gy = np.convolve(ogy, fir_coefficients, mode='same')
    gz = np.convolve(ogz, fir_coefficients, mode='same')
    mx = np.convolve(omx, fir_coefficients, mode='same')
    my = np.convolve(omy, fir_coefficients, mode='same')
    mz = np.convolve(omz, fir_coefficients, mode='same')

    return ax, ay, az, gx, gy, gz, mx, my, mz


def ekf_filter(ax, ay, az, gx, gy, gz, mx, my, mz):
    initial_quart = estimate_initial_quaternion(magnetometer_data=[mx[0], my[0], mz[0]])
    estimated_quaternions = [initial_quart]
    model = ekf.EKF(acc=np.array([ax, ay, az]), gyro=np.array([gx, gy, gz]), mag=np.array([mx, my, mz]), magnetic_ref=-0.09, frequency=20)
    q_est = initial_quart
    q_est /= np.linalg.norm(q_est)
    for i in range(1,len(ax)):
        q_est = model.update(acc=[ax[i], ay[i], az[i]], mag=[mx[i], my[i], mz[i]], gyr=[gx[i], gy[i], gz[i]], q=q_est)
        estimated_quaternions.append(q_est)

    data = {'x':[], 'y':[], 'z':[]}
    rotated = []
    for i in range(len(ax)):
        rotated_points = rotateframe(estimated_quaternions[i], np.array([ax[i], ay[i], az[i]]))
        rotated.append(rotated_points)
        data['x'].append(rotated_points[0])
        data['y'].append(rotated_points[1])
        data['z'].append(rotated_points[2])
    return data['x'], data['y'], data['z']

def overspeed_intervals(speed_data, overspeed_limit=100, interval_duration=50):
    overspeed_intervals = []
    current_interval = []
    current_time = 0
    for speed in speed_data:
        if speed > overspeed_limit:
            current_interval.append(current_time)
        current_time += 1

        if current_time % interval_duration == 0:
            if current_interval:
                overspeed_intervals.append(current_interval)
            current_interval = []
    
    return overspeed_intervals

def extract_lat_long(input_string):
    pattern = r"lat:\s*([\d.]+),\s*long:\s*([\d.]+)"
    match = re.search(pattern, input_string)

    if match:
        latitude = float(match.group(1))
        longitude = float(match.group(2))
        return latitude, longitude
    else:
        print("Pattern not found in the input string.")
        return None, None


def rotateframe(quat, cartesianPoints):
    quat /= np.linalg.norm(quat)
    R = np.array([
        [1 - 2*(quat[2]**2 + quat[3]**2), 2*(quat[1]*quat[2] - quat[0]*quat[3]), 2*(quat[1]*quat[3] + quat[0]*quat[2])],
        [2*(quat[1]*quat[2] + quat[0]*quat[3]), 1 - 2*(quat[1]**2 + quat[3]**2), 2*(quat[2]*quat[3] - quat[0]*quat[1])],
        [2*(quat[1]*quat[3] - quat[0]*quat[2]), 2*(quat[2]*quat[3] + quat[0]*quat[1]), 1 - 2*(quat[1]**2 + quat[2]**2)]
    ])
    rotatedPoints = np.dot(cartesianPoints, R.T)
    
    return rotatedPoints

def calculate_exponential_score(risk_score, base=2, exponent_multiplier=0.1):
    final_score = 100 * (base ** (-exponent_multiplier * risk_score))
    final_score = max(0, min(100, final_score))
    
    return final_score

def parse_time(time_str):
    try:
        parsed_time = datetime.strptime(time_str, '%H:%M:%S').time()
        return parsed_time
    except ValueError:
        print("Invalid time format")
        return None
    
def estimate_initial_quaternion(magnetometer_data):
    magnetometer_data /= np.linalg.norm(magnetometer_data)
    reference_magnetic_field = np.array([0, 0, 1.0])
    rotation_axis = np.cross(magnetometer_data, reference_magnetic_field)
    rotation_angle = np.arccos(np.dot(magnetometer_data, reference_magnetic_field))
    initial_quaternion = np.array([np.cos(rotation_angle / 2.0),
                                   rotation_axis[0] * np.sin(rotation_angle / 2.0),
                                   rotation_axis[1] * np.sin(rotation_angle / 2.0),
                                   rotation_axis[2] * np.sin(rotation_angle / 2.0)])

    return initial_quaternion