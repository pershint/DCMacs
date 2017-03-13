
#  ---------- START OF VARIABLES FOR MANIPULATION BY USER ---------- #
#  ----------------------------------------------------------------- #
MATERIAL = "water"
#mask used to make CleanData.mac; events in the clean output have none of
#these dc flags. events in the dirty output have one or more or these flags.
masks = ["default","muontag"]

#Options for changing the output of the dcaProc ran in RunDCAProc.mac
types = ["timediff","flagged"]

getdirty = True
#  ---------------------- END USER MANIPULATION -------------------- #
#  ----------------------------------------------------------------- #


