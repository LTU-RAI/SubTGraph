import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

def display_matrix(matrix, highlights=None):
    """
    Display a matrix with optional highlighted cells.
    
    Args:
    - matrix (2D list or np.array): The matrix to display.
    - highlights (dict): Optional. Keys are (row, col) tuples, values are color strings.
    """
    matrix = np.array(matrix)
    nrows, ncols = matrix.shape

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(ncols, nrows))
    ax.set_xlim(0, ncols)
    ax.set_ylim(0, nrows)
    ax.invert_yaxis()
    ax.axis('off')  # Hide the axes

    # Draw each cell
    for i in range(nrows):
        for j in range(ncols):
            # Check if this cell is highlighted
            color = highlights.get((i, j), 'white') if highlights else 'white'
            # Draw rectangle
            rect = plt.Rectangle((j, i), 1, 1, facecolor=color, edgecolor='black')
            ax.add_patch(rect)
            # Add number in center
            ax.text(j + 0.5, i + 0.5, str(matrix[i, j]),
                    va='center', ha='center', color='black', fontsize=24)

    plt.tight_layout()
    plt.show()


# Figure 1
# matrix = [
#     [0, 0, 0, 0, "$O^N_2$", 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, "$O^N_1$", 0],
#     [0, 0, "$C_{tjun^n}$", 0, 0, 0, 0, 0, 0, 0],
#     [0, "$C_{tjun^n}$", "$C_{tjun^n}$", "$C_{tjun^n}$", 0, 0, "$S^N$", 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, "$O^N_3$", 0],
# ]

# highlights = {
#     (3, 6): 'lightblue',
#     (0, 4): 'lightgreen',
#     (1, 8): 'lightgreen',
#     (4, 8): 'lightgreen',
#     (2, 2): 'lightcoral',
#     (3, 1): 'lightcoral',
#     (3, 2): 'lightcoral',
#     (3, 3): 'lightcoral',
# }

# Figure 2
# matrix = [
#     [0, "$A^N_2$", 0, 0, "$O^N_2$", 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, "$O^N_1$", 0],
#     [0, 0, "$C_{tjun^n}$", 0, 0, 0, 0, 0, 0, 0],
#     [0, "$C_{tjun^n}$", "$C_{tjun^n}$", "$C_{tjun^n}$", 0, 0, "$S^N$", 0, 0, 0],
#     ["$A^N_1$", 0, 0, 0, 0, 0, 0, 0, "$O^N_3$", 0],
# ]

# highlights = {
#     (0, 1): 'khaki',
#     (4, 0): 'khaki',

#     (2, 5): 'azure',
#     (2, 6): 'azure',
#     (3, 5): 'azure',
#     (3, 6): 'lightblue',
#     (4, 5): 'azure',
#     (4, 6): 'azure',

#     (0, 3): 'honeydew',
#     (0, 4): 'lightgreen',
#     (0, 5): 'honeydew',
#     (1, 3): 'honeydew',
#     (1, 4): 'honeydew',
#     (1, 5): 'honeydew',

#     (0, 7): 'honeydew',
#     (0, 8): 'honeydew',
#     (0, 9): 'honeydew',
#     (1, 7): 'honeydew',
#     (1, 8): 'lightgreen',
#     (1, 9): 'honeydew',
#     (2, 7): 'lightcyan',
#     (2, 8): 'honeydew',
#     (2, 9): 'honeydew',
    
#     (3, 7): 'lightcyan',
#     (3, 8): 'honeydew',
#     (3, 9): 'honeydew',
#     (4, 7): 'lightcyan',
#     (4, 8): 'lightgreen',
#     (4, 9): 'honeydew',

#     (2, 1): 'mistyrose',
#     (2, 2): 'lightcoral',
#     (2, 3): 'mistyrose',
#     (3, 1): 'lightcoral',
#     (3, 2): 'lightcoral',
#     (3, 3): 'lightcoral',
#     (4, 1): 'mistyrose',
#     (4, 2): 'mistyrose',
#     (4, 3): 'mistyrose',
# }


# Figure 4
# matrix = [
#     [0, "$A^N_2$", 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 1, 1, 0, 0, 0, 0, 1, "$O^N_1$", 0],
#     [0, 0, "$C_{tjun^n}$", 0, 0, 0, 1, 1, 0, 0],
#     [0, 0, 0, 0, 0, 0, "$S^N$", 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
# ]

# highlights = {
#     (3, 6): 'lightblue',
#     (2, 6): 'thistle',
#     (2, 7): 'thistle',
#     (1, 7): 'thistle',
#     (1, 8): 'lightgreen',

#     (0, 1): 'khaki',
#     (1, 1): 'thistle',
#     (1, 2): 'thistle',
#     (2, 2): 'lightcoral',
# }

# Figure 5
matrix = [
    [0, "$A^N_2$", 0, 0, "$O^N_2$", 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 1, 1, 0, 1, "$O^N_1$", 0],
    [0, 0, "$C_{tjun^n}$", 0, 0, 1, 1, 1, 0, 0],
    [1, "$C_{tjun^n}$", "$C_{tjun^n}$", "$C_{tjun^n}$", 1, 1, "$S^N$", 0, 0, 0],
    ["$A^N_1$", 0, 0, 0, 0, 0, 1, 1, "$O^N_3$", 0],
]

highlights = {
    (1, 4): 'thistle',
    (1, 5): 'thistle',
    (2, 5): 'thistle',

    (3, 4): 'thistle',
    (3, 5): 'thistle',
    (3, 6): 'lightblue',
    (4, 6): 'thistle',
    (4, 7): 'thistle',

    (0, 4): 'lightgreen',
    (1, 8): 'lightgreen',
    (4, 8): 'lightgreen',

    (4, 0): 'khaki',

    (3, 6): 'lightblue',
    (2, 6): 'thistle',
    (2, 7): 'thistle',
    (1, 7): 'thistle',
    (1, 8): 'lightgreen',

    (0, 1): 'khaki',
    (1, 1): 'thistle',
    (1, 2): 'thistle',
    (2, 2): 'lightcoral',

    (3, 1): 'lightcoral',
    (3, 0): 'thistle',

    (3, 2): 'lightcoral',
    (3, 3): 'lightcoral',
}

display_matrix(matrix, highlights)

# # Figure 3
# matrix = np.round(differential_sum((5, 10), (0, 8)), 2)

# norm = plt.Normalize(vmin=np.min(matrix), vmax=np.max(matrix))
# cmap = cm.get_cmap('coolwarm')

# nrows, ncols = matrix.shape
# fig, ax = plt.subplots(figsize=(ncols, nrows))
# ax.set_xlim(0, ncols)
# ax.set_ylim(0, nrows)
# ax.invert_yaxis()
# ax.axis('off')  # Hide the axes

# Draw each cell with color based on value
# for i in range(nrows):
#     for j in range(ncols):
#         value = matrix[i, j]
#         color = cmap(norm(value))  # Map value to colormap
#         rect = plt.Rectangle((j, i), 1, 1, facecolor=color, edgecolor='black')
#         ax.add_patch(rect)
#         ax.text(j + 0.5, i + 0.5, f"{value:.2f}",
#                 va='center', ha='center', color='black', fontsize=24)

# plt.tight_layout()
# plt.show()