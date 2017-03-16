
#  ---------- START OF VARIABLES FOR MANIPULATION BY USER ---------- #
#  ----------------------------------------------------------------- #
import os.path

MATERIAL = "water"

#Link this to your system's rat source
basepath = os.path.dirname(__file__)
ratpath = os.path.abspath(os.path.join(basepath,"..","..","..",".."))
sourcetype = "env_rat-dev.sh"
RATSRC = ratpath + "/" + sourcetype

#mask used to make CleanData.mac. See README for more info. on usage. 
masks = ["neckcut","muontag"]

#Options for changing the output of the dcaProc ran in RunDCAProc.mac
types = ["timediff","flagged"]

getclean = False
getdirty = True
cdget = [getclean,getdirty]  
#  ---------------------- END USER MANIPULATION -------------------- #
#  ----------------------------------------------------------------- #


