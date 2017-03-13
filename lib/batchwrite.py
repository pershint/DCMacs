#Classes write out a batchfile that will run the macros from macwrite.py
#On a single zdab file.

import os
import os.path
from subprocess import call

basepath = os.path.dirname(__file__)
batchpath = os.path.abspath(os.path.join(basepath, "..", "batchscripts"))
macropath = os.path.abspath(os.path.join(basepath, "..", "outmacs"))
ratpath = os.path.abspath(os.path.join(basepath, "..","..",".."))

class BatchScript(object):
    def __init__(self,name,macro_list):
        self.name = name
        self.macro_list = macro_list
        self.batchloc = batchpath + "/" + self.name
        self.batchfile = open(self.batchloc,"w")
        self.write()

    def write(self):
        self.batchfile.write("source " + ratpath + "/env.sh\n")
        for macroname in self.macro_list:
            self.batchfile.write("rat " + macropath + "/" + macroname + "\n")

    def save(self):
        self.batchfile.close()

    def run(self):
        call(["bash",self.batchloc])

    def delete(self):
        os.remove(self.batchloc)
        print("Removed " + self.name + " from batchscripts directory")
