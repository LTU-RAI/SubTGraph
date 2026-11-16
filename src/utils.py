import math, random, string, yaml, numpy as np, tkinter as tk

from datetime import datetime
from graph.shape import EmptyShape
from tkinter import ttk, font as tkfont

###

# !!! PATH TO CONFIGURATION !!!
with open('config/custom.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Obtain limits of grid as square root of the world length
grid_rows = grid_columns = int(math.sqrt(np.random.randint(low=config["world_min_length"][0], high=config["world_min_length"][1]+1, size=1)[0]))

# Check empty shape
isEmptyShape =   lambda obj:     isinstance(obj, EmptyShape)

# Check openings of the asset based on direction array
isOpenWest =     lambda openings:   "w" in openings
isOpenNorth =    lambda openings:   "n" in openings
isOpenSouth =    lambda openings:   "s" in openings
isOpenEast =     lambda openings:   "e" in openings

# Check the limits of the grid based on coordinates
isLimitNorth =    lambda idx:     idx == 0
isLimitWest  =    lambda jdx:     jdx == 0
isLimitSouth =    lambda idx:     idx == grid_rows - 1
isLimitEast  =    lambda jdx:     jdx == grid_columns - 1

isLimitNorthWest  = lambda idx, jdx: isLimitNorth(idx) and isLimitWest(jdx)
isLimitNorthEast  = lambda idx, jdx: isLimitNorth(idx) and isLimitEast(jdx)
isLimitSouthWest  = lambda idx, jdx: isLimitSouth(idx) and isLimitWest(jdx)
isLimitSouthEast  = lambda idx, jdx: isLimitSouth(idx) and isLimitEast(jdx)

# Get values at specified directions
getValueNorth = lambda matrix, idx, jdx: matrix[idx-1][jdx]
getValueSouth = lambda matrix, idx, jdx: matrix[idx+1][jdx]
getValueWest  = lambda matrix, idx, jdx: matrix[idx][jdx-1]
getValueEast  = lambda matrix, idx, jdx: matrix[idx][jdx+1]

###

def get_random_id() -> str:
    """
    Generate random 32 length string.

    Returns
    -------
    out : str
        Random 32 length string
    """
    return ''.join(random.choice(string.ascii_letters) for i in range(32))


def get_datetime_id(prefix="subtgraph") -> str:
    """
    Generate date and time string.

    Parameters
    -------
    prefix : str, optional
        Prefix of the string
    
    Returns
    -------
    out : str
        Date and Time string
    """
        
    # Get current date and time
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Combine prefix with the formatted date and time
    return f"{prefix}_{current_time}"


def intersection_over_union(mat1, mat2):
    """Compute IoU for binary occupancy matrices (1 = occupied, 0 = free)."""
    mat1 = (mat1 > 0).float()
    mat2 = (mat2 > 0).float()
    
    intersection = torch.sum((mat1 * mat2))
    union = torch.sum((mat1 + mat2) > 0)
    
    if union == 0:
        return torch.tensor(1.0)  # both empty, treat as identical
    return intersection / union


def visualize(environment, title="Generated environment"):
    content = environment if isinstance(environment, str) else str(environment)
    accepted = {"value": False}

    window = tk.Tk()
    window.title(title)
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    # Maximize a normal decorated window (title bar and window controls remain).
    window.geometry(f"{int(screen_width * 0.9)}x{int(screen_height * 0.9)}")
    try:
        window.state("zoomed")
    except tk.TclError:
        try:
            window.attributes("-zoomed", True)
        except tk.TclError:
            window.geometry(f"{screen_width}x{screen_height}+0+0")
    window.minsize(500, 350)
    window.resizable(True, True)
    window.configure(background="#000000")
    window.rowconfigure(0, weight=1)
    window.columnconfigure(0, weight=1)

    style = ttk.Style(window)
    style.configure("Black.TFrame", background="#000000")
    frame = ttk.Frame(window, padding=12, style="Black.TFrame")
    frame.grid(row=0, column=0, sticky="nsew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    text = tk.Text(
        frame,
        wrap="none",
        undo=False,
        padx=8,
        pady=8,
        borderwidth=0,
        background="#000000",
        foreground="#FFFFFF",
        insertbackground="#FFFFFF",
        selectbackground="#555555",
        spacing1=0,
        spacing2=0,
        spacing3=0,
    )
    text.grid(row=0, column=0, sticky="nsew")
    text.insert("1.0", content)
    text.configure(state="disabled")

    fixed_font = tkfont.nametofont("TkFixedFont")
    display_font = tkfont.Font(
        root=window,
        family=fixed_font.actual("family"),
        size=18,
        weight="bold",
    )
    text.configure(font=display_font)

    buttons = ttk.Frame(frame, style="Black.TFrame")
    buttons.grid(row=1, column=0, sticky="e", pady=(10, 0))

    def finish(value):
        accepted["value"] = value
        window.destroy()

    ttk.Button(buttons, text="Reject", command=lambda: finish(False)).pack(
        side="right", padx=(8, 0)
    )
    ttk.Button(buttons, text="Accept", command=lambda: finish(True)).pack(side="right")

    def fit_text():
        # Tk only reports the final client area after the window manager has
        # mapped/maximized the window, so this is scheduled after it settles.
        lines = content.split("\n")
        available_width = max(1, text.winfo_width() - 20)
        available_height = max(1, text.winfo_height() - 20)

        # Negative Tk font sizes are pixel sizes. Binary-search for the largest
        # bold size that fits, rather than rounding down to whole point sizes.
        low = 1
        high = max(1, min(120, available_height // max(1, len(lines)) + 1))
        fitted_size = 1
        while low <= high:
            size = (low + high) // 2
            display_font.configure(size=-size)
            widest_line = max((display_font.measure(line) for line in lines), default=0)
            total_height = display_font.metrics("linespace") * max(1, len(lines))
            if widest_line <= available_width and total_height <= available_height:
                fitted_size = size
                low = size + 1
            else:
                high = size - 1
        display_font.configure(size=-fitted_size)

    # Closing the window is equivalent to rejecting this environment.
    window.protocol("WM_DELETE_WINDOW", lambda: finish(False))
    window.bind("<Escape>", lambda _event: finish(False))
    window.after(250, fit_text)
    window.mainloop()
    return accepted["value"]