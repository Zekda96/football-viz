import pandas as pd
import json
import numpy as np

from mplsoccer import Pitch, VerticalPitch, Standardizer

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap



def get_qualifiers():
    """Read qualifiers to properly parse event data

    Returns:
        _type_: _description_
    """
    fp = 'data/qualifier_ids.csv'
    tdf = pd.read_csv(fp, header=None)

    qual = pd.Series(tdf.iloc[:,2].values, index=tdf.iloc[:,0]).to_dict()
    qual = {i: val.strip() for i, val in qual.items()}
    
    return qual


def get_event_ids():
    fp = 'data/event_ids.csv'
    tdf = pd.read_csv(fp, encoding='cp1252', header=None)

    vals = pd.Series(tdf.iloc[:,1].values, index=tdf.iloc[:,0]).to_dict()
    vals = {i: val.strip() for i, val in vals.items()}
    
    return vals
    
    
def get_team_mapping():
    fp = 'data/teams.csv'
    tdf = pd.read_csv(fp, header=None)
    teams = pd.Series(tdf.iloc[:,1].values, index=tdf.iloc[:,0]).to_dict()
    return teams


def read_data(fp, qual):
    """Read data and order it using qualiifers and save as df

    Args:
        fp (_type_): _description_
        qual (_type_): qualifiers from get_qualifiers()

    Returns:
        _type_: _description_
    """
    
    # fp = 'data/imbabura-delfin.json'
    with open(fp, "r") as f:
        data = json.load(f)
    

    df = []

    for event in data["liveData"]["event"]:
        row = {}
        for key, value in event.items():
            if key != "qualifier":
                row[key] = value
            elif key == "qualifier":
            # value is a list of json qualifiers
                for val in value:
                    # Create qualifier columns for which we have a mapping
                    if val["qualifierId"] in qual.keys():
                        # Some qualifiers dont have values, as they are boolean (Throw-ins)
                        if "value" in val.keys():
                            row[qual[val["qualifierId"]]] = val["value"]
                        else:
                            row[qual[val["qualifierId"]]] = True

        df.append(row)

    df = pd.DataFrame(df)
    
    # Use event ids and team mapping in dataframe
    df = df.replace({"typeId": get_event_ids(), "contestantId": get_team_mapping()})

    df["Pass End X"] = pd.to_numeric(df["Pass End X"])
    df["Pass End Y"] = pd.to_numeric(df["Pass End Y"])

    df = df.rename(
        {
            "typeId": "event",
            "contestantId": "team"
            },
        axis="columns"
        )
    
    return df


def filter_passes_to_box(df: pd.DataFrame, team: str):
    
    event = "Pass"
    pdf = df[["eventId", "event", "outcome", "playerName", "team", "periodId", "timeMin", "x", "y",
              "Pass End X", "Pass End Y",
              "Cross",
              "Corner taken"
              ]]
 
    pdf = pdf[pdf['event'] == event]
    pdf = pdf[pdf['team'] == team]
    pdf = pdf[pdf["Corner taken"] != True]

    # Passes into pen box
    sb_to_op = Standardizer(pitch_from='statsbomb', pitch_to='opta')
    endx, endy = sb_to_op.transform([102, 102], [18, 62])
    pdf = pdf[
        (
                (pdf["Pass End X"] >= endx[0])
                & (pdf["Pass End Y"] >= endy[1])
                & (pdf["Pass End Y"] <= endy[0])
        )
        ]
    
    return pdf
    

def add_box_passes(pitch, ax, df):
  
    standard = Standardizer(pitch_from='opta', pitch_to='statsbomb')

    ### FAILED PASSES
    color = '#c1c1bf'
    failed = df['outcome'] == 0

    x, y = standard.transform(df['x'][failed], df['y'][failed])
    xend, yend = standard.transform(df["Pass End X"][failed], df["Pass End Y"][failed])

    ev1 = pitch.lines(
        xstart=x,
        ystart=y,
        xend=xend,
        yend=yend,
        comet=True,
        transparent=True,
        color=color, # BenGriffis gray
        ax=ax,
        alpha_start=0.1,
        alpha_end=0.3,
                )

    ev2 = pitch.scatter(x=xend, y=yend, ax=ax,linewidth=0, color='#c1c1bf')

    ### SUCCESSFULL PASSES
    color = "green"
    success = df['outcome'] == 1

    x, y = standard.transform(df['x'][success], df['y'][success])
    xend, yend = standard.transform(df["Pass End X"][success], df["Pass End Y"][success])

    ev1 = pitch.lines(
        xstart=x,
        ystart=y,
        xend=xend,
        yend=yend,
        comet=True,
        transparent=True,
        color=color, # BenGriffis gray
        ax=ax,
        alpha_start=0.1,
        alpha_end=0.3,
                )

    ev2 = pitch.scatter(x=xend, y=yend, ax=ax,linewidth=0, color=color)


def add_box_heatmap(pitch, ax, df):

    standard = Standardizer(pitch_from='opta', pitch_to='statsbomb')

    # Bins for heatmap
    bin_x = np.sort(np.array([pitch.dim.left,
                                pitch.dim.penalty_area_left,
                                pitch.dim.penalty_area_left + 21,
                                pitch.dim.length/2,
                                pitch.dim.length/2 + 21,
                                pitch.dim.penalty_area_right,
                                pitch.dim.right
                                ]))

    bin_y = np.sort(np.array([pitch.dim.bottom,
                                pitch.dim.penalty_area_bottom,
                                pitch.dim.six_yard_bottom,
                                pitch.dim.six_yard_top,
                                pitch.dim.penalty_area_top,
                                pitch.dim.top
                                ]))

    # Transform values
    xstart, ystart = standard.transform(df['x'], df['y'])

    # Count passes per zone
    bin_statistic = pitch.bin_statistic(xstart, ystart,
                                            statistic='count',
                                            bins=(bin_x, bin_y),
                                            normalize=True)

    # Create custom colormap from viz base color
    # clist = custom_cmap(event1_marker_color1)
    # Original hand-picked colors
    clist = ['#FFF1DB', '#FFE9CE', '#de9314', '#99610F']
    clist = ["#38383b", "red"]

    # Custom color map
    ccmap = LinearSegmentedColormap.from_list("custom", clist)

    # Plot heatmap

    pitch.heatmap(bin_statistic,
                    ax=ax,
                    cmap=ccmap,
                    # edgecolor='#03191E',
                    edgecolor='blue',
                    alpha=0.5,
                    zorder=0,
                    linestyle=(0, (5,10))
                        )



if __name__ == "__main__":
    
    bg_color = '#faf9f4'
    bg_color = "#38383b"
    
    fp = 'data/imbabura-delfin.json'
    team = "Delfin"
    df = read_data(fp, get_qualifiers())
    
    # Draw the pitch
    pitch = VerticalPitch(line_color='white')
    
    # Show the plot
    fig = plt.figure(layout='constrained', figsize=(9.5, 4))
    fig.patch.set_facecolor(bg_color)

    ax_title = fig.add_axes([0, 1.05, 1, 0.2], anchor='SW', zorder=1)
    ax_title.axis('off')
    ax_annotate = fig.add_axes([0, -0.16, 1, 0.125], anchor='NW', zorder=1)
    ax_annotate.axis('off')

    subfigs = fig.subfigures(1, 3, wspace=0.07, width_ratios=[1, 1, 1])

    axsLeft = subfigs[0].subplots(1, 1)
    axsMiddle = subfigs[1].subplots(1, 1)
    axsRight = subfigs[2].subplots(1, 1)
    
    ax_title.text(x=0.5, y=0.5, s="Hello World")
    
    pitch.draw(ax=axsLeft)
    pitch.draw(ax=axsMiddle)
    pitch.draw(ax=axsRight)

    axsLeft.set_facecolor(bg_color)
    axsMiddle.set_facecolor(bg_color)
    axsRight.set_facecolor(bg_color)
    
    # Passes to box
    pdf = filter_passes_to_box(df=df, team=team)
    add_box_passes(pitch=pitch, ax=axsLeft, df=pdf)
    add_box_heatmap(pitch=pitch, ax=axsLeft, df=pdf)
    
    
    
    # ------------------------------- Save fig
    plt.savefig('images/20240501_viz.png',
                bbox_inches='tight',
                dpi=250
                )

