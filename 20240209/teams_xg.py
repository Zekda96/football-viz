# Data Management
import pandas as pd
import numpy as np

# Viz
import matplotlib.pyplot as plt
from mplsoccer import Pitch, VerticalPitch, Standardizer
from PIL import Image


bg_color = '#faf9f4'

# Standardizer
standard = Standardizer(pitch_from='opta', pitch_to='statsbomb')

data = pd.read_csv('data/LigaPro2023_xg.csv').iloc[:, 1:]


test = data[['team', 'home', 'away', 'xG']].groupby(['team', 'home', 'away']).sum()

# Get teams list
teams = data.team.unique().tolist()

# ------------------------- Get 'xG for' of all teams
# Create dict for total xG of each team
xg_total = dict(zip(teams, [0] * len(teams)))

# Go through xG of all matches
for match in test.index.to_list():
    # Get team name
    team = match[0]
    # Add xG of match to team's total xG for
    xg_total[team] += test.loc[match, :].values[0]

# ------------------------- Get 'xG against' of all teams
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

# ------------- Figure
# Create single dataframe for xg and xga
xg = pd.DataFrame.from_dict(xg_total, columns=['xg'], orient='index')
xg = xg.assign(xga=pd.Series(xga_total))

# Since not all matches are available, get /per match vals
xgp90 = dict(zip(teams, [0] * len(teams)))
for t in teams:
    matches_no = len(test.loc[t, :])

    xgp90[t] = xg.loc[t, :]/matches_no

xgp90 = pd.DataFrame(xgp90).T

# Plot xg vs xga

x = list(xgp90['xg'].values)
y = list(xgp90['xga'].values)

fig, ax = plt.subplots(nrows=1, ncols=1)
fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

plt.scatter(
    x=x,
    y=y,
)

plt.gca().invert_yaxis()

# Add Team Labels
for i, txt in enumerate(xgp90.index.to_list()):
    plt.annotate(txt, (x[i], y[i]))

# # TODO: Add team logos

logos = {'Aucas': 'au',
}

DC_to_FC = ax.transData.transform
FC_to_NFC = fig.transFigure.inverted().transform
# -- Take data coordinates and transform them to normalized figure coordinates
DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))

ax_size = 0.05

for i, x, y in enumerate(zip(x, y)):
    ax_coords = DC_to_NFC((x, y))
    newax = fig.add_axes(
        [ax_coords[0] - ax_size/2, ax_coords[1] - ax_size/2, ax_size, ax_size],
        fc='None'
    )
    image = Image.open(logos[i])
    newax.imshow(image)
    newax.axis('off')


plt.axhline(y=np.median(y), linestyle='dotted', alpha=0.6, c='black')
plt.axvline(x=np.median(x), linestyle='dotted', alpha=0.6, c='black')

plt.title(r'Goles Esperados a favor y en contra', fontsize=10)
plt.suptitle('Liga Pro 2023', fontsize=17)
plt.xlabel('xG - Goles Esperados A Favor')
plt.ylabel('xG Against - Goles Esperados En Contra')

plt.grid(
    False,
    # linestyle='-'
)

plt.tick_params(
    # labelcolor='r',
    labelsize='small',
    width=1
)

plt.savefig('data/ligapro_xg.png',
            bbox_inches='tight',
            dpi=250
            )
