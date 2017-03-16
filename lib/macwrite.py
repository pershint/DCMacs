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
drpath = os.path.abspath(os.path.join(basepath, "..","data","dc_roots"))


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
        self.mac.write("/rat/physics_list/OmitMuonicProcesses true\n")
        self.mac.write("/rat/physics_list/OmitHadronicProcesses true\n")
        self.mac.write("\n")


    def save(self):
        self.mac.close()

    def delete(self):
        os.remove(self.macloc)
        print("removed " + self.filename + "from outmacs\n")

#Class writes your first pass data cleaning macro
class FPMacro(Macro):
    def __init__(self,zdab, *args, **kwargs):
        super(FPMacro, self).__init__(*args, **kwargs)
        self.zdab = zdpath + "/" + zdab
        self.write_main()
        self.save()
        
    def write_main(self):
        #TODO: Load in particular zdab?
        self.mac.write('/rat/inzdab/load {}\n'.format(self.zdab))
        self.mac.write('/rat/db/set DETECTOR geo_file "geo/snoplus_{}.geo"\n'.format(self.material))
        self.mac.write('\n')
        self.mac.write("/run/initialize\n\n")
        self.mac.write("### EVENT LOOP ###\n")
        self.mac.write("/rat/proc datacleaning\n")
        self.mac.write('/rat/procset add "tpmuonfollowercut"\n')
        self.mac.write("/rat/procset pass 1\n")
        self.mac.write("### END EVENT LOOP ###\n")
        self.mac.write("/rat/inzdab/read\n")
        self.mac.write("exit")

#Class writes your Main processing loop
class ProcMacro(Macro):
    def __init__(self,zdab, *args, **kwargs):
        super(ProcMacro, self).__init__(*args, **kwargs)
        self.zdabloc = zdpath + "/" + zdab
        self.ntloc = prpath + "/" + zdab.rstrip(".zdab") + "_ntuple.root"
        self.rootloc = prpath + "/" + zdab.rstrip(".zdab") + "_processed.root"
        self.write_main()
        
    def write_main(self):
        #TODO: Load in particular zdab?
        self.mac.write('/rat/inzdab/load {}\n'.format(self.zdabloc))
        self.mac.write('/rat/db/set DETECTOR geo_file "geo/snoplus_{}.geo"\n'.format(self.material))
        self.mac.write('\n')
        self.mac.write("/run/initialize\n\n")

        self.mac.write("### EVENT LOOP ###\n")
        self.mac.write("/rat/proc calibratePMT\n")
        self.mac.write("/rat/proc datacleaning\n")
        self.mac.write('/rat/procset mask "default"\n')
        self.mac.write('/rat/procset add "tpmuonfollowercut"\n')
        self.mac.write("/rat/procset pass 2\n")
        self.mac.write("/rat/proc hitcleaning\n")
        self.mac.write('/rat/procset mask "default"\n')
        self.mac.write("/rat/proc dqrunproc\n")
        self.mac.write("/rat/proc dqpmtproc\n")
        self.mac.write("/rat/proc dqtimeproc\n")
        self.mac.write("/rat/proc dqtriggerproc\n")
        self.mac.write("/rat/proc chanSWStatusCalib\n\n")

        self.mac.write("# Conditional logic for construction (exclude specific" + \
                "trigger types\n")
        self.mac.write("/rat/proc/if trigTypeSelector\n")
        self.mac.write('    /rat/procset trigType "PulseGT"\n')
        self.mac.write('    /rat/procset trigType "EXTASY"\n')
        self.mac.write('    /rat/procset trigType "Pedestal"\n')
        self.mac.write("/rat/proc/else\n")
        if self.material == "water":
            #FIXME: changed to waterFitter once it has been pushed to RAT
            self.mac.write('    /rat/proc partialWaterFitter\n')
        elif self.material == "partial":
            self.mac.write('    /rat/proc partialWaterFitter\n')
        elif self.material == "scintillator":
            self.mac.write('    /rat/proc scintFitter\n')
        else:
            print("Invalid material selected (OR TeDiol not implemented here.)" + \
                    "Try again with your material selection in ./config.")
            sys.exit(0)
        self.mac.write('/rat/proc/endif\n\n')

        self.mac.write('/rat/proc outntuple\n')
        self.mac.write('/rat/procset file "{}"\n'.format(self.ntloc))
        self.mac.write('/rat/proclast outroot\n')
        self.mac.write('/rat/procset file "{}"\n'.format(self.rootloc))
        self.mac.write("### END EVENT LOOP ###\n\n")

        self.mac.write("/rat/inzdab/read\n")
        self.mac.write("exit")

    def get_procrootname(self):
        return self.rootloc.replace(prpath + "/","")
    

#Class takes in the desired masks and outputs both a "cleaned" root (events where
#The event did not have any of the flags set) and a "dirty" root (events where
#The event did have the data cleaning flags set).
class DCMacro(Macro):
    def __init__(self,procroot, masks,cdget,*args, **kwargs):
        super(DCMacro, self).__init__(*args, **kwargs)
        self.masks = masks
        self.procroot = prpath + "/" + procroot
        self.dcroot = drpath + "/" + procroot
        self.getclean = cdget[0]
        self.getdirty = cdget[1] # Bools defined in config/config.py
        self.write_main()
        
    def write_main(self):
        #TODO: Load in particular zdab?
        #FIXME: Load in the processed root here?
        self.mac.write('/rat/inroot/load {}\n'.format(self.procroot))
        self.mac.write('\n')
        self.mac.write("/run/initialize\n\n")

        self.mac.write("### EVENT LOOP ###\n")
        self.mac.write("/rat/proc datacleaning\n")
        self.mac.write('/rat/procset mask "default"\n\n')
        for mask in self.masks:
            self.mac.write("/rat/proc/if dataCleaningCut\n")
            self.mac.write('/rat/procset flag "{}"\n'.format(mask))
            if self.getclean:
                self.mac.write('    /rat/proc outroot\n')
                self.mac.write('    /rat/procset file "{0}_{1}_clean.root"\n'.format(self.dcroot.rstrip('.root'),mask))
            if self.getdirty:
                self.mac.write("/rat/proc/else\n")
                self.mac.write('    /rat/proc outroot\n')
                self.mac.write('    /rat/procset file "{0}_{1}_dirty.root"\n'.format(self.dcroot.rstrip('.root'),mask))
            self.mac.write("/rat/proc/endif\n")

        self.mac.write("### END EVENT LOOP ###\n\n")

        self.mac.write("/rat/inroot/read\n\n")

        self.mac.write("exit")



class DCAProcMacro(Macro):
    def __init__(self,procroot, types, *args, **kwargs):
        super(DCAProcMacro, self).__init__(*args, **kwargs)
        self.types = types
        self.procroot = prpath + "/" + procroot
        self.dcroot = drpath + "/" + procroot
        self.write_main()
        
    def write_main(self):
        #TODO: Load in particular zdab?
        #FIXME: Load in the processed root here?
        self.mac.write('/rat/inroot/load {}\n'.format(self.procroot))
        self.mac.write('\n')
        self.mac.write("/run/initialize\n\n")

        self.mac.write("### EVENT LOOP ###\n")
        self.mac.write("/rat/proc count\n")
        self.mac.write("/rat/procset update 100\n\n")

        self.mac.write("/rat/proc dcaProc\n")
        for onetype in self.types:
            self.mac.write('/rat/procset type "{}"\n'.format(onetype))
        self.mac.write('/rat/proc outroot\n')
        self.mac.write('/rat/procset file "{}_dcaProc.root"\n'.format( \
                self.dccroot.rstrip(".root")))

        self.mac.write("### END EVENT LOOP ###\n\n")

        self.mac.write("/rat/inroot/read\n\n")

        self.mac.write("exit")

