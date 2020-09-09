#!/usr/bin/python3
import glob
import subprocess
import argparse
import os
import sqlite3

def addBandwidth():
    update = """update imc set bw = ?  
    where socket = ? and channel = ? and access = ? and time = ?"""
    select = "select socket,channel,access,time,size from imc"
    con = sqlite3.connect(output)
    con.execute("alter table imc add column bw real")
    cur = con.cursor()
    cur.execute(select)
    data = cur.fetchall()
    lastTime = {} 
    for row in data:
        socket = row[0]
        channel=row[1]
        access=row[2]
        time=float(row[3])
        data=float(row[4])
        print(socket,channel,time,data)
        deltaTime = time
        lastTime = {}
        if socket in lastTime:
            if channel in lastTime[socket]:
                if access in lastTime[socket][channel]:
                    deltaTime = time-lastTime[socket][channel][access]
                else:
                    lastTime[socket][channel][access] = time;
            else:
                lastTime[socket][channel] = {}
                lastTime[socket][channel][access] = time;
        else:
            lastTime[socket] = {}
            lastTime[socket][channel] = {}
            lastTime[socket][channel][access] = time;
        bw = data/deltaTime
        cur.execute(update,(bw,socket,channel,access,time))
    con.commit()
    con.close()

parser = argparse.ArgumentParser()
parser.add_argument("--output","-o",default="perf.db")
parser.add_argument("--csv",action="store_true",default=False)
parser.add_argument("command",nargs=argparse.REMAINDER)
args = parser.parse_args()
output = args.output;
outputTemp = args.output + ".csv"

devPath = "/sys/bus/event_source/devices/uncore_imc_*"
readEvent = "cas_count_read"
writeEvent = "cas_count_write"
eventString = ""

for imcPath in glob.glob(devPath):
    imc = imcPath.split("/")[-1]
    eventString += imc + "/" + readEvent + "/" + "," + imc + "/" + writeEvent + "/" + ","

eventString = eventString[:-1]
perf = "perf"
command = " ".join(args.command)
perfOptions =  " stat --no-big-num --per-socket -I 500 -x , -o %s -e %s %s" % (outputTemp,eventString,command)

subprocess.call(perf + perfOptions,shell=True)

txt2sql="""
graphem/a2sql/bin/txt2sql "%s" --table imc \
--row '(?P<time>\d+\.\d+),S(?P<socket>\d),1,(?P<size>\d+\.\d+),MiB,uncore_imc_(?P<channel>\d)\/cas_count_(?P<access>read|write)' \
    "%s"
    """ % (output,outputTemp)

if not args.csv:
    if os.path.exists(output):
        os.remove(output)
    subprocess.call(txt2sql,shell=True)
    os.remove(outputTemp)
else:
    os.rename(outputTemp,output)

addBandwidth()