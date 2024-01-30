import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch, Standardizer
from customcmap import custom_cmap
from matplotlib import patheffects
from matplotlib.patches import FancyArrow
from PIL import Image
from scipy.ndimage import gaussian_filter

# ----------------------------------------------------- MANUAL PARAMETERS

# Replace player names
old_player_list = [
    '1',

    '54 Hurt',
    '2 Castro',
    '3 Loor',

    '52 Mndz',
    '19 Porozo',
    '15 Cmch',
    '59 Vldz',

    '10 Cbzs',

    '7 Qntrs',
    '11 Mlna'
]

player_list = [
    '1 Albarracin',
    '54 Hurtado',
    '2 Castro',
    '3 Loor',
    '52 Mendoza',
    '19 Porozo',
    '15 Camacho',
    '59 Valdez',
    '10 Cabezas',
    '7 Quinteros',
    '11 Molina'
]

# ------------------------------------------------------------------ READ DATA
data = pd.read_csv('data/20240119_events.csv')

# Sort values by time
df = data.sort_values(['Mins', 'Secs'], ascending=[True, True])
# Fix Missing Values
df.loc[:, ['X2', 'Y2']] = df[['X2', 'Y2']].apply(pd.to_numeric,
                                                 errors='coerce')
df[['X2', 'Y2']] = df[['X2', 'Y2']].astype(float)
# Get 1st and 2nd Half values to invert coordinates
half_time = 60
df1 = df[df['Mins'] < half_time]
df2 = df[df['Mins'] > half_time]
# Invert coordinates
invert_first_half = False
if invert_first_half:
    df1[['X', 'Y', 'X2', 'Y2']] = 100 - df1[['X', 'Y', 'X2', 'Y2']]
else:
    df2.loc[:, ['X', 'Y', 'X2', 'Y2']] = 100 - df2.loc[:,
                                               ['X', 'Y', 'X2', 'Y2']]

df = pd.concat([df1, df2])

# Sort in arbitrary order so passes/assists appear just before pass received
# This way we create the connections between passers/receivers
order = ["Failed Pass", "Pass", "Assist", "Pass Received", "Shot", "Goal"]
df['Event'] = pd.Categorical(df['Event'], order)
df = df.sort_values(by=['Mins', 'Secs', 'Event']).reset_index()

# Replace Player Names
df = df.replace(to_replace=old_player_list, value=player_list)

# Standardizer
standard = Standardizer(pitch_from='opta', pitch_to='statsbomb')

# ---------------------------------------------- 1. COUNT PASS COMBINATIONS

# Create dict for pass combinations
passes = {}
for p in df.Player.unique():
    receivers = {}
    for p2 in df.Player.unique():
        if p != p2:
            receivers[p2] = 0
    passes[p] = receivers

# List of all indexes of pass receivers
receivers_id = df[df['Event'] == 'Pass Received'].index.tolist()
# Start counting pass/pass receivers combinations
for idx in receivers_id:
    first = df.loc[idx - 1]
    second = df.loc[idx]

    # Sanity check just so events are in order
    if (first['Event'] in (['Pass', 'Assist'])) & \
            (second['Event'] == 'Pass Received'):

        passer = first['Player']
        receiver = second['Player']
        # Add
        passes[passer][receiver] += 1
        passes[receiver][passer] += 1
    else:
        print('LIST IS NOT IN ORDER. DEBUG')

# Get the highest pass count for a single combination of players
max_val = 0
for i in passes.values():
    if max(i.values()) > max_val:
        max_val = max(i.values())

# Get the total number of passes per players (Marker size)
for pl in df['Player'].unique().tolist():
    passes[pl]['Total'] = sum(passes[pl].values())

# Get the total number of passes (Marker Size)
total_passes = df[df['Event'] == 'Pass'].Event.count()

# ----------------------------------------- 2. Calculate Average Pass Position
passes_loc = {}
for pl in df['Player'].unique():
    pdf = df[(df['Player'] == pl) & (df['Event'] == 'Pass')]
    x = pdf.loc[:, 'X'].mean()
    y = pdf.loc[:, 'Y'].mean()
    passes_loc[pl] = [x, y]

# --------------------------------------------------------------- CREATE FIGURE
bg_color = '#faf9f4'
base_color = '#de9314'

fig = plt.figure(layout='constrained', figsize=(9.5, 12), dpi=250)
fig.patch.set_facecolor(bg_color)

# Axis for title
h = 0.1
ax_title = fig.add_axes([0, 1, 1, h], zorder=1)
ax_title.axis('off')

# Axis for credits
h = 0.1
ax_annotate = fig.add_axes([0, -h, 1, h], zorder=1)
ax_annotate.axis('off')

subfigs = fig.subfigures(3, 1,
                         wspace=0.01,
                         hspace=0.01,
                         height_ratios=[1, 1.5, 0.5])

axsTop = subfigs[0].subplots(1, 1)
axsMiddle = subfigs[1].subplots(3, 3)
axsBot = subfigs[2].subplots(1, 2)

axsTop.text(
    x=60,
    y=-1,
    s='Red de Pases',
    size=18,
    ha='center',
    va='bottom',
)

pitch = Pitch(
    # goal_type='box',
    line_color='#03191E',
    # line_alpha=0.5,
    linewidth=2,
    # line_color='black',
    line_zorder=2
)

pitch.draw(ax=axsTop)
axsTop.set_facecolor(bg_color)

# Add Arrow
dx = 0.3
l1 = FancyArrow(x=0.75 - dx/2, y=0.08, dx=dx, dy=0,
                transform=axsTop.transAxes,
                figure=fig,
                length_includes_head=True,
                head_length=0.01,
                head_width=0.02,
                zorder=50,
                color='black',
                )

subfigs[0].lines.extend([l1])

axsTop.text(x=90, y=76,
            s='Dirección de Ataque',
            ha='center',
            size='10.5',
            )

# -------------------------------------------------------------- 1. Pass Lines
for pl1 in player_list:
    for pl2 in player_list:
        if pl2 != pl1:

            if passes[pl1][pl2] > 3:
                lw = passes[pl1][pl2]
            else:
                lw = 0.5

            xstart = [passes_loc[pl1][0]]
            ystart = [passes_loc[pl1][1]]

            xend = [passes_loc[pl2][0]]
            yend = [passes_loc[pl2][1]]

            xstart, ystart = standard.transform(xstart, ystart)
            xend, yend = standard.transform(xend, yend)
            pitch.lines(
                xstart=xstart,
                ystart=ystart,
                xend=xend,
                yend=yend,
                ax=axsTop,
                color='black',
                # color='#ef4146',
                edgecolors='white',
                # alpha=0.5,
                # zorder=2,
                lw=(lw * 1.3) / 2,
                alpha=((lw / max_val) * 1.1) / 2,
                # comet=True,
                # transparent=True,
                # alpha_start=0.1,
                # alpha_end=0.,
            )
# ------------------------------------------------ 2. Average Passing Location
# Path effects
path_eff = [patheffects.Stroke(linewidth=2, foreground='black'),
            patheffects.Normal()]

for i, pl in enumerate(player_list):
    x, y = standard.transform([passes_loc[pl][0]], [passes_loc[pl][1]])

    # With 10% of total team passes, marker size will be s1 which is average
    r = (passes[pl]['Total'] / total_passes)

    th1 = -0.4
    s1 = 400

    th2 = 0.7
    s2 = 9

    marker_s = (s1 * th1) + (10 * r * s1 * (1-th1))
    text_s = (s2 * th2) + (10 * r * s2 * (1-th2))

    # Player Icons
    pitch.scatter(
        x=x,
        y=y,
        ax=axsTop,
        s=marker_s,
        marker='o',
        facecolor=base_color,
        # facecolor='crimson',
        # facecolor='#ef4146',
        edgecolors='black',
        linewidths=1,
        # alpha=0.5,
        zorder=2,
    )

    # Player Numbers
    axsTop.text(
        x=x,
        y=y,
        s=pl.split()[0],
        size=text_s,
        c='white',
        ha='center',
        va='center',
        path_effects=path_eff,
    )

# --------------------------------------------------------- 3. PLAYERS HEATMAP
players_pitch = Pitch(
    # goal_type='box',
    line_color='#03191E',
    # line_alpha=0.5,
    linewidth=2,
    # line_color='black',
    line_zorder=2
)

ids1 = len(axsMiddle.flat)
ids2 = len(player_list) - ids1
c = 0
for axes in [axsMiddle, axsBot]:
    for ax in axes.flat:
        players_pitch.draw(ax=ax)
        ax.set_facecolor(bg_color)

        pl = player_list[c]
        # Passes
        pdf = df[(df['Event'] == 'Pass') & (df['Player'] == pl)]

        # Transform values
        xstart, ystart = standard.transform(pdf['X'], pdf['Y'])
        # Density Estimation heatmap
        players_pitch.kdeplot(
            xstart,
            ystart,
            ax=ax,
            # fill using 100 levels so it looks smooth
            fill=True, levels=1000,
            # shade the lowest area, so it looks smooth
            # so even if there are no events it gets some color
            thresh=0,
            cut=4,
            # extended the cut so it reaches the bottom edge
            # cmap='Reds',
            cmap='OrRd',
            # cmap='Oranges',
            # cmap=ccmap,
        )
        ax.set_title(f'{pl.split()[0]}. {pl.split()[1]}', size=15)
        c += 1

# ------------------------------------------------------------------- Add Title
# -- Transformation functions (thanks Son of a corner)
DC_to_FC = ax_title.transData.transform
FC_to_NFC = fig.transFigure.inverted().transform
# Transform for title axes
ax_title_tf = lambda x: FC_to_NFC(DC_to_FC(x))

# Add team logo
ax_coords = ax_title_tf((0.065, 0.5))
ax_size = 0.1
image = Image.open('data/20240119_logo.png')
newax = fig.add_axes(
    [ax_coords[0]-ax_size/2, ax_coords[1]-ax_size/2, ax_size, ax_size],
    anchor='W', zorder=1
)
newax.imshow(image)
newax.axis('off')

title = ax_title.text(
    x=0.5,
    y=0.8,
    s='DT Jonathan Mendoza - La Concordia SC',
    size=24,
    ha='center',
    va='top',
    # weight='bold',
)

subtitle = ax_title.text(
    x=0.5,
    y=0.4,
    s='Victoria 4-1 vs. Japan Auto  - Ascenso Nacional 2023',
    size=18,
    ha='center',
    va='top',
    color="#030303",
    alpha=0.6,
)
# ----------------------------------------------------------------- Add Credits
# Source label
source = ax_annotate.text(
    x=1,
    y=0.5,
    s='Datos y Gráficos: Daniel Granja C.',
    va='bottom',
    ha='right',
    fontsize=20,
    # weight='bold',
    # ontproperties=robotto_regular.prop,
    color='#030303',
    alpha=0.7,
)

# Twitter Account
tw_account = ax_annotate.text(
    x=1,
    y=0,
    s='@DGCFutbol',
    va='bottom',
    ha='right',
    fontsize=24,
    weight='bold',
    # ontproperties=robotto_regular.prop,
    # color='#941C2F',
    color=base_color,
    # color='#0b4393',
    alpha=1,
)

# -- Add Social Media logo
# Twitter Logo
ax_size1 = 0.05
x1 = 0.7
y1 = -0.102

image = Image.open('data/tw.png')
newax1 = fig.add_axes(
    (x1, y1, ax_size1, ax_size1),
    zorder=1, anchor='SW',
)
newax1.imshow(image)
newax1.axis('off')

# Instagram logo
ax_size2 = 0.065
x2 = x1 - ax_size2
y2 = y1 - 0.0048  # ax2 is larger, so we center the image
v = abs((ax_size2-ax_size1)/2)

image = Image.open('data/ig.png')
newax2 = fig.add_axes(
    (x2, y2-v, ax_size2, ax_size2),
    zorder=1, anchor='SW',
)
newax2.imshow(image)
newax2.axis('off')
# ------------------------------- Save fig

plt.savefig('20240124_viz.png',
            bbox_inches='tight',
            dpi=250
            )
