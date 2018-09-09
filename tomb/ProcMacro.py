
#Class writes your Main processing loop
#FIXME: This isn't up to date with the third pass macro that would be used
#For analysis with SNO+ data!
class ProcMacro(Macro):
    def __init__(self,zdablist,defapply,procopts, *args, **kwargs):
        super(ProcMacro, self).__init__(*args, **kwargs)
        self.zdablist = zdablist
        self.defapply = defapply
        self.procopts = procopts

        self.fileinfo= self.zdablist[0].replace("SNOP_",
                "").replace(".zdab","").replace(".l2","")
        self.rootout = "DCMProcessed_"+self.fileinfo
        self.ntloc = prpath + "/" + self.rootout + "_ntuple.root"
        self.rootloc = prpath + "/" + self.rootout + ".root"
        self.write_main()
    
    def write_main(self):
        for zdab in self.zdablist:
            zdab = zdpath + "/" + zdab
            self.mac.write('/rat/inzdab/load {}\n'.format(zdab))
        self.mac.write('/rat/db/set DETECTOR geo_file "geo/snoplus_{}.geo"\n'.format(self.material))
        self.mac.write('\n')
        self.mac.write("/run/initialize\n\n")

        self.mac.write("### EVENT LOOP ###\n")
        self.mac.write("/rat/proc calibratePMT\n")
        self.mac.write("/rat/proc datacleaning\n")
        self.mac.write('/rat/procset mask "{}"\n'.format(self.defapply))
        self.mac.write('/rat/procset add "tpmuonfollowercut"\n')
        self.mac.write("/rat/procset pass 2\n")
        if self.procopts["fullprocess"]:
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
        if self.procopts["ntuple"]:
            self.mac.write('/rat/proc outntuple\n')
            self.mac.write('/rat/procset file "{}"\n'.format(self.ntloc))
        self.mac.write('/rat/proclast outroot\n')
        self.mac.write('/rat/procset file "{}"\n'.format(self.rootloc))
        self.mac.write("### END EVENT LOOP ###\n\n")

        self.mac.write("/rat/inzdab/read\n")
        self.mac.write("exit")

    def get_procrootname(self):
        return self.rootloc.replace(prpath + "/","")
    

