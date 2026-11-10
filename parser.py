"""Parsning af rå loglinjer til strukturerede logrecords."""


import datetime
from time import strptime

import log_creation as log_creation


def sepperation(lines):
    list_of_logs = []
    for i in range(len(lines)):
        line_split_initial = lines[i].split(" ")
        section1 = str(line_split_initial[1])
        section2 = str(line_split_initial[2])
        section3 = str(line_split_initial[3])
        section4 = str(line_split_initial[4])
        section5 = str(line_split_initial[5])
        section6 = str(line_split_initial[6])
        section7 = str(line_split_initial[7])
        event = section2.split("=")
        event = event[1]
        user = section3.split("=")
        user = user[1]
        level = section1.split("=")
        level = level[1]
        src = section4.split("=")
        src = src[1]
        dest = section5.split("=")
        dest = dest[1]
        port = section6.split("=")
        port = int(port[1])
        status = section7.split("=")
        status = status[1]
        timestamp = line_split_initial[0]
        msg = lines[0].split("=")
        msg = msg[-1]
        timestamp=strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
        name = f"{timestamp}.{user}.{event}.{status}"
        list_of_logs.append(log_creation.Memory(event, user, level, src, dest, port, status, timestamp, msg, name))
    return list_of_logs
