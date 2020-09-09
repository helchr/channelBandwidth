#!/usr/bin/python

import sys
import lots_plots as lp 
g = lp.lots_plots()

db = str(sys.argv[1])
outList = db.split(".")[:-1]
out = ".".join(outList)

sockets=g.do_sql(db,"select distinct socket from imc order by socket",single_col=1)
channels=g.do_sql(db,"select distinct channel from imc order by channel",single_col=1)

def plotBwByTime():
    query="""
    select time, bwRead + bwWrite from
    (select time,bw as bwRead from imc where socket = {socket} and channel = {channel} and access = "read")
    inner join
    (select time,bw as bwWrite from imc where socket = {socket} and channel = {channel} and access = "write")
    using (time)
    """

    g.default_terminal = """pdf noenhanced font ',14' size 8,4"""
    g.graphs((db, query),
        graph_attr="""set key top right outside title 'Channel' samplen 3
        set ylabel offset 1,0,0
        set xlabel offset 0,0.5,0
        set title offset 0,-0.5,0
        """,
        output=out+"-socket{socket}.pdf",
        plot_with="linespoints",
        using="1:2",
        graph_title="Channel Bandwidth on Socket {socket}",
        plot_title="{channel}",
        xlabel="Time (s)",
        ylabel="Bandwidth (MB/s)",
        channel=channels,
        socket=sockets,
        graph_vars=["socket"])

plotBwByTime()

