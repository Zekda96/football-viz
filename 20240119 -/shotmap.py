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
bg_color = '#faf9f4'
# Title
x_title = 0.16
y_title = 0.85
spacing = 0.43  # title to subtitle space

title_text = 'DT Jonathan Mendoza - La Concordia 2023'

# Fig Titles
fig_fontsize = 12
# ---------------------------------- Events
# event1_marker_color1 = '#0b4393'
event1_marker_color1 = '#de9314'
event2_marker_color1 = '#B5B4B2'
event_line_width1 = 1.8

event_marker_width = 12
event_marker_width2 = 18

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


# ------------------------------------------------------------- CREATE FIGURE
fig = plt.figure(layout='constrained', figsize=(9, 4))
fig.patch.set_facecolor('#faf9f4')

ax_title = fig.add_axes([0, 1.05, 1, 0.2], anchor='SW', zorder=1)
ax_title.axis('off')
ax_annotate = fig.add_axes([0, -0.14, 1, 0.125], anchor='NW', zorder=1)
ax_annotate.axis('off')

subfigs = fig.subfigures(1, 2, wspace=0.07, width_ratios=[6, 3])
axsLeft = subfigs[0].subplots(1, 2)
axsRight = subfigs[1].subplots(2, 1)

pitch = VerticalPitch(
            # axis=True,
            # label=True,
            # tick=True,
            goal_type='box',
            line_color='#03191E',
            # line_alpha=0.5,
            linewidth=1.6,
        )

pitch.draw(ax=axsLeft[0])
pitch.draw(ax=axsLeft[1])

axsLeft[0].set_facecolor(bg_color)
axsLeft[1].set_facecolor(bg_color)

# Zoomed in pitch for Shots and Goals
shots_pitch = VerticalPitch(
    goal_type='box',
    line_color='#03191E',
    linewidth=1.6,
    pad_right=-10,
    pad_left=-10,
    pad_bottom=-75
)
# Draw pitch
shots_pitch.draw(ax=axsRight[0])
# Add small border
axsRight[0].patch.set_edgecolor('black')
axsRight[0].patch.set_linewidth(0.3)
# Add bg color
axsRight[0].set_facecolor(bg_color)

passes_box_pitch = VerticalPitch(
    goal_type='box',
    line_color='#03191E',
    linewidth=1.6,
    # pad_right=-5,
    # pad_left=-5,
    pad_bottom=-55
)

# Draw Pitch
passes_box_pitch.draw(ax=axsRight[1])
# Add small border
# axsRight[1].patch.set_edgecolor('black')
# axsRight[1].patch.set_linewidth(0.3)
# Add bg color
axsRight[1].set_facecolor(bg_color)

# fig, axs = pitch.grid(
#             nrows=1, ncols=2,
#             figheight=10,
#
#             #title_height=title_h,  # the title takes up 15% of the fig height
#             #grid_height=grid_h,  # the grid takes up 71.5% of the figure height
#            # endnote_height=endnote_h,  # endnote takes up 6.5% of the figure height
#             #
#             #grid_width=grid_w,  # gris takes up 95% of the figure width
#             #
#             # # 1% of fig height is space between pitch and title
#             #title_space=title_space,
#             #
#             # # 1% of fig height is space between pitch and endnote
#            # endnote_space=endnote_space,
#             #
#             #space=space,  # 5% of grid_height is reserved for space between axes
#             #
#             # # centers the grid horizontally / vertically
#             # left=0.1,
#             bottom=None,
#             axis=False,
# )

# -------------------------------------------- Fig 1. Passes into Final Third
axsLeft[0].set_title('Pases al Último Tercio', fontsize=fig_fontsize)

tdf = df[(df['Event'] == 'Failed Pass')]
tdf = tdf[(tdf['X'] < (2/3*100)) & (tdf['X2'] >= (2/3*100))]
final_failed = len(tdf)

# Successful Passes
pdf = df[df['Event'] == 'Pass']
pdf = pdf[(pdf['X'] < (2/3*100)) & (pdf['X2'] >= (2/3*100))]
final_completed = len(pdf)

# Add Data
xval = 40
yval = -13
axsLeft[0].text(x=xval, y=yval,
                s=f'{final_completed} Pases Completados',
                c=event1_marker_color1,
                ha='center',
                weight='bold',
                )

axsLeft[0].text(x=xval, y=yval-6,
                s=f'{final_failed} Pases Fallados',
                c=event2_marker_color1,
                ha='center',
                weight='bold',
                )

xstart, ystart = standard.transform(pdf['X'], pdf['Y'])
xend, yend = standard.transform(pdf['X2'], pdf['Y2'])

pitch.lines(
    xstart=xstart,
    ystart=ystart,
    xend=xend,
    yend=yend,
    ax=axsLeft[0],
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
    ax=axsLeft[0],
    s=event_marker_width,
    marker='o',
    facecolor=event1_marker_color1,
    # facecolor='#ef4146',
    zorder=2,
)

# Unsuccessful Passes
pdf = df[df['Event'] == 'Failed Pass']
pdf = pdf[(pdf['X'] < (2/3*100)) & (pdf['X2'] >= (2/3*100))]

xstart, ystart = standard.transform(pdf['X'], pdf['Y'])
xend, yend = standard.transform(pdf['X2'], pdf['Y2'])

pitch.lines(
    xstart=xstart,
    ystart=ystart,
    xend=xend,
    yend=yend,
    ax=axsLeft[0],
    lw=3,
    color=event2_marker_color1,
    comet=True,
    transparent=True,
    alpha_start=line_alpha_start,
    alpha_end=line_alpha_end,
)

pitch.scatter(
    x=xend,
    y=yend,
    ax=axsLeft[0],
    s=event_marker_width,
    marker='o',
    facecolor=event2_marker_color1,
    # facecolor='#ef4146',
    zorder=2,
)


# Add Final 3rd Line

y, _ = standard.transform([2 / 3 * 100], [0])
axsLeft[0].hlines(
    y=y,
    xmin=-3,
    xmax=83,
    colors='black',
    linestyles='dashed',
    alpha=0.3,
    clip_on=False,
    zorder=-1,
)

# ------------------------------------------------ Fig 2. Passes from Defenders
axsLeft[1].set_title('Pases de Defensas Centrales', fontsize=fig_fontsize)
defenders = ['3 Loor', '2 Castro', '54 Hurt']

# Get team total passes
team_total = len(df[(df['Event'] == 'Pass') | (df['Event'] == 'Failed Pass')])
team_completed = len(df[(df['Event'] == 'Pass')])

# Get defs total passes
tdf = df[(df['Event'] == 'Pass') | (df['Event'] == 'Failed Pass')]
tdf = tdf[tdf['Player'].isin(defenders)]
def_total = len(tdf)

# Successful Passes
pdf = df[(df['Event'] == 'Pass')]
pdf = pdf[pdf['Player'].isin(defenders)]
def_completed = len(pdf)


# Data for Figure
val = np.round(def_total/team_total * 100, 1)

fig_datos = f'Pases del Equipo\n{val}%'

xval = 40
# yval = 80
yval = -13
axsLeft[1].text(x=xval, y=yval,
                s=f'{def_completed} Pases Completados',
                c=event1_marker_color1,
                ha='center',
                weight='bold',
                )

axsLeft[1].text(x=xval, y=yval-6,
                s=f'{def_total-def_completed} Pases Fallados',
                c=event2_marker_color1,
                ha='center',
                weight='bold',
                )

xstart, ystart = standard.transform(pdf['X'], pdf['Y'])
xend, yend = standard.transform(pdf['X2'], pdf['Y2'])

pitch.lines(
    xstart=xstart, ystart=ystart, xend=xend, yend=yend,
    ax=axsLeft[1],
    lw=3,
    color=event1_marker_color1,
    comet=True,
    transparent=True,
    alpha_start=line_alpha_start,
    alpha_end=line_alpha_end,
)

pitch.scatter(x=xend, y=yend,
    ax=axsLeft[1],
    s=event_marker_width,
    marker='o',
    facecolor=event1_marker_color1,
    # facecolor='#ef4146',
    zorder=2,
)

# Failed Passes
pdf = df[df['Event'] == 'Failed Pass']
pdf = pdf[pdf['Player'].isin(defenders)]

xstart, ystart = standard.transform(pdf['X'], pdf['Y'])
xend, yend = standard.transform(pdf['X2'], pdf['Y2'])

pitch.lines(
    xstart=xstart, ystart=ystart, xend=xend, yend=yend,
    ax=axsLeft[1],
    lw=3,
    color=event2_marker_color1,
    comet=True,
    transparent=True,
    alpha_start=line_alpha_start,
    alpha_end=line_alpha_end,
)

pitch.scatter(x=xend, y=yend,
    ax=axsLeft[1],
    s=event_marker_width,
    marker='o',
    facecolor=event2_marker_color1,
    # facecolor='#ef4146',
    zorder=2,
)

# --------------------------------------------------------------- Fig 3. Shots
axsRight[0].set_title('Tiros y Goles', fontsize=fig_fontsize)

# Shots
pdf = df[(df['Event'] == 'Shot')]
tiros = len(pdf)
xstart, ystart = standard.transform(pdf['X'], pdf['Y'])

pitch.scatter(x=xstart, y=ystart,
              ax=axsRight[0],
              s=event_marker_width2,
              marker='o',
              edgecolor=event1_marker_color1,
              facecolor=bg_color,
              # facecolor=event2_marker_color1,
              # facecolor='#ef4146',
              # zorder=2,
)

# Goals
pdf = df[(df['Event'] == 'Goal')]
goles = len(pdf)
tiros += goles

xstart, ystart = standard.transform(pdf['X'], pdf['Y'])
xend, yend = standard.transform(pdf['X2'], pdf['Y2'])

pitch.lines(
    xstart=xstart, ystart=ystart, xend=xend, yend=yend,
    ax=axsRight[0],
    lw=2,
    color=event1_marker_color1,
    comet=True,
    transparent=True,
    alpha_start=line_alpha_start,
    alpha_end=line_alpha_end,
)

pitch.scatter(x=xstart, y=ystart,
              ax=axsRight[0],
              s=event_marker_width2,
              marker='o',
              facecolor=event1_marker_color1,
              # facecolor='#ef4146',
              # zorder=2,
)

axsRight[0].text(
    x=15, y=85,
    s=f'{tiros} Tiros',
    ha='left',
    va='top',
    color=event1_marker_color1,
    alpha=1,
)
axsRight[0].text(
    x=15, y=80,
    s=f'{goles} Goles',
    ha='left',
    va='top',
    color=event1_marker_color1,
    weight='bold',
)


# --------------------------------------------- Fig 4. Passes into Penalty Box
axsRight[1].set_title('Pases al Area Rival', fontsize=fig_fontsize)

sb_to_op = Standardizer(pitch_from='statsbomb', pitch_to='opta')
endx, endy = sb_to_op.transform([102, 102], [18, 62])

# Successful Passes
pdf = df[df['Event'] == 'Pass']
pdf = pdf[
    (
            (pdf['X2'] >= endx[0])
            & (pdf['Y2'] >= endy[1])
            & (pdf['Y2'] <= endy[0])
    )
]

xstart, ystart = standard.transform(pdf['X'], pdf['Y'])
xend, yend = standard.transform(pdf['X2'], pdf['Y2'])

pitch.lines(
    xstart=xstart, ystart=ystart, xend=xend, yend=yend,
    ax=axsRight[1],
    lw=3,
    color=event1_marker_color1,
    comet=True,
    transparent=True,
    alpha_start=line_alpha_start,
    alpha_end=line_alpha_end,
)

pitch.scatter(x=xend, y=yend,
    ax=axsRight[1],
    s=event_marker_width,
    marker='o',
    facecolor=event1_marker_color1,
    # facecolor='#ef4146',
    zorder=2,
)

failed = False
if failed:
    # Unsuccessful Passes
    pdf = df[df['Event'] == 'Failed Pass']
    pdf = pdf[
        (
                (pdf['X2'] >= endx[0])
                & (pdf['Y2'] >= endy[1])
                & (pdf['Y2'] <= endy[0])
        )
    ]

    xstart, ystart = standard.transform(pdf['X'], pdf['Y'])
    xend, yend = standard.transform(pdf['X2'], pdf['Y2'])

    pitch.lines(
        xstart=xstart, ystart=ystart, xend=xend, yend=yend,
        ax=axsRight[1],
        lw=3,
        color=event2_marker_color1,
        comet=True,
        transparent=True,
        alpha_start=line_alpha_start,
        alpha_end=line_alpha_end,
    )

    pitch.scatter(x=xend, y=yend,
        ax=axsRight[1],
        s=event_marker_width,
        marker='o',
        facecolor=event2_marker_color1,
        # facecolor='#ef4146',
        zorder=2,
    )

# --------------------------------------------------------------- Add Title

# Add team logo
image = Image.open('data/20240119_logo.png')
newax = fig.add_axes([0.06, 1.06, 0.18, 0.18], anchor='W', zorder=1)
newax.imshow(image)
newax.axis('off')

title = ax_title.text(
    x=x_title,
    y=y_title,
    s=title_text,
    size=20,
    ha='left',
    va='top',
    # weight='bold',
)

# Add subtitle 1
subtitle = ax_title.text(
    x=x_title,
    y=y_title - spacing,
    s='Juego de Posesion y Directo | Victoria 4-1 vs. Japan Auto',
    size=13,
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


# fig.text(
#     x=-0.025,
#     y=0.5,
#     s='.',
#     alpha=0,
# )
#
# fig.text(
#     x=1.025,
#     y=0.5,
#     s='.',
#     alpha=0,
# )

# --------------------------------------------------------------- Add Credits
# Twitter Account
tw_account = ax_annotate.text(
    1,
    0,
    '@DGCFutbol',
    va='bottom',
    ha='right',
    fontsize=13,
    weight='bold',
    # ontproperties=robotto_regular.prop,
    # color='#941C2F',
    color=event1_marker_color1,
    # color='#0b4393',
    alpha=1,
)

# Source label
source = ax_annotate.text(
    1,
    .45,
    'Datos y Gráficos: Daniel Granja C.',
    va='bottom',
    ha='right',
    fontsize=12,
    # weight='bold',
    # ontproperties=robotto_regular.prop,
    color='#030303',
    alpha=0.7,
)

plt.savefig('20240119_viz.png',
            bbox_inches='tight',
            dpi=250
            )
