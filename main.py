#This will be the main script called to build the Data Cleaning Macros.

import sys
import os.path
import optparse
from subprocess import call
import lib.macwrite as m
import lib.bashwrite as b
import config.config as c
import glob

basepath = os.path.dirname(__file__)
homepath = os.path.abspath(os.path.join(basepath,""))
logpath = os.path.abspath(os.path.join(basepath,"log"))
rlpath = os.path.abspath(os.path.join(logpath,"ratlogs"))
ljpath = os.path.abspath(os.path.join(logpath,"json"))
prpath = m.prpath
zdabpath = m.zdpath
drpath = m.drpath
RATSRC = c.RATSRC

#PARSERUTILS
parser = optparse.OptionParser()

parser.add_option("-d","--debug",action="store_true",dest="debug",
        default=False,
        help="Turn on debug mode")

parser.add_option("-z","--zdab",action="store",dest="zdabname",
        default=None,
        help="Input name of one particular zdab to process from ./zdabs")

parser.add_option("-r","--runrange",action="store",dest="runrange",
        default=None,
        help="Imput a run number range of zdabs to process from ./zdabs")
parser.add_option("-p","--procroot",action="store",dest="procroot",
        default=None,
        help="Give a name of a file in ./data/proc_roots to run ONLY" + \
                "data cleaning on")
parser.add_option("-P","--cleanall",action="store_true",dest="cleanall",
        default=False,
        help="Runs data cleaning on all of the processed roots in" + \
                "./data/proc_roots")
parser.add_option("-D","--delproc",action="store_true",dest="delproc",
	default=False,
	help="Permanently delete the processed root after splitting into" + \
		"clean and dirty DC rootfiles")
parser.add_option("-a","--dcaproc",action="store_true",dest="dcaproc",
        default=False,
        help="Also run dcaproc after each data cleaning macro is run")
parser.add_option("-O","--occupancy",action="store_true",dest="occupancy",
        default=True,
        help="Run the 'occupancy' configuration of the dcaproc after" + \
                "each data cleaning macro is run")
(options,args) = parser.parse_args()

DEBUG = options.debug
zdabname = options.zdabname
runrange = options.runrange
procroot = options.procroot
cleanall = options.cleanall
dcaproc = options.dcaproc
occupancy = options.occupancy
delproc=options.delproc
#/PARSERUTILS


#FILENAMES
FIRSTPASS = "firstpass.mac"
PROCMAIN = "processing.mac"
DCSPLIT = "CleanData.mac"  #Outputs two roots per flag mask; one clean, one dirty
DCAPROC = "RunDCAProc.mac" #Outputs a root with various histograms describing DC
OCCPROC = "RunOccProc.mac"

PROCBATCH_NAME = "ZDABProcessRunner.sh"
DCBATCH_NAME = "DCRATRunner.sh"
#/FILENAMES

#Types of histograms generated when the occupancy macro is run
occtypes = ["slot","crate","channel"]

#Order is important here!  See ./templates/order.txt for reference
PROCMACRO_LIST = [FIRSTPASS, PROCMAIN]
DCMACRO_LIST = [DCSPLIT]
if dcaproc:
    DCMACRO_LIST.append(DCAPROC)
if occupancy:
    DCMACRO_LIST.append(OCCPROC)


def procCleanUp():
    '''
    Moves files resulting from processing a zdab to their proper directory.
    ''' 
    jsons = glob.glob(homepath + "/*.json")
    for ajson in jsons:
        call(["mv",ajson,ljpath])

def getzdabnames():
    zdablist = []
    if zdabname and runrange:
        print("You must choose either one zdab or a run range, not both." + \
                "Please try defining your options again.\n")
        sys.exit(0)
    if zdabname:
        zdablist.append(options.zdabname)
	print("ZDAB CHOSEN TO PROCESS:" + str(zdablist))
    elif runrange:
        print("Not yet implemented.  Only YOU can implement this feature!")
        sys.exit(0)
        #FIXME: Use glob to get the desired filenames. example would be:
        #zdabnames = glob.glob(zdabpath + '/SNOP_0000' + RUNNUM + '*.zdab')
        #or something of the sort.
    else:
        print("No file specified.  Getting all zdabs from the zdabpath and" + \
                "trying to process them as requested.")
        zdabpaths = glob.glob(zdabpath + '/*.zdab')
        print(zdabpaths)
        for zdab in zdabpaths:
            zdablist.append(zdab.replace(zdabpath + "/",""))
        if DEBUG:
            print("LIST OF ZDABS CHOSEN TO PROCESS: \n")
            print(zdablist)
    return zdablist

def rootstoclean():
    rootlist = []
    if procroot:
        rootlist.append(procroot)
    else:
        procrootpaths = glob.glob(prpath + "/*.root")
        for pr in procrootpaths:
            pr = pr.replace(prpath + "/","")
            if pr.find("ntuple") == 1:
                continue
            else:
                rootlist.append(pr.replace(prpath + "/",""))
        if DEBUG:
            print("LIST OF ROOTS GOING TO CLEANING: \n")
            print(rootlist)
    return rootlist

def CleanRoots(rootlist):
    for rootfile in rootlist:
        datacleaning = m.DCMacro(rootfile,c.analysis_flags,c.cdget, \
                DCSPLIT,c.MATERIAL)
        datacleaning.save()

        if dcaproc:
            dcamacro = m.DCAProcMacro(rootfile,c.types,DCAPROC,c.MATERIAL)
            dcamacro.save()

        if occupancy:
            occmacro = m.DCAProcMacro(rootfile,occtypes,OCCPROC,c.MATERIAL)
            occmacro.save()

        #Write your bashscript that runs the DC macros in order
        dcscript = b.BashScript(DCBATCH_NAME,RATSRC,DCMACRO_LIST)
        dcscript.save()
        #Run the script written using bash
        try:
            dcscript.run()
        except:
            print("something went wrong running your script.  noooooo")
            raise
	if delproc:
	    #Remove the processed root now that cleaning is complete
            if DEBUG:
                print("DELETING PROCESSED ROOT FILE.")
            call(["rm",prpath + "/" + rootfile])
      

        #if not in debug mode, do cleanup
        if not DEBUG:
            dcscript.delete()
            del dcscript
            datacleaning.delete()
            del datacleaning
            if dcaproc:
                dcamacro.delete()
                del dcamacro
            if occupancy:
                occmacro.delete()
                del occmacro


def ProcessZdabs(zdablist):
    for zdabname in zdablist:
        if DEBUG:
            print("BUILDING MACROS FOR ZDAB {}...".format(zdabname))
        fp = m.FPMacro(zdabname,FIRSTPASS,c.MATERIAL)
        fp.save()

        proc = m.ProcMacro(zdabname,c.default_apply,PROCMAIN,c.MATERIAL)
        processed_root = proc.get_procrootname()
        proc.save()

        datacleaning = m.DCMacro(processed_root,c.analysis_flags, \
                c.cdget,DCSPLIT,c.MATERIAL)
        datacleaning.save()

        if dcaproc:
            dcamacro = m.DCAProcMacro(processed_root,c.types,DCAPROC,c.MATERIAL)
            dcamacro.save()
        if occupancy:
            occmacro = m.DCAProcMacro(processed_root,occtypes,OCCPROC,c.MATERIAL)
            occmacro.save()

        if DEBUG:
            print("MACROS WRITTEN AND SAVED.")

        #Write your bashscript that runs all of these macros in order
        procscript = b.BashScript(PROCBATCH_NAME,RATSRC,PROCMACRO_LIST)
        procscript.save()
        dcscript = b.BashScript(DCBATCH_NAME,RATSRC,DCMACRO_LIST)
        dcscript.save()
        #Run the zdab -> ROOT processor
        try:
            procscript.run()
        except:
            print("something went wrong processing your zdabs.  noooooo")
            raise
        #Move files produced during processing
        procCleanUp()

        #Run your Data Cleaning Scripts
        try:
            dcscript.run()
        except:
            print("something went wrong cleaning processed roots. noooo")
            raise
	if delproc:
            if DEBUG:
                print("REMOVING PROCESSED ROOT FILE.")
	    #Remove the processed root now that cleaning is complete
            call(["rm",prpath + "/" + processed_root])
       

        #if not in debug mode, do cleanup
        if not DEBUG:
            procscript.delete()
            del procscript
            dcscript.delete()
            del dcscript
            fp.delete()
            del fp
            proc.delete()
            del proc
            datacleaning.delete()
            del datacleaning
            if dcaproc:
                dcamacro.delete()
                del dcamacro
            if occupancy:
                occmacro.delete()
                del occmacro


if __name__ == '__main__':
    if procroot or cleanall:
        rlist = rootstoclean()
        CleanRoots(rlist)
    else:
        zdablist = getzdabnames()
        ProcessZdabs(zdablist)
    if DEBUG:
        print("MOVING RATLOGS")
    ratlogs = glob.glob(basepath + 'rat*log')
    for ratlog in ratlogs:
        call(["mv",ratlog,rlpath])


