import pandas as pd
import json
import numpy as np

from mplsoccer import Pitch, VerticalPitch, Standardizer

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import rcParams



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
    

def add_box_passes(pitch: Pitch, ax: plt.axis, df, flip):
  
    standard = Standardizer(pitch_from='opta', pitch_to='statsbomb')
    ax.set_title("Pases al area",
                 c="white",
                 fontsize=13
                 )
    
    size = rcParams['lines.markersize'] ** 1.7
    
    ### FAILED PASSES
    color = '#c1c1bf'
    failed = df['outcome'] == 0

    x, y = standard.transform(df['x'][failed], df['y'][failed])
    xend, yend = standard.transform(df["Pass End X"][failed], df["Pass End Y"][failed])

    if flip:
        x, y = pitch.flip_side(x, y, [True]*len(x))
        xend, yend = pitch.flip_side(xend, yend, [True]*len(xend))
    
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
        zorder=1
                )
    
    ev2 = pitch.scatter(x=xend, y=yend,
                        s=size,
                        ax=ax,linewidth=1, color='#c1c1bf', zorder=0)

    ### SUCCESSFULL PASSES
    color = "green"
    success = df['outcome'] == 1

    x, y = standard.transform(df['x'][success], df['y'][success])
    xend, yend = standard.transform(df["Pass End X"][success], df["Pass End Y"][success])

    if flip:
        x, y = pitch.flip_side(x, y, [True]*len(x))
        xend, yend = pitch.flip_side(xend, yend, [True]*len(xend))
    
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
        zorder=2
                )

    ev2 = pitch.scatter(x=xend, y=yend,
                        s=size,
                        zorder=2,
                        ax=ax,linewidth=0, color=color)


def add_box_heatmap(pitch, ax, df, flip):

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
    
    if flip:
        xstart, ystart = pitch.flip_side(xstart, ystart, [True]*len(xstart))

    # Count passes per zone
    bin_statistic = pitch.bin_statistic(xstart, ystart,
                                            statistic='count',
                                            bins=(bin_x, bin_y),
                                            normalize=True)

    # Create custom colormap from viz base color
    # clist = custom_cmap(event1_marker_color1)
    # Original hand-picked colors
    clist = ['#FFF1DB', '#FFE9CE', '#de9314', '#99610F']
    clist = [bg_color, "#03A9F4"]

    # Custom color map
    ccmap = LinearSegmentedColormap.from_list("custom", clist)

    # Plot heatmap

    pitch.heatmap(bin_statistic,
                    ax=ax,
                    cmap=ccmap,
                    # edgecolor='#03191E',
                    # edgecolor='blue',
                    alpha=0.5,
                    zorder=0,
                    linestyle=(0, (5,10))
                        )


def add_def_actions(df, pitch: Pitch, axs: list, c: str):
    """_summary_

    Args:
        df (_type_): _description_
        pitch (_type_): _description_
        axs (list): _description_
    """
    
    standard = Standardizer(pitch_from="opta", pitch_to="statsbomb")

    # BINS FOR HEATMAP
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
    max = 0
    
    stat = [
        "Interception"
        "Ball recovery",
        "Clearance",
        "Foul",
        "Aerial",
        "Tackle",
        "Challenge",
        "Offside provoked"
        ]
    
    for i, team in enumerate(df.team.unique()):
        ax = axs[i]
        ax.set_title(
            label="Acciones defensivas",
            c="white"
                     )
        
        #Data
        pdf = df[df["team"] == team]
        pdf = pdf[pdf["event"] == "Clearance"]
        
        # Transform values
        x, y = standard.transform(pdf.x, pdf.y)

        # Get max events per zone
        new_max = pitch.bin_statistic(x, y, statistic='count', bins=(bin_x, bin_y))["statistic"].max()
        max = new_max if new_max > max else max
    
    # Loop for drawing on pitch
    for i, team in enumerate(df.team.unique()):
        flip = False if i==0 else True
        ax = axs[i]
        #Data
        pdf = df[df["team"] == team]
        pdf = pdf[pdf["event"].isin(stat)]
        # Transform values
        x, y = standard.transform(pdf['x'], pdf['y'])
        
        if flip:
            x, y = pitch.flip_side(x, y, [True] * len(x))

        # Count events per zone
        bin_statistic = pitch.bin_statistic(x, y,
                                                statistic='count',
                                                bins=(bin_x, bin_y)
                                                )
        
        clist = [bg_color,  "#03A9F4"]
        # Custom color map
        ccmap = LinearSegmentedColormap.from_list("custom", clist)

        # Plot heatmap

        pitch.heatmap(bin_statistic,
                        ax=ax,
                        cmap=ccmap,
                        # edgecolor='#03191E',
                        alpha=0.5,
                        zorder=0,
                        # linestyle=(0, (5,10)),
                        vmax=max,
                        shading="auto"
                            )
    
        # Add average defensive action line
        pdf = df[df["team"] == team]
        pdf = pdf[pdf["event"].isin(stat)]
        
        x, y = standard.transform(pdf.x, pdf.y)
        if i > 0:
            x, y = pitch.flip_side(x, y, [True]*len(x))

        d = np.sqrt(np.power(x - 0, 2) + np.power(y - 40, 2)).mean()

        pitch.lines(
            xstart=d,
            ystart=-3,
            xend=d,
            yend=83,
            ax=ax,
            color='white',
            linestyles='dashed',
            alpha=1,
            linewidth=2.5,
            clip_on=False,
            zorder=-1,
        )

if __name__ == "__main__":
    
    bg_color = '#faf9f4'
    bg_color = "#38383b"
    
    fp = 'data/imbabura-delfin.json'
    team = "Delfin"
    df = read_data(fp, get_qualifiers())
    
    # Draw the pitch
    pitch = Pitch(line_color='white', linewidth=0.5)
    
    # Show the plot
    fig = plt.figure(layout='constrained', figsize=(9.5, 4))
    fig.patch.set_facecolor(bg_color)

    ax_title = fig.add_axes([0, 1.05, 1, 0.2], anchor='SW', zorder=1)
    ax_title.axis('off')
    ax_annotate = fig.add_axes([0, -0.16, 1, 0.125], anchor='NW', zorder=1)
    ax_annotate.axis('off')

    subfigs = fig.subfigures(1, 2, wspace=0.07, width_ratios=[1, 1])

    ax1, ax3 = subfigs[0].subplots(2, 1) #1st team are odd axes
    ax2, ax4 = subfigs[1].subplots(2, 1) #2nd team are even axes
    
    axs = {df.team.unique()[0]: [ax1, ax3],
           df.team.unique()[1]: [ax2, ax4]}
    
    teams = df.team.unique()
    ax_title.text(x=0.5, y=0.5,
                  s=f"{teams[0]} vs. {teams[1]}",
                  c="white",
                  ha="center",
                  fontsize=22
                  )
    
    # Draw pitches on all the empty axes
    pitch.draw(ax=ax1)
    pitch.draw(ax=ax2)
    pitch.draw(ax=ax3)
    pitch.draw(ax=ax4)

    # Change axes background color
    ax1.set_facecolor(bg_color)
    ax2.set_facecolor(bg_color)
    ax3.set_facecolor(bg_color)
    ax4.set_facecolor(bg_color)
    
    # Add Passes to box
    for i, team in enumerate(df.team.unique()):
        ax = axs[team]
        flip = False if i==0 else True
        pdf = filter_passes_to_box(df=df, team=team)
        add_box_heatmap(pitch=pitch, ax=ax[0], df=pdf, flip=flip)
        add_box_passes(pitch=pitch, ax=ax[0], df=pdf, flip=flip)
        
    
    add_def_actions(df=df, pitch=pitch, axs=[ax3, ax4], c=bg_color)
    
    
    # ------------------------------- Save fig
    plt.savefig('images/20240501_viz.png',
                bbox_inches='tight',
                dpi=250
                )

