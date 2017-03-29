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
    def __init__(self,name,ratsource,macro_list,runinfo):
        self.name = name
	self.ratsource = ratsource
        self.macro_list = macro_list
        self.runinfo = runinfo #Format RUNNUM_SUBNUM
        self.bashloc = bashpath + "/" + self.name
        self.bashfile = open(self.bashloc,"w")
        self.write()

    def write(self):
        self.bashfile.write("source " + self.ratsource + "\n")
        if self.runinfo:
            runpath = runlogpath + "/" + self.runinfo
            self.bashfile.write("mkdir " + runpath + "\n")
            self.bashfile.write("cd " + runpath + "\n")
        else:
            self.bashfile.write("cd " + mainpath + "\n")
        for macroname in self.macro_list:
            self.bashfile.write("rat " + macropath + "/" + macroname + "\n")

    def save(self):
        self.bashfile.close()

    def run(self):
        call(["bash",self.bashloc])

    def delete(self):
        os.remove(self.bashloc)
        print("Removed " + self.name + " from bashscripts directory")
