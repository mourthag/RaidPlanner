import datetime
import re

def parse_date(arg):

   if arg == "today":
       return datetime.datetime.today()
   elif arg == "tomorrow":
       today = datetime.datetime.today()
       return today.replace(day=today.day+1)
   elif re.match("\d?\d.\d?\d.(\d\d)?", arg):
       vals = arg.split(".")
       year = datetime.datetime.today().year

       if len(vals) == 3 and vals[2] != "":
        year = int(vals[2])

       return datetime.datetime(month=int(vals[0]),day=int(vals[1]), year=year)
   else:
       return datetime.datetime.today()

def parse_time(arg):

    if re.match("\d?\dam", arg):
        match = re.search("\d?\d", arg)
        return datetime.time(hour=int(match.group(0)))    
    if re.match("\d?\dpm", arg):
        match = re.search("\d?\d", arg)
        return datetime.time(hour=int(match.group(0))+12)
    if re.match("\d?\d:\d\d", arg):
        vals = arg.split(":")
        return datetime.time(hour=int(vals[0]), minute=int(vals[1]))
    else:
        return datetime.datetime.now().time
