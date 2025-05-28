import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt

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

def bezier_model(x, x0, x1, cx_offset, cy_offset, _):
    t = (x - x0) / (x1 - x0)
    cx = (x0 + x1) / 2 + cx_offset
    cy = cy_offset

    P0, P1, P2 = x0, cx, x1
    return (1 - t)**2 * P0 + 2 * (1 - t) * t * P1 + t**2 * P2

def cubic_spline_model(x, spline_x, spline_y, _, __, ___):
    return spline_y(spline_x(x))

###

def draw_path(heatmap, path_points, weight=1.0):
    for x, y in path_points:
        if 0 <= x < heatmap.shape[1] and 0 <= y < heatmap.shape[0]:
            heatmap[int(y), int(x)] -= weight

def create_heatmaps(matrix_shape, initial, objectives, constraints, blur_sigma=0.5):
    combined_heatmap = np.zeros(matrix_shape)
    individual_heatmaps = []

    for target in objectives:
        heatmap = np.ones(matrix_shape) * 10  # Higher value = less visited

        path_array = [  # Positive/Negative parabolic sines for constraints
                      fit_parabola_neg_sine_through_points([initial, target, *constraints]),
                      fit_parabola_pos_sine_through_points([initial, target, *constraints]),
                     ] if len(constraints) > 0 else \
                     [fit_linear_through_points([initial, target])]
        
        for path in path_array:
            draw_path(heatmap, path, weight=0.2)

        heatmap = gaussian_filter(heatmap, sigma=blur_sigma)
        individual_heatmaps.append(heatmap)
        combined_heatmap += heatmap

    return individual_heatmaps, combined_heatmap

###

## With constraints
matrix_shape = (5, 10)
initial = (6, 1)
constraints = [(2, 2), (1, 1), (2, 1), (3, 1)]
objectives = [(1, 4), (0, 0)]
individual_heatmaps, combined_heatmap = create_heatmaps(matrix_shape, initial, objectives, constraints)

## Without constraints
matrix_shape = (5, 10)
initial = (6, 1)
constraints = []
objectives = [(4, 4), (8, 0), (8, 3)]
individual_heatmaps_no, combined_heatmap_no = create_heatmaps(matrix_shape, initial, objectives, constraints)

## Plot values
individual_heatmaps.extend(individual_heatmaps_no)
combined_heatmap += combined_heatmap_no

nodes = np.array([
    [
        ["", "", "", "", "", "", "", "", "", ""],
        ["", "$C_{tjun^n}$", "$C_{tjun^n}$", "$C_{tjun^n}$", "", "", "$S^N$", "", "", ""],
        ["", "", "$C_{tjun^n}$", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", "", "", ""],
        ["", "$A^N_2$", "", "", "", "", "", "", "", ""],
    ],
    [
        ["$A^N_1$", "", "", "", "", "", "", "", "", ""],
        ["", "$C_{tjun^n}$", "$C_{tjun^n}$", "$C_{tjun^n}$", "", "", "$S^N$", "", "", ""],
        ["", "", "$C_{tjun^n}$", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", "", "", ""],
    ],
    [
        ["", "", "", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "$S^N$", "", "", ""],
        ["", "", "", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", "", "", ""],
        ["", "", "", "", "$O^N_2$", "", "", "", "", ""],
    ],
    [
        ["", "", "", "", "", "", "", "", "$O^N_3$", ""],
        ["", "", "", "", "", "", "$S^N$", "", "", ""],
        ["", "", "", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", "", "", ""],
    ],
    [
        ["", "", "", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "$S^N$", "", "", ""],
        ["", "", "", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", "", "$O^N_1$", ""],
        ["", "", "", "", "", "", "", "", "", ""],
    ],
    [
        ["$A^N_1$", "", "", "", "", "", "", "", "$O^N_3$", ""],
        ["", "$C_{tjun^n}$", "$C_{tjun^n}$", "$C_{tjun^n}$", "", "", "$S^N$", "", "", ""],
        ["", "", "$C_{tjun^n}$", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", "", "$O^N_1$", ""],
        ["", "$A^N_2$", "", "", "$O^N_2$", "", "", "", "", ""],
    ],
])

highlights = [
    {
        (4, 1): 'purple',
        (1, 6): 'gray',
    },
    {
        (0, 0): 'purple',
        (1, 6): 'gray',
    },
    {
        (4, 4): 'purple',
        (1, 6): 'gray',
    },
    {
        (0, 8): 'purple',
        (1, 6): 'gray',
    },
    {
        (3, 8): 'purple',
        (1, 6): 'gray',
    },
    {
        (0, 0): 'purple',
        (4, 1): 'purple',
        (1, 6): 'gray',
        (4, 4): 'purple',
        (0, 8): 'purple',
        (3, 8): 'purple',
    }]

for mdx, matrix in enumerate([*individual_heatmaps, combined_heatmap]): # 

    norm = plt.Normalize(vmin=np.min(matrix), vmax=np.max(matrix))
    cmap = cm.get_cmap('coolwarm')

    nrows, ncols = matrix.shape
    fig, ax = plt.subplots(figsize=(ncols, nrows))
    ax.set_xlim(0, ncols)
    ax.set_ylim(0, nrows)
    # ax.invert_yaxis()
    ax.axis('off')  # Hide the axes

    # Draw each cell with color based on value
    for i in range(nrows):
        for j in range(ncols):
            value = matrix[i, j]
            color = highlights[mdx].get((i, j), cmap(norm(value)))  # Map value to colormap
            rect = plt.Rectangle((j, i), 1, 1, facecolor=color, edgecolor='black')
            ax.add_patch(rect)
            ax.text(j + 0.5, i + 0.5, str(nodes[mdx][i, j]),
                    va='center', ha='center', color='black', fontsize=24)

    plt.tight_layout()
    plt.show()
