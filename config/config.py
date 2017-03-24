
#  ---------- START OF VARIABLES FOR MANIPULATION BY USER ---------- #
#  ----------------------------------------------------------------- #
import os.path

MATERIAL = "water"

#Link this to your system's rat source
basepath = os.path.dirname(__file__)
ratpath = os.path.abspath(os.path.join(basepath,"..","..","..",".."))
sourcetype = "env_rat-dev.sh"
RATSRC = ratpath + "/" + sourcetype

#Toggles which mask should be used in 2nd pass processing (processing.mac).
#Don't change this unless you really know what you're doing!
default_apply = "default_apply"

#analysis_flags used to make CleanData.mac. See README for more info. on usage. 
#analysis_flags = ["neckcut","muontag"]
analysis_flags = ["zerozerocut"]

#Options for changing the output of the dcaProc ran in RunDCAProc.mac
types = ["timediff","flagged"]

#Toggles if you want to save the "clean"/"dirty" roots after data cleaning
getclean = False
getdirty = True
dcopts = {"getclean":getclean,"getdirty":getdirty}  

#if fullprocess is True, runs hit cleaning, reconstruction, the whole 9 yards
#if procntuple is true, also outputs the processed ntuple
fullprocess = False
procntuple = True
procopts = {"fullprocess":fullprocess, "ntuple":procntuple}
#  ---------------------- END USER MANIPULATION -------------------- #
#  ----------------------------------------------------------------- #


