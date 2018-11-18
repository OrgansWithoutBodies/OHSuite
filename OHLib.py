#Library of functions and stuff which are useful for all apps in OH, 
#or are useful to be set the same across several apps
"""Imports
==================================================================================
"""
import datetime
import sqlite3

"""Misc fns 
==================================================================================
""" 
class Timer(): #times how long certain processes go, create timer object, then call lap to get seconds since either start or last lap
    def __init__(self):
        self.zero=datetime.datetime.now()
    def lap(self):
        self.dt=datetime.datetime.now()-self.zero
        self.zero=datetime.datetime.now()
        return self.dt
    
"""DB METHODS 
==================================================================================
"""   
def dbFilter(inp,typ=None): #removes formatting that may be deleterious to database stuff, have here as fn for consistency purposes
    if str in {type(inp),typ}: #
        try: out=str(int(inp))
        except: out=inp.lower().strip()  #makes lowercase, strips of spaces
    elif typ==int:
        out=int(float(inp))
    else: out=inp
    return out
def connwrite(path,commandtuple,many=0):    
    conn=sqlite3.connect(path)
    c=conn.cursor() #make some rollback thing/error handling
    try:
        if many==0:
            res=conn.execute(*commandtuple).fetchall()
        else:
            res=conn.executemany(*commandtuple).fetchall()
    except:
        raise
        res=None
    conn.commit()
    conn.close()
    return res

"""Links
==================================================================================
"""
#link to google form thing
feedbacklink=r'https://docs.google.com/forms/d/e/1FAIpQLSct6bhTmrjgvchtm0lEnV_-46xalMgC93DRTiUic6AjMnZILQ/formResponse'


"""Dicts/Lists
==================================================================================
""" 
FL=["First","Last"] #useful for dict comprehensions

rainbow=['Red','Orange','Yellow','Green','Blue','Purple']


"""Stats?
==================================================================================
""" 