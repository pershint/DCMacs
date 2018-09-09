#classes write out a bashfile that will run the macros from macwrite.py
#On a single zdab file.

import os
import os.path
import macwrite as m
from subprocess import call

basepath = os.path.dirname(__file__)
bashpath = os.path.abspath(os.path.join(basepath, "..", "bashscripts"))
mainpath = os.path.abspath(os.path.join(basepath, ".."))
runlogpath = os.path.abspath(os.path.join(basepath, "..","data","runlogs"))
macropath = m.macropath

class BashScript(object):
    def __init__(self,ratsource,macro_list=None,runinfo=None,slurmjob=False):
        self.name = "default_bashname.sh" 
	self.ratsource = ratsource
        self.macro_list = macro_list
        self.runinfo = runinfo #Format RUNNUM_SUBNUM
        self.bashloc = None 

    def Set_RunInfo(self,runinfo):
        '''Sets the subrun info for logging each subrun's processing'''
        self.runinfo = runinfo

    def Set_ScriptPath(self,loc):
        '''Sets the path and filename for saving the bash script at.'''
        self.bashloc = loc 

    def write(self):
        if self.bashloc is None:
            print("You must specify a location to write the script to!")
            sys.exit(0)
        self.bashfile = open(self.bashloc,"w")
        if slurmjob:
            print("Slurm header implementation not yet supported.  Soooon")
        self.bashfile.write("source " + self.ratsource + "\n")
        if self.runinfo:
            runpath = runlogpath + "/" + self.runinfo
            self.bashfile.write("mkdir -p " + runpath + "\n")
            self.bashfile.write("cd " + runpath + "\n")
        else:
            self.bashfile.write("cd " + mainpath + "\n")
        for macroname in self.macro_list:
            self.bashfile.write("rat " + macropath + "/" + macroname + "\n")

    def save(self):
        self.bashfile.close()

    def run(self):
        if slurmjob:
            print("call command for submitting to slurm not implemented yet.")
            sys.exit(0)
        else:
            call(["bash",self.bashloc])

    def delete(self):
        os.remove(self.bashloc)
        print("Removed " + self.name + " from bashscripts directory")
