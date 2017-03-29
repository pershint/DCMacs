#This will be the main script called to build the Data Cleaning Macros.

import sys
import os.path
import numpy as np
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

#LOAD CONFIG
RATSRC = c.RATSRC
dcopts = {"getclean":c.getclean,"getdirty":c.getdirty}
procopts = {"fullprocess":c.fullprocess, "ntuple":c.procntuple}
#/LOAD CONFIG

#PARSERUTILS
parser = optparse.OptionParser()

parser.add_option("-d","--debug",action="store_true",dest="debug",
        default=False,
        help="Turn on debug mode")

parser.add_option("-z","--zdab",action="store",dest="zdabname",
        default=None,
        help="Input name of one particular zdab to process from ./zdabs")

parser.add_option("-r","--run",action="store",dest="run",
        default=None,
        help="Input a run number to process zdabs in ./zdabs for that run")
parser.add_option("-R","--runrange",action="store",dest="runrange",
        default=None,
        help="Input a run range to process zdabs in ./zdabs for each run in" + \
                "range. Input as min-max (inclusive)")
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
        default=False,
        help="Run the 'occupancy' configuration of the dcaproc after" + \
                "each data cleaning macro is run")
parser.add_option("-j","--jobnum",action="store",dest="jobnum",
        default=0, help="Job number appended to macro names and bashscript" + \
                "names")
(options,args) = parser.parse_args()

DEBUG = options.debug

zdabname = options.zdabname
run = options.run
RUNRANGE = options.runrange
zdabopts = [run,RUNRANGE,zdabname]

procroot = options.procroot
cleanall = options.cleanall
dcaproc = options.dcaproc
occupancy = options.occupancy
delproc=options.delproc
jobnum=options.jobnum
#/PARSERUTILS


#FILENAMES
FIRSTPASS = "firstpass_"+str(jobnum)+".mac"
PROCMAIN = "processing_"+str(jobnum)+".mac"
DCSPLIT = "CleanData_"+str(jobnum)+".mac"  #Outputs two roots per flag mask; one clean, one dirty
DCAPROC = "RunDCAProc_"+str(jobnum)+".mac" #Outputs a root with various histograms describing DC
OCCPROC = "RunOccProc_"+str(jobnum)+".mac"

PROCBATCH_NAME = "ZDABProcessRunner_"+str(jobnum)+".sh"
DCBATCH_NAME = "DCRATRunner_"+str(jobnum)+".sh"
#/FILENAMES


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


def zdabsbyrun(zdablist):
    '''
    Takes a zdab list and groups the zdabs into arrays that have all
    zdabs associated with a run in them.
    '''
    rundict = {}
    for zdab in zdablist:
        fileinfo = zdab.replace("SNOP_","").replace(".zdab","").replace(".l2","")
        runnum = fileinfo.split("_")[0].lstrip("0")
        if DEBUG:
            print("GOT ZDAB WITH RUN NUMBER: " + str(runnum))
        if run:
            if int(run) == int(runnum):
                rundict[fileinfo] = []
                rundict[fileinfo].append(zdab)
            break
        if RUNRANGE:
            runrange = RUNRANGE.split("-")
            lowrun = int(runrange[0])
            highrun = int(runrange[1])
            zdabrange = np.arange(lowrun,highrun,1)
            if int(runnum) not in zdabrange:
                continue
        while True:
            try:
                rundict[fileinfo].append(zdab)
            except KeyError:
                rundict[fileinfo] = []
                continue
            break
    if DEBUG:
        print("PROCESSING ZDABS FOR THE FOLLOWING RUNS: \n")
        print(rundict)
    if rundict == {}:
        print("No run range or run exists in /zdabs that was requested." + \
                "Try another run range.  Exiting")
        sys.exit(0)
    return rundict


def getzdabdict():
    zdablist = []
    if zdabopts.count(None) < (len(zdabopts)-1):
        print("You must choose all zdabs, one zdab, one run, or a run range." + \
                "Please try defining your options again.\n")
        sys.exit(0)
    if zdabname:
        zdablist.append(options.zdabname)
	print("ZDAB CHOSEN TO PROCESS:" + str(zdablist))
    else:
        if RUNRANGE:
            print("Getting zdabs from input run range")
        else:
            print("Getting all zdabs in ./zdabs to process")
        zdabpaths = glob.glob(zdabpath + '/*.zdab')
        for zdab in zdabpaths:
            zdablist.append(zdab.replace(zdabpath + "/",""))
    rundict = zdabsbyrun(zdablist)
    if rundict == {}:
        print("No zdabs met the specified run/name information.  Exiting")
        sys.exit(0)
    return rundict

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
        datacleaning = m.DCMacro(rootfile,c.analysis_type,dcopts, \
                DCSPLIT,c.MATERIAL)
        datacleaning.save()

        if dcaproc:
            dcamacro = m.DCAProcMacro(rootfile,c.types,DCAPROC,c.MATERIAL)
            dcamacro.save()

        if occupancy:
            occmacro = m.OccProcMacro(rootfile,OCCPROC,c.MATERIAL)
            occmacro.save()

        #Write your bashscript that runs the DC macros in order
        dcscript = b.BashScript(DCBATCH_NAME,RATSRC,DCMACRO_LIST,None)
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


def ProcessZdabs(zdabdict):
    for subrun in zdabdict:
        if DEBUG:
            print("BUILDING MACROS FOR ZDABS {}...".format(zdabdict[subrun]))
        fp = m.FPMacro(zdabdict[subrun],FIRSTPASS,c.MATERIAL)
        fp.save()

        proc = m.ProcMacro(zdabdict[subrun],c.default_apply,procopts,PROCMAIN,c.MATERIAL)
        processed_root = proc.get_procrootname()
        proc.save()

        datacleaning = m.DCMacro(processed_root,c.analysis_type, \
                dcopts,DCSPLIT,c.MATERIAL)
        datacleaning.save()

        if dcaproc:
            dcamacro = m.DCAProcMacro(processed_root,c.types,DCAPROC,c.MATERIAL)
            dcamacro.save()
        if occupancy:
            occmacro = m.OccProcMacro(processed_root,OCCPROC,c.MATERIAL)
            occmacro.save()

        if DEBUG:
            print("MACROS WRITTEN AND SAVED.")

        #Write your bashscript that runs processing
        procscript = b.BashScript(PROCBATCH_NAME,RATSRC,PROCMACRO_LIST,subrun)
        procscript.save()
        #Write your bashscript that runs data cleaning
        dcscript = b.BashScript(DCBATCH_NAME,RATSRC,DCMACRO_LIST,subrun)
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
        zdabdict = getzdabdict()
        ProcessZdabs(zdabdict)
    if DEBUG:
        print("MOVING RATLOGS")
    ratlogs = glob.glob(basepath + 'rat*log')
    for ratlog in ratlogs:
        call(["mv",ratlog,rlpath])


