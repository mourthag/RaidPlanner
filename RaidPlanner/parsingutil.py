import datetime
import re

def parse_date(arg):

    if arg == "today":
       return datetime.datetime.today()
    else:
       return datetime.datetime.today()

def parse_time(arg):

    if re.match("\d?\dam", arg):
        return datetime.time(hour=int(arg[0]))    
    if re.match("\d?\dpm", arg):
        return datetime.time(hour=int(arg[0])+12)
    if re.match("\d?\d:\d\d", arg):
        vals = arg.split(":")
        return datetime.time(hour=int(vals[0]), minute=int(vals[1]))
    else:
        return datetime.time(hour=0)
