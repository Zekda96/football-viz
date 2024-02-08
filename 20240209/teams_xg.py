# Data Management
import pandas as pd
import numpy as np

# Viz
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch, Standardizer
from PIL import Image


bg_color = '#faf9f4'
y_color = 'red'
x_color = 'green'

# Standardizer
standard = Standardizer(pitch_from='opta', pitch_to='statsbomb')

data = pd.read_csv('data/LigaPro2023_xg.csv').iloc[:, 1:]

test = data[['team', 'home', 'away', 'xG']].\
    groupby(['team', 'home', 'away']).sum()

# Get teams list
teams = data.team.unique().tolist()

# --------------------------------------------------- Get 'xG for' of all teams
# Create dict for total xG of each team
xg_total = dict(zip(teams, [0] * len(teams)))

# Go through xG of all matches
for match in test.index.to_list():
    # Get team name
    team = match[0]
    # Add xG of match to team's total xG for
    xg_total[team] += test.loc[match, :].values[0]

# ----------------------------------------------- Get 'xG against' of all teams
# Create dict for total 'xG against (xga)' of each team
xga_total = dict(zip(teams, [0] * len(teams)))

for i, match in enumerate(test.index.to_list()):
    # index with team, home and away
    against = list(test.index.to_list()[i])
    # Delete team generating the xG to get only the team receiving it
    idxs = [i for i, team in enumerate(match) if team == match[0]]
    idxs.reverse()
    for idx in idxs:
        del against[idx]

    xga_total[against[0]] += test.loc[match, :].values[0]

# ------------------------------------------------------------------------ Data
# Create single dataframe for xg and xga
xg = pd.DataFrame.from_dict(xg_total, columns=['xg'], orient='index')
xg = xg.assign(xga=pd.Series(xga_total))

# Since not all matches are available, get /per match vals
xgp90 = dict(zip(teams, [0] * len(teams)))
for t in teams:
    matches_no = len(test.loc[t, :])

    xgp90[t] = xg.loc[t, :]/matches_no

xgp90 = pd.DataFrame(xgp90).T

# ---------------------------- Plot xg vs xga

x = list(xgp90['xg'].values)
y = list(xgp90['xga'].values)

fig, ax = plt.subplots(nrows=1, ncols=1)
fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

ax.axhline(y=np.median(y), linestyle='dotted', alpha=0.6, c='black')
ax.axvline(x=np.median(x), linestyle='dotted', alpha=0.6, c='black')

ax.set_title(f'Goles Esperados a favor y en contra', fontsize=10)
fig.suptitle('Liga Pro 2023', fontsize=17)
ax.set_xlabel('xGp90 - Goles Esperados A Favor (p90)', c=x_color)
ax.set_ylabel('xGp90 Against - Goles Esperados En Contra (p90)', c=y_color)

plt.grid(
    False,
    # linestyle='-'
)

plt.tick_params(
    # labelcolor='r',
    labelsize='small',
    width=1,
    bottom=False,
    left=False,
)

ax.tick_params(axis='y',
               labelcolor=y_color,
               pad=3.5,
               )

ax.tick_params(axis='x',
               labelcolor=x_color,
               pad=2.5,
               )

# Color left edge
plt.setp(list(ax.spines.values())[0], color=y_color)
# Color bottom edge
plt.setp(list(ax.spines.values())[2], color=x_color)

plt.setp(list(ax.spines.values())[1], color=bg_color)
plt.setp(list(ax.spines.values())[3], color=bg_color)

plt.scatter(
    x=x,
    y=y,
)

plt.gca().invert_yaxis()

# Add Team Labels
# for i, txt in enumerate(xgp90.index.to_list()):
xoff = [
    # 0.027,
    -0.18
]
yoff = [
    # 0.012,
    -0.009
]
# offset_teams = ['Deportivo Cuenca']
# for i, txt in enumerate(offset_teams):
#     id = xgp90.index.to_list().index(txt)
#     if txt == 'Deportivo Cuenca':
#         txt = 'D. Cuenca'
#     plt.annotate(txt, (x[id]+xoff[i], y[id] + yoff[i]))

# ---------------------------------------------------------------- Team logos

logos = {'Aucas': 'au',
         'Deportivo Cuenca': 'dc',
         'LDU': 'ldu',
         'Independiente del Valle': 'idv',
         'Mushuc Runa': 'mr',
         'Cumbayá FC': 'cu',
         'Guayaquil City': 'gc',
         'Barcelona SC': 'bsc',
         'Gualaceo SC': 'gu',
         'Universidad Católica del Ecuador': 'uc',
         'Técnico Universitario': 'tu',
         'El Nacional': 'na',
         'Emelec': 'cse',
         'Libertad': 'lb',
         'Orense SC': 'or',
         'Delfín': 'de'
}

DC_to_FC = ax.transData.transform
FC_to_NFC = fig.transFigure.inverted().transform
# -- Take data coordinates and transform them to normalized figure coordinates
DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))


for i, (x, y) in enumerate(zip(x, y)):
    ax_size = 0.067
    team_name = xgp90.index.to_list()[i]
    # if team_name == "Emelec":
    #     x += 0.045
    # if team_name == "Deportivo Cuenca":
    #     x -= 0.045
    ax_coords = DC_to_NFC((x, y))
    newax = fig.add_axes(
        [ax_coords[0] - ax_size/2, ax_coords[1] - ax_size/2, ax_size, ax_size],
        fc='None'
    )
    image = Image.open(f"data/{logos[team_name]}.png")
    newax.imshow(image)
    newax.axis('off')


# LIGA PRO LOGO
ax_coords = [0.28, 0.95]
ax_size = 0.1
image = Image.open('data/lp.png')
newax = fig.add_axes(
    [ax_coords[0]-ax_size/2, ax_coords[1]-ax_size/2, ax_size, ax_size],
    anchor='W', zorder=1
)
newax.imshow(image)
newax.axis('off')

# Save
plt.savefig('ligapro_xg.png',
            bbox_inches='tight',
            dpi=250
            )
