#This file contains classes for writing out particular types of macros
#For RAT.  The macros are specifically focused on the SNO+ geometry.
import os
import os.path
import glob
from subprocess import call

basepath = os.path.dirname(__file__)
macropath = os.path.abspath(os.path.join(basepath, "..","outmacs"))
zdpath = os.path.abspath(os.path.join(basepath, "..","data","zdabs"))
prpath = os.path.abspath(os.path.join(basepath, "..","data","proc_roots"))
drpath = os.path.abspath(os.path.join(basepath, "..","data","datacleaned_roots"))
dcarpath = os.path.abspath(os.path.join(basepath, "..","data","dcaocc"))

#Base class for all macros.  Writes to ignore Muonic/Hadronic processes
class Macro(object):
    def __init__(self,filename,material):
        self.filename = filename
        self.macloc = macropath + "/" + self.filename
        self.mac = open(self.macloc,"w")
        self.material = material
        self.write_init()

    def write_init(self):
        self.mac.write("#Start of file\n")
        self.mac.write("/rat/physics_list/OmitAll true\n")
        self.mac.write("\n")


    def save(self):
        self.mac.close()

    def delete(self):
        os.remove(self.macloc)
        print("removed " + self.filename + "from outmacs\n")

#Class writes your first pass data cleaning macro for a list of zdabs associated with one run
class FPMacro(Macro):
    '''Class takes in a list of zdabs and writes the first pass of data
    cleaning on all zdabs in the list.  The first pass does not output
    any new files; only writes RATDB tables needed for the second pass
    processing of livetime cuts.'''

    def __init__(self,zdablist, *args, **kwargs):
        super(FPMacro, self).__init__(*args, **kwargs)
        self.zdablist = zdablist
        self.write_main()
        self.save()
        
    def write_main(self):
        for zdab in self.zdablist:
            zdab = zdpath + "/" + zdab
            self.mac.write('/rat/inzdab/load {}\n'.format(zdab))
        self.mac.write('/rat/db/set DETECTOR geo_file "geo/snoplus_{}.geo"\n'.format(self.material))
        self.mac.write('\n')
        self.mac.write("/run/initialize\n\n")
        self.mac.write("### EVENT LOOP ###\n")
        self.mac.write("/rat/proc datacleaning\n")
        self.mac.write('/rat/procset add "tpmuonfollowercut"\n')
        self.mac.write('/rat/procset add "missedmuonfollower"\n')
        self.mac.write('/rat/procset add "pedcut"\n')
        self.mac.write('/rat/procset add "atmospheric"\n')
        self.mac.write("/rat/procset pass 1\n")
        self.mac.write("### END EVENT LOOP ###\n")
        self.mac.write("/rat/inzdab/read\n")
        self.mac.write("exit")

class SPMacro(Macro):
    def __init__(self,zdablist, *args, **kwargs):
        '''Class takes in a list of zdabs and writes the second
        pass of data cleaning macro.  Data cleaning is run on all
        events in the subfiles and output to a single ratds or
        ntuple.'''

        super(SPMacro, self).__init__(*args, **kwargs)
        self.zdablist = zdablist
        outroot_list = []
        self.write_main()
        self.save()

        self.fileinfo= self.zdablist[0].replace("SNOP_",
                "").replace(".zdab","").replace(".l2","")
        self.rootout = "DCMProcessed_"+self.fileinfo
        self.ntloc = prpath + "/" + self.rootout + "_ntuple.root"
        self.rootloc = prpath + "/" + self.rootout + ".root"
        self.out_type = "ntuple"

    def setOutputType(self,outtype):
        '''specify if you want the ntuple output or full ratds output
        after the second pass processing (I.E. data cleaning completion)'''
        self.out_type = outtype
    
    def get_procrootname(self):
        if self.out_type == "ratds":
            return self.rootloc.replace(prpath + "/","")
        elif self.out_type == "ntuple":
            return self.ntloc.replace(prpath + "/","")

    def write_main(self):
        for zdab in self.zdablist:
            zdab = zdpath + "/" + zdab
            self.mac.write('/rat/inzdab/load {}\n'.format(zdab))
        self.mac.write('/rat/db/set DETECTOR geo_file "geo/snoplus_{}.geo"\n'.format(self.material))
        self.mac.write('\n')
        self.mac.write("/run/initialize\n\n")
        self.mac.write("### EVENT LOOP ###\n")

        self.mac.write("/rat/proc calibratePMT\n")
        self.mac.write("/rat/proc triggerEfficiency\n")
        self.mac.write("/rat/proc reconstructClocks\n")
        self.mac.write("/rat/proc datacleaning\n")
        self.mac.write('/rat/procset mask "default_apply"\n')
        self.mac.write('/rat/procset add "tpmuonfollowercut"\n')
        self.mac.write('/rat/procset add "missedmuonfollower"\n')
        self.mac.write('/rat/procset add "pedcut"\n')
        self.mac.write('/rat/procset add "atmospheric"\n')
        self.mac.write("/rat/procset pass 2\n")
        if self.out_type == "ratds":
            self.mac.write('/rat/proclast outroot\n')
        elif self.out_type == "ntuple":
            self.mac.write('/rat/proclast outntuple\n')
        else:
            print("OUTPUT FORMAT SPECIFIED NOT SUPPORTED IN RAT. Choose"+\
                    "either 'ratds' or 'ntuple' with self.setOutputType")
            sys.exit(1)

        self.mac.write("### END EVENT LOOP ###\n")
        self.mac.write("/rat/inzdab/read\n")
        self.mac.write("exit")

#Class takes in the desired masks and outputs both a "cleaned" root (events where
#The event did not have any of the flags set) and a "dirty" root (events where
#The event did have the data cleaning flags set).
class DCMacro(Macro):
    def __init__(self,procroot, analysis_type,dcopts,*args, **kwargs):
        super(DCMacro, self).__init__(*args, **kwargs)
        self.aflags = analysis_type
        self.procroot = prpath + "/" + procroot
        self.dcroot = drpath + "/" + procroot
        self.getclean = dcopts["getclean"]
        self.getdirty = dcopts["getdirty"]
        self.write_main()
        
    def write_main(self):
        self.mac.write('/rat/inroot/load {}\n'.format(self.procroot))
        self.mac.write('\n')
        self.mac.write("/run/initialize\n\n")

        self.mac.write("### EVENT LOOP ###\n")
        #FIXME: Need these lines if DCing data processed on the grid
        self.mac.write("/rat/proc datacleaning\n")
        self.mac.write('/rat/procset mask "{}"\n'.format("default_apply"))
	for key in self.aflags:
            if key == 'flag':
                flagarr = self.aflags[key]
		for flag in flagarr:
		    self.mac.write("/rat/proc/if dataCleaningCut\n")
		    self.mac.write('/rat/procset flag "{}"\n'.format(flag))
		    if self.getclean:
			self.mac.write('    /rat/proc outroot\n')
			self.mac.write('    /rat/procset file "{0}_{1}_clean.root"\n'.format(self.dcroot.rstrip('.root'),flag))
		    if self.getdirty:
			self.mac.write("/rat/proc/else\n")
			self.mac.write('    /rat/proc outroot\n')
			self.mac.write('    /rat/procset file "{0}_{1}_dirty.root"\n'.format(self.dcroot.rstrip('.root'),flag))
		    self.mac.write("/rat/proc/endif\n")
            if key == 'mask':
	        self.mac.write("/rat/proc/if dataCleaningCut\n")
	        self.mac.write('/rat/procset mask "{}"\n'.format(self.aflags[key]))
	        if self.getclean:
		    self.mac.write('    /rat/proc outroot\n')
		    self.mac.write('    /rat/procset file "{0}_{1}_clean.root"\n'.format(self.dcroot.rstrip('.root'),self.aflags[key]))
	        if self.getdirty:
		    self.mac.write("/rat/proc/else\n")
		    self.mac.write('    /rat/proc outroot\n')
		    self.mac.write('    /rat/procset file "{0}_{1}_dirty.root"\n'.format(self.dcroot.rstrip('.root'),self.aflags[key]))
	        self.mac.write("/rat/proc/endif\n")
        self.mac.write("### END EVENT LOOP ###\n\n")

        self.mac.write("/rat/inroot/read\n\n")

        self.mac.write("exit")


#FIXME: DCAProcMacro assumes that your file is in proc_roots.  What about the
#"clean" or "dirty" files output to dc_roots?
class DCAProcMacro(Macro):
    def __init__(self,procroot, types, *args, **kwargs):
        super(DCAProcMacro, self).__init__(*args, **kwargs)
        self.types = types
        self.procroot = prpath + "/" + procroot
        self.dcaroot = dcarpath + "/" + procroot
        self.write_main()
        
    def write_main(self):
        self.mac.write('/rat/inroot/load {}\n'.format(self.procroot))
        self.mac.write('\n')
        self.mac.write("/run/initialize\n\n")

        self.mac.write("### EVENT LOOP ###\n")
        self.mac.write("/rat/proc count\n")
        self.mac.write("/rat/procset update 100\n\n")

        self.mac.write("/rat/proc dcaProc\n")
        for onetype in self.types:
            self.mac.write('/rat/procset type "{}"\n'.format(onetype))
        self.mac.write('/rat/procset file "{}_dcaProcHists.root"\n'.format( \
                self.dcaroot.rstrip(".root")))

        self.mac.write("### END EVENT LOOP ###\n\n")

        self.mac.write("/rat/inroot/read\n\n")

        self.mac.write("exit")

class OccProcMacro(Macro):
    def __init__(self,procroot, *args, **kwargs):
        super(OccProcMacro, self).__init__(*args, **kwargs)
        self.types = ["slot","crate","channel"]
        self.procroot = prpath + "/" + procroot
        self.dcaroot = dcarpath + "/" + procroot
        self.write_main()
        
    def write_main(self):
        self.mac.write('/rat/inroot/load {}\n'.format(self.procroot))
        self.mac.write('\n')
        self.mac.write("/run/initialize\n\n")

        self.mac.write("### EVENT LOOP ###\n")
        self.mac.write("/rat/proc count\n")
        self.mac.write("/rat/procset update 100\n\n")

        self.mac.write("/rat/proc dcaProc\n")
        for onetype in self.types:
            self.mac.write('/rat/procset type "{}"\n'.format(onetype))
        self.mac.write('/rat/procset file "{}_occProcHists.root"\n'.format( \
                self.dcaroot.rstrip(".root")))

        self.mac.write("### END EVENT LOOP ###\n\n")

        self.mac.write("/rat/inroot/read\n\n")

        self.mac.write("exit")

