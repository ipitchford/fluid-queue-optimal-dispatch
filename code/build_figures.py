"""Generate the two figures of the paper. Usage: python3 build_figures.py OUTPUT_DIR"""
import argparse
import os
from pathlib import Path
import tempfile
import numpy as np
os.environ.setdefault("MPLCONFIGDIR",str(Path(tempfile.gettempdir())/"fluid_dispatch_mpl_cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fluid_quadrature import Law, FluidSolution  # noqa: E402

COLOURS=["#6A3B72","#00897B","#B27617","#BF577D"]
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8.5,
    "axes.labelsize":8.5,"axes.titlesize":10,"legend.fontsize":7.3,
    "axes.spines.top":False,"axes.spines.right":False,
    "axes.edgecolor":"#77717B","axes.labelcolor":"#312B34",
    "xtick.color":"#55505A","ytick.color":"#55505A",
    "grid.color":"#DDD8DE","grid.linewidth":0.5,
    "mathtext.fontset":"stix","savefig.facecolor":"white"})


def build(out):
    out.mkdir(parents=True,exist_ok=True)
    fig,axs=plt.subplots(1,2,figsize=(7.1,3.45),layout="constrained")
    ax=axs[0]
    points=np.array([[.5,.5],[4/7,5/14],[9/14,0],[0,0]])
    ax.plot(points[:,0],points[:,1],color=COLOURS[0],lw=2.0,zorder=3)
    ax.scatter(points[:-1,0],points[:-1,1],s=20,color=COLOURS[0],zorder=4)
    for first,second in zip(points[:-1],points[1:]):
        a=first+.43*(second-first); b=first+.58*(second-first)
        ax.annotate("",xy=b,xytext=a,arrowprops={"arrowstyle":"->","color":COLOURS[0],"lw":1.3})
    ax.plot([.5,.75,0],[.5,0,0],color=COLOURS[2],ls="--",lw=1.2,label="Most work left")
    ax.plot([0,.55],[0,.55],color="#B0A8B2",lw=.8,ls=":")
    ax.text(.46,.524,"Start",ha="right",fontsize=8)
    ax.annotate("Size split starts",xy=points[1],xytext=(.17,.32),
        arrowprops={"arrowstyle":"-","color":"#77717B","lw":.7},fontsize=8)
    ax.annotate("Short queue empty",xy=points[2],xytext=(.36,.10),
        arrowprops={"arrowstyle":"-","color":"#77717B","lw":.7},fontsize=8)
    ax.set(xlim=(-.02,.81),ylim=(-.025,.57),xlabel="Longer queue workload",ylabel="Shorter queue workload")
    ax.set_title("A. Exact optimal workload path",loc="left")
    ax.grid(alpha=.6)
    ax.legend(handles=[plt.Line2D([],[],color=COLOURS[0],lw=2,label="Optimal"),
                       plt.Line2D([],[],color=COLOURS[2],ls="--",label="Most work left")],loc="upper left",frameon=False)
    ax=axs[1]
    zstar=3/13
    for level in [.5,1.5]:
        ax.add_patch(Rectangle((0,level-.14),1,.28,color=COLOURS[0],alpha=.94))
    ax.add_patch(Rectangle((zstar,.36),1-zstar,.28,color=COLOURS[1],alpha=.94))
    ax.axvline(zstar,color="#77717B",lw=.9,ls="--")
    ax.text(zstar,1.83,r"$z=3/13$",ha="center",fontsize=9)
    ax.text(.50,.98,"Initially both sizes use the longer queue.\nAfter the switch, small jobs use the shorter queue.",
            fontsize=7.0,va="center",ha="center",bbox={"facecolor":"white","edgecolor":"none","pad":2})
    ax.set(xlim=(0,1.02),ylim=(-.13,1.98),xlabel=r"Relative imbalance $z=|u_1-u_2|/(u_1+u_2)$",ylabel="Job size")
    ax.set_yticks([.5,1.5],[r"$1/2$",r"$3/2$"])
    ax.set_title("B. Routing before either queue empties",loc="left")
    ax.legend(handles=[Patch(color=COLOURS[0],label="To longer queue"),
                       Patch(color=COLOURS[1],label="To shorter queue")],
              loc="lower left",frameon=True,facecolor="white",edgecolor="white",framealpha=1,fontsize=7)
    fig.savefig(out/"two_point_policy.png",dpi=300)
    plt.close(fig)

    laws=[(Law("exponential"),"Exponential"),(Law("gamma",4),"Gamma (shape 4)"),
          (Law("pareto",1.5),"Pareto (shape 1.5)"),(Law("two_point"),"Two sizes")]
    fig,axs=plt.subplots(1,2,figsize=(7.1,3.25),layout="constrained")
    for (law,label),colour in zip(laws,COLOURS):
        model=FluidSolution(law,.75)
        path=model.path(1,0,count=110)
        x,y=path[:,0],path[:,1]
        axs[0].plot((x+y)/2,(x-y)/2,color=colour,lw=1.7,label=label)
        axs[0].scatter([(x[-1]+y[-1])/2],[0],color=colour,s=14,zorder=3)
        fraction=(1-x)/(1-x[-1])
        axs[1].plot(fraction,y/x,color=colour,lw=1.7)
    axs[0].plot([0,.5],[0,.5],color="#B0A8B2",lw=.8,ls=":")
    axs[0].scatter([.5],[.5],color="#302635",s=15,zorder=4)
    axs[0].set(xlim=(.30,.68),ylim=(-.02,.53),xlabel="Longer queue workload",ylabel="Shorter queue workload")
    axs[0].set_title("A. Workload trajectories",loc="left")
    axs[0].legend(loc="lower left",frameon=False)
    axs[1].set(xlim=(0,1),ylim=(0,1.015),xlabel="Fraction of time to first empty queue",ylabel="Relative imbalance")
    axs[1].set_title("B. Imbalance grows along every path",loc="left")
    for ax in axs: ax.grid(alpha=.6)
    fig.savefig(out/"optimal_paths.png",dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("out",type=Path,help="output directory")
    build(parser.parse_args().out)
