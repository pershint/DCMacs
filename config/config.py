
#  ---------- START OF VARIABLES FOR MANIPULATION BY USER ---------- #
#  ----------------------------------------------------------------- #
import os.path

MATERIAL = "water"

#Link this to your system's rat source
basepath = os.path.dirname(__file__)
ratpath = os.path.abspath(os.path.join(basepath,"..","..",".."))
sourcetype = "env.sh"
RATSRC = ratpath + "/" + sourcetype

#Toggles which mask should be used in 2nd pass processing (processing.mac).
#This doesn't split the data; just indicates which flags an event COULD get
#Don't change this unless you know what you're doing!
apply_mask = "default_apply"

#Analysis mask used to actually split the data with CleanData.mac.
#If an event in the infed processed root files has any of the flags in
#The analysis_type defined, it is saved to the "dirty" ROOT file.
#analysis_type = {"flag":["muontag","neckcut"]}
analysis_type = {"mask":"analysis_mask"}



#Options for changing the output of the dcaProc ran in RunDCAProc.mac
types = ["timediff","flagged"]

#Toggles if you want to save the "clean"/"dirty" roots after data cleaning
getclean = True
getdirty = False

#Set the output type you want for the data cleaned files 
output_type = "ntuple"    #ntuple or ratds
#  ---------------------- END USER MANIPULATION -------------------- #
#  ----------------------------------------------------------------- #


