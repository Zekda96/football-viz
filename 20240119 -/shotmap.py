import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch, Standardizer
from matplotlib import patheffects
from matplotlib.patches import FancyArrow
from matplotlib.colors import LinearSegmentedColormap
from colorsys import rgb_to_hsv, hsv_to_rgb
from PIL import Image, ImageColor


def short_hex(hex_tpl: tuple):
    out = []
    for i in hex_tpl:
        if len(i) == 3:
            out.append(f'0{i[-1]}')
        elif len(i) == 4:
            out.append(f'{i[-2:]}')
    return tuple(out)


def rgb2hex(rgbv: tuple):
    rgbh = (hex(round(rgbv[0])), hex(round(rgbv[1])), hex(round(rgbv[2])))
    rgbh = short_hex(rgbh)
    hex_vals = f'#{rgbh[0]}{rgbh[1]}{rgbh[2]}'
    return hex_vals


def custom_cmap(clr: str, sat_diff1=0.2, sat_diff2=0.25, bright_diff=0.6):
    c3 = clr
    c3_rgb = ImageColor.getcolor(c3, "RGB")
    c3_hsv = rgb_to_hsv(c3_rgb[0], c3_rgb[1], c3_rgb[2])

    c1 = hsv_to_rgb(c3_hsv[0], c3_hsv[1] * sat_diff1, 255)
    c1 = rgb2hex(c1)
    c2 = hsv_to_rgb(c3_hsv[0], c3_hsv[1] * sat_diff2, 255)
    c2 = rgb2hex(c2)
    c4 = hsv_to_rgb(c3_hsv[0], c3_hsv[1], c3_hsv[2] * bright_diff)
    c4 = rgb2hex(c4)

    color_list = [c1, c2, c3, c4]

    return color_list


# ----------------------------------------------------- MANUAL PARAMETERS
half_time = 60
invert_first_half = False

# ----------------------------------- Text
bg_color = '#faf9f4'
# Title
x_title = 0.135
y_title = 0.81
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
df.loc[:, ['X2', 'Y2']] = df[['X2', 'Y2']].apply(pd.to_numeric,
                                                 errors='coerce')
df[['X2', 'Y2']] = df[['X2', 'Y2']].astype(float)
# Get 1st and 2nd Half values to invert coordinates
df1 = df[df['Mins'] < half_time]
df2 = df[df['Mins'] > half_time]
# Invert coordinates
if invert_first_half:
    df1[['X', 'Y', 'X2', 'Y2']] = 100 - df1[['X', 'Y', 'X2', 'Y2']]
else:
    df2.loc[:, ['X', 'Y', 'X2', 'Y2']] = 100 - df2.loc[:,
                                               ['X', 'Y', 'X2', 'Y2']]

df = pd.concat([df1, df2])

# Standardizer
standard = Standardizer(pitch_from='opta', pitch_to='statsbomb')

# ------------------------------------------------------------- CREATE FIGURE
fig = plt.figure(layout='constrained', figsize=(9.5, 4))
fig.patch.set_facecolor('#faf9f4')

ax_title = fig.add_axes([0, 1.05, 1, 0.2], anchor='SW', zorder=1)
ax_title.axis('off')
ax_annotate = fig.add_axes([0, -0.16, 1, 0.125], anchor='NW', zorder=1)
ax_annotate.axis('off')

subfigs = fig.subfigures(1, 3, wspace=0.07, width_ratios=[2, 1, 1])

axsLeft = subfigs[0].subplots(1, 2)
axsMiddle = subfigs[1].subplots(2, 1)
axsRight = subfigs[2].subplots(2, 1)

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

# Horizontal Pitch for Pass Zones Figure
hor_pitch = Pitch(
    # axis=True,
    # label=True,
    # tick=True,
    goal_type='box',
    line_color='#03191E',
    # line_alpha=0.5,
    linewidth=1.6,
)

# Draw pitch
hor_pitch.draw(ax=axsMiddle[0])
hor_pitch.draw(ax=axsMiddle[1])
axsMiddle[0].set_facecolor(bg_color)
axsMiddle[1].set_facecolor(bg_color)

# Pitch for final third passes
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
# Add bg color
axsRight[1].set_facecolor(bg_color)

# -------------------------------------------- Fig 1. Passes into Final Third
axsLeft[0].set_title('Pases al Último Tercio', fontsize=fig_fontsize)

tdf = df[(df['Event'] == 'Failed Pass')]
tdf = tdf[(tdf['X'] < (2 / 3 * 100)) & (tdf['X2'] >= (2 / 3 * 100))]
final_failed = len(tdf)

# Successful Passes
pdf = df[df['Event'] == 'Pass']
pdf = pdf[(pdf['X'] < (2 / 3 * 100)) & (pdf['X2'] >= (2 / 3 * 100))]
final_completed = len(pdf)

# Add Data
xval = 40
yval = -13
axsLeft[0].text(x=xval, y=yval,
                s=f'{final_completed} Completados',
                c=event1_marker_color1,
                ha='center',
                weight='bold',
                )

axsLeft[0].text(x=xval, y=yval - 6,
                s=f'{final_failed} Fallados',
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
pdf = pdf[(pdf['X'] < (2 / 3 * 100)) & (pdf['X2'] >= (2 / 3 * 100))]

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
axsLeft[1].set_title('Pases de\nDefensas Centrales', fontsize=fig_fontsize)
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
val = np.round(def_total / team_total * 100, 1)

fig_datos = f'Pases del Equipo\n{val}%'

xval = 40
# yval = 80
yval = -13
axsLeft[1].text(x=xval, y=yval,
                s=f'{def_completed} Completados',
                c=event1_marker_color1,
                ha='center',
                weight='bold',
                )

axsLeft[1].text(x=xval, y=yval - 6,
                s=f'{def_total - def_completed} Fallados',
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

# ----------------------------------------------------- Fig 3. Passes by Zones
# Passes
pdf = df[df['Event'] == 'Pass']

# Bins for heatmap
bin_x = np.linspace(hor_pitch.dim.left, hor_pitch.dim.right, num=7)
bin_y = np.sort(np.array([hor_pitch.dim.bottom, hor_pitch.dim.six_yard_bottom,
                          hor_pitch.dim.six_yard_top, hor_pitch.dim.top]))

# Transform values
xstart, ystart = standard.transform(pdf['X'], pdf['Y'])

# Count passes per zone
bin_statistic = hor_pitch.bin_statistic(xstart, ystart,
                                        statistic='count',
                                        bins=(bin_x, bin_y),
                                        normalize=True)

# Create custom colormap from viz base color
clist = custom_cmap(event1_marker_color1)
# Original hand-picked colors
# clist = ['#FFF1DB', '#FFE9CE', '#de9314', '#99610F']

# Custom color map
ccmap = LinearSegmentedColormap.from_list("custom", clist)

# Plot heatmap
hor_pitch.heatmap(bin_statistic,
                  ax=axsMiddle[0],
                  cmap=ccmap,
                  edgecolor='#03191E',
                  )
# Path effects
path_eff = [patheffects.Stroke(linewidth=1.5, foreground='black'),
            patheffects.Normal()]
# Add % labels
labels = hor_pitch.label_heatmap(bin_statistic,
                                 color='#f4edf0',
                                 fontsize=9,
                                 ax=axsMiddle[0],
                                 ha='center',
                                 va='center',
                                 str_format='{:.0%}',
                                 path_effects=path_eff,
                                 )

# -------------------------------------------- Fig 4. Passes by Vertical Zones
axsMiddle[0].set_title('Pases por Zonas', fontsize=fig_fontsize)

# Passes
pdf = df[df['Event'] == 'Pass']

# Bins for heatmap
bin_x = np.linspace(hor_pitch.dim.left, hor_pitch.dim.right, num=6)
bin_y = np.sort(np.array([hor_pitch.dim.bottom, hor_pitch.dim.top]))

# Transform Values
xstart, ystart = standard.transform(pdf['X'], pdf['Y'])

# Count passes per zone
bin_statistic = hor_pitch.bin_statistic(xstart, ystart,
                                        statistic='count',
                                        bins=(bin_x, bin_y),
                                        normalize=True)

# Plot heatmap
hor_pitch.heatmap(bin_statistic,
                  ax=axsMiddle[1],
                  cmap=ccmap,
                  edgecolor='#03191E',
                  # edgecolor='black'
                  )

# Add % labels
labels2 = hor_pitch.label_heatmap(bin_statistic,
                                  color='#f4edf0',
                                  fontsize=9,
                                  ax=axsMiddle[1],
                                  ha='center',
                                  va='center',
                                  str_format='{:.0%}',
                                  path_effects=path_eff,
                                  )

# Add arrow and text 'Dirección de Ataque'
l1 = FancyArrow(x=0.51, y=0.49, dx=0.215, dy=0,
                            transform=fig.transFigure, figure=fig,
                            length_includes_head=True,
                            head_length=0.01,
                            head_width=0.0225)

axsMiddle[0].text(x=60, y=96,
                  s='Dirección de Ataque',
                  ha='center'
)

fig.lines.extend([l1])
# --------------------------------------------------------------- Fig 5. Shots
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

# --------------------------------------------- Fig 6. Passes into Penalty Box
axsRight[1].set_title('Pases en Último Tercio', fontsize=fig_fontsize)

y, _ = standard.transform([2 / 3 * 100], [0])
axsRight[1].hlines(
    y=y,
    xmin=-3,
    xmax=83,
    colors='black',
    linestyles='dashed',
    alpha=0.3,
    clip_on=False,
    zorder=-1,
)

sb_to_op = Standardizer(pitch_from='statsbomb', pitch_to='opta')
endx, endy = sb_to_op.transform([102, 102], [18, 62])

# Passes on Final 3rd
pdf = df[df['Event'] == 'Pass']
pdf = pdf[(pdf['X'] > (2 / 3 * 100)) & (pdf['X2'] > (2 / 3 * 100))]
completed = len(pdf)

# Get data
# val1 = np.round(completed/team_completed * 100, 1)
# axsRight[1].text(x=8, y=65, s=f'{val1}% de los Pases Totales')

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
newax = fig.add_axes([0.021, 1.04, 0.19, 0.19], anchor='W', zorder=1)
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
    s='Juego de Posesión y Directo | Victoria 4-1 vs. Japan Auto',
    size=13,
    ha='left',
    va='top',
    # fontproperties=font_bold.prop,
    color="#030303",
    alpha=0.6,
)

# --------------------------------------------------------------- Add Credits
# Twitter Account
tw_account = ax_annotate.text(
    x=1,
    y=-0.1,
    s='@DGCFutbol',
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

# Add Social Media logo
y = -0.175
x = 0.84
image = Image.open('data/tw.png')
newax = fig.add_axes([x, y, 0.045, 0.045], anchor='SW', zorder=0)
newax.imshow(image)
newax.axis('off')

image = Image.open('data/ig.png')
newax = fig.add_axes([x - 0.03, y - 0.012, 0.07, 0.07], anchor='SW', zorder=0)
newax.imshow(image)
newax.axis('off')

plt.savefig('20240119_viz.png',
            bbox_inches='tight',
            dpi=250
            )
