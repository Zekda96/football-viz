import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch, Standardizer

# --------------------------------- DATA
data = pd.read_csv("data/20240119_events.csv")

#### Fig parameters
# --- Figure: Pitch


# Events
event1_marker_color1 = '#0b4393'
event2_marker_color1 = '#B5B4B2'
event_line_width1 = 1.8

event_marker_width1 = 12

is_line_transparent = True
line_alpha_start = 0.1
line_alpha_end = 1
#### FIGURE

pitch = VerticalPitch(
            # axis=True,
            # label=True,
            # tick=True,
            goal_type='box',
            line_color='#03191E',
            # line_alpha=0.5,
            linewidth=0.8,

            # bring the left axis in 10 data units (reduce the size)
            pad_left=0,
            # bring the right axis in 10 data units (reduce the size)
            pad_right=0,
            # extend the top axis 10 data units
            pad_top=0,
            # extend the bottom axis 20 data units
            pad_bottom=-35,
        )

fig, axs = pitch.grid(
            nrows=1, ncols=2,
            figheight=10,

            #title_height=title_h,  # the title takes up 15% of the fig height
            #grid_height=grid_h,  # the grid takes up 71.5% of the figure height
           # endnote_height=endnote_h,  # endnote takes up 6.5% of the figure height
            #
            #grid_width=grid_w,  # gris takes up 95% of the figure width
            #
            # # 1% of fig height is space between pitch and title
            #title_space=title_space,
            #
            # # 1% of fig height is space between pitch and endnote
           # endnote_space=endnote_space,
            #
            #space=space,  # 5% of grid_height is reserved for space between axes
            #
            # # centers the grid horizontally / vertically
            #left=left_p,
            bottom=None,
            axis=False,
)

axs['pitch'][0].set_facecolor('#faf9f4')

# ------------ Add Credits
# Twitter Account
tw_account = axs['title'].text(
    1,
    .95,
    '@DGCFutbol',
    va='top',
    ha='right',
    fontsize=15.5,
    weight='bold',
    # ontproperties=robotto_regular.prop,
    # color='#941C2F',
    color=event1_marker_color1,
    alpha=1,
)

# Source label
source = axs['title'].text(
    1,
    .75,
    'Datos y Gráficos: @DGCFutbol',
    va='top',
    ha='right',
    fontsize=13,
    # weight='bold',
    # ontproperties=robotto_regular.prop,
    color='#030303',
    # color=event1_marker_color1,
    alpha=0.7,
)

plt.savefig('filename.png',
            bbox_inches='tight',
            dpi=250
            )
