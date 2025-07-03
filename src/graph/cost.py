import numpy as np
# import matplotlib.cm as cm
# import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter

###

def linear_model_minimal(x, m, d):
    return m * x + d

def linear_model(x, m, d, _, __, x0):
    return m * (x - x0) + d

def fit_linear_through_points(points, num_points=10):
    points = sorted(points)
    x_data, y_data = zip(*points)
    x_data = np.array(x_data)
    y_data = np.array(y_data)

    # m, d, _, __, x0
    # p0 = [1.0, 0.0, 0, 0, np.mean(x_data)]
    p0 = [1.0, 0.0]

    try:
        popt, _ = curve_fit(linear_model_minimal, x_data, y_data, p0=p0)
    except RuntimeError:
        print("Fit failed")
        return []

    x_fit = np.linspace(min(x_data), max(x_data), num_points)
    y_fit = linear_model_minimal(x_fit, *popt)
    return list(zip(x_fit, y_fit))

###

def parabola_pos_model_minimal(x, a, x0, d):
    return a * (x - x0)**2 + d

def parabola_pos_model(x, a, _, __, d, x0):
    return a * (x - x0)**2 + d

def fit_parabola_pos_through_points(points, num_points=10):
    points = sorted(points)
    x_data, y_data = zip(*points)
    x_data = np.array(x_data)
    y_data = np.array(y_data)

    p0 = [1.0, 0, 0, 0.0, np.mean(x_data)]

    try:
        popt, _ = curve_fit(parabola_pos_model_minimal, x_data, y_data, p0=p0)
    except RuntimeError:
        print("Fit failed")
        return []

    x_fit = np.linspace(min(x_data), max(x_data), num_points)
    y_fit = parabola_pos_model(x_fit, *popt)
    return list(zip(x_fit, y_fit))

###

def parabola_neg_model_minimal(x, a, x0, d):
    return -abs(a) * (x - x0)**2 + d

def parabola_neg_model(x, a, _, __, d, x0):
    return -abs(a) * (x - x0)**2 + d

def fit_parabola_neg_through_points(points, num_points=10):
    points = sorted(points)
    x_data, y_data = zip(*points)
    x_data = np.array(x_data)
    y_data = np.array(y_data)

    p0 = [-1.0, 0, 0, 0.0, np.mean(x_data)]

    try:
        popt, _ = curve_fit(parabola_neg_model_minimal, x_data, y_data, p0=p0)
    except RuntimeError:
        print("Fit failed")
        return []

    x_fit = np.linspace(min(x_data), max(x_data), num_points)
    y_fit = parabola_neg_model(x_fit, *popt)
    return list(zip(x_fit, y_fit))

###

def sine_model(x, _, b, c, d, x0):
    return b * np.sin(c * (x - x0)) + d

def fit_sine_through_points(points, num_points=10):
    points = sorted(points)
    x_data, y_data = zip(*points)
    x_data = np.array(x_data)
    y_data = np.array(y_data)

    p0 = [0, 1.0, 2*np.pi/5, 0.0, np.mean(x_data)]  # a is unused

    try:
        popt, _ = curve_fit(sine_model, x_data, y_data, p0=p0)
    except RuntimeError:
        print("Fit failed")
        return []

    x_fit = np.linspace(min(x_data), max(x_data), num_points)
    y_fit = sine_model(x_fit, *popt)
    return list(zip(x_fit, y_fit))

###

def parabola_pos_sine_model(x, a, b, c, d, x0):
    return a * (x - x0)**2 + b * np.sin(c * (x - x0)) + d

def fit_parabola_pos_sine_through_points(points, num_points=10):
    points = sorted(points)
    x_data, y_data = zip(*points)
    x_data = np.array(x_data)
    y_data = np.array(y_data)

    p0 = [1.0, 0.1, 2*np.pi/5, 0.0, np.mean(x_data)]

    try:
        popt, _ = curve_fit(parabola_pos_sine_model, x_data, y_data, p0=p0)
    except RuntimeError:
        print("Fit failed")
        return []

    x_fit = np.linspace(min(x_data), max(x_data), num_points)
    y_fit = parabola_pos_sine_model(x_fit, *popt)
    return list(zip(x_fit, y_fit))

###

def parabola_neg_sine_model(x, a, b, c, d, x0):
    return -abs(a) * (x - x0)**2 + b * np.sin(c * (x - x0)) + d

def fit_parabola_neg_sine_through_points(points, num_points=10):
    points = sorted(points)
    x_data, y_data = zip(*points)
    x_data = np.array(x_data)
    y_data = np.array(y_data)

    p0 = [-1.0, 0.1, 2*np.pi/5, 0.0, np.mean(x_data)]

    try:
        popt, _ = curve_fit(parabola_neg_sine_model, x_data, y_data, p0=p0)
    except RuntimeError:
        print("Fit failed")
        return []

    x_fit = np.linspace(min(x_data), max(x_data), num_points)
    y_fit = parabola_neg_sine_model(x_fit, *popt)
    return list(zip(x_fit, y_fit))

###

def draw_path(heatmap, path_points, weight=1.0):
    for x, y in path_points:
        if 0 <= x < heatmap.shape[1] and 0 <= y < heatmap.shape[0]:
            heatmap[int(y), int(x)] -= weight

def create_heatmaps(matrix_shape, initial, objectives, constraints, blur_sigma=2.0):
    combined_heatmap = np.zeros(matrix_shape)
    individual_heatmaps = []

    for target in objectives:
        heatmap = np.ones(matrix_shape) * 5  # Higher value = less visited

        path_array = [fit_linear_through_points([initial, target])]
        
                    #  [  # Positive/Negative parabolic sines for constraints
                    #   fit_parabola_neg_sine_through_points([initial, target, *constraints]),
                    #   fit_parabola_pos_sine_through_points([initial, target, *constraints]),
                    #  ] if len(constraints) > 0 else \
                    #  [fit_linear_through_points([initial, target])]
        
        for path in path_array:
            draw_path(heatmap, path, weight=0.2)

        heatmap = gaussian_filter(heatmap, sigma=blur_sigma)
        individual_heatmaps.append(heatmap)
        combined_heatmap += heatmap

    return individual_heatmaps, combined_heatmap