import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch, Standardizer
from PIL import Image
# import datetime

# ----------------------------------------------------- MANUAL PARAMETERS
half_time = 60
invert_first_half = False

# ----------------------------------- Text
# Title
x_title = 0.11
y_title = 0.75
spacing = 0.27  # title to subtitle space

title_text = 'DT Jonathan Mendoza - La Concordia 2023'
# ---------------------------------- Events
# event1_marker_color1 = '#0b4393'
event1_marker_color1 = '#de9314'
event2_marker_color1 = '#B5B4B2'
event_line_width1 = 1.8

event_marker_width = 12

is_line_transparent = True
line_alpha_start = 0.05
line_alpha_end = 0.15

# ------------------------------------------------------------ DATA
data = pd.read_csv("data/20240119_events.csv")

# Sort values by time
df = data.sort_values(['Mins', 'Secs'], ascending=[True, True])
# Fix Missing Values
df.loc[:, ['X2', 'Y2']] = df[['X2', 'Y2']].apply(pd.to_numeric, errors='coerce')
df[['X2', 'Y2']] = df[['X2', 'Y2']].astype(float)
# Get 1st and 2nd Half values to invert coordinates
df1 = df[df['Mins'] < half_time]
df2 = df[df['Mins'] > half_time]
# Invert coordinates
if invert_first_half:
    df1[['X', 'Y', 'X2', 'Y2']] = 100 - df1[['X', 'Y', 'X2', 'Y2']]
else:
    df2.loc[:, ['X', 'Y', 'X2', 'Y2']] = 100 - df2.loc[:, ['X', 'Y', 'X2', 'Y2']]

df = pd.concat([df1, df2])

# Standardizer
standard = Standardizer(pitch_from='opta', pitch_to='statsbomb')


# ------------------------------------------------------------ FIGURE

pitch = VerticalPitch(
            # axis=True,
            # label=True,
            # tick=True,
            goal_type='box',
            line_color='#03191E',
            # line_alpha=0.5,
            linewidth=1.6,

            # bring the left axis in 10 data units (reduce the size)
            pad_left=0,
            # bring the right axis in 10 data units (reduce the size)
            pad_right=0,
            # extend the top axis 10 data units
            pad_top=0,
            # extend the bottom axis 20 data units
            pad_bottom=0,
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
            # left=0.1,
            bottom=None,
            axis=False,
)

fig.patch.set_facecolor('#faf9f4')
axs['pitch'][0].set_facecolor('#faf9f4')
axs['pitch'][1].set_facecolor('#faf9f4')

# -------------------------------------------- Add Passes into Final Third

pdf = df[df['Event'] == 'Pass']
pdf = pdf[(pdf['X'] < 66) & (pdf['X2'] >= 66)]

xstart, ystart = standard.transform(pdf['X'], pdf['Y'])
xend, yend = standard.transform(pdf['X2'], pdf['Y2'])

pitch.lines(
    xstart=xstart,
    ystart=ystart,
    xend=xend,
    yend=yend,
    ax=axs['pitch'][0],
    lw=3,
    color=event1_marker_color1,
    comet=True,
    transparent=True,
    alpha_start=line_alpha_start,
    alpha_end=line_alpha_end,
)

pitch.scatter(
    x=xend,
    y=yend,
    ax=axs['pitch'][0],
    s=event_marker_width,
    marker='o',
    facecolor=event1_marker_color1,
    # facecolor='#ef4146',
    zorder=2,
)
# ------------------------------------------------- Add Passes In Own Half
pdf = df[df['Event'] == 'Pass']
# pdf = pdf[(pdf['X'] < 50) & (pdf['X2'] < 50)]
pdf = pdf[(pdf['Player'] == '3 Loor') |
          (pdf['Player'] == '2 Castro') |
          (pdf['Player'] == '54 Hurt')
]

xstart, ystart = standard.transform(pdf['X'], pdf['Y'])
xend, yend = standard.transform(pdf['X2'], pdf['Y2'])

pitch.lines(
    xstart=xstart,
    ystart=ystart,
    xend=xend,
    yend=yend,
    ax=axs['pitch'][1],
    lw=3,
    color=event1_marker_color1,
    comet=True,
    transparent=True,
    alpha_start=line_alpha_start,
    alpha_end=line_alpha_end,
)

pitch.scatter(
    x=xend,
    y=yend,
    ax=axs['pitch'][1],
    s=event_marker_width,
    marker='o',
    facecolor=event1_marker_color1,
    # facecolor='#ef4146',
    zorder=2,
)

# --------------------------------------------------------------- Add Title

# Add team logo
image = Image.open('data/20240119_logo.png')
# newax = fig.add_axes([0.018, 0.855, 0.111, 0.111], anchor='W', zorder=1)
newax = fig.add_axes([0.018, 0.8555, 0.09, 0.09], anchor='W', zorder=1)
newax.imshow(image)
newax.axis('off')

title = axs['title'].text(
    x=x_title,
    y=y_title,
    s=title_text,
    size=20,
    ha='left',
    va='top',
    # weight='bold',
)

# Add subtitle 1
subtitle = axs['title'].text(
    x=x_title,
    y=y_title - spacing,
    s='Juego de Posesion y Directo | Victoria 4-1 vs. Japan Auto',
    size=16,
    ha='left',
    va='top',
    # fontproperties=font_bold.prop,
    color="#030303",
    alpha=0.6,
)
# Add subtitle 2

# subtitle2 = axs['title'].text(
#     x=x_text,
#     y=0.28,
#     s='Datos y Graficos: Daniel Granja C. @DGCFutbol',
#     size=14,
#     ha='left',
#     va='top',
#     # fontproperties=font_bold.prop,
#     color="#030303",
#     alpha=0.6,
# )


axs['title'].text(
    x=-0.025,
    y=0.5,
    s='.',
    alpha=0,
)

axs['title'].text(
    x=1.025,
    y=0.5,
    s='.',
    alpha=0,
)

# --------------------------------------------------------------- Add Credits
# Twitter Account
tw_account = axs['endnote'].text(
    1,
    .5,
    '@DGCFutbol',
    va='top',
    ha='right',
    fontsize=15.5,
    weight='bold',
    # ontproperties=robotto_regular.prop,
    # color='#941C2F',
    color=event1_marker_color1,
    # color='#0b4393',
    alpha=1,
)

# Source label
source = axs['endnote'].text(
    1,
    .95,
    'Datos y Gráficos: Daniel Granja C.',
    va='top',
    ha='right',
    fontsize=13,
    # weight='bold',
    # ontproperties=robotto_regular.prop,
    color='#030303',
    alpha=0.7,
)

plt.savefig('20240119_viz.png',
            bbox_inches='tight',
            dpi=250
            )
