#This will be the main script called to build the Data Cleaning Macros.

import sys
import os.path
import numpy as np
from subprocess import call
import lib.macwrite as m
import lib.bashwrite as b
import config.config as c
import glob

import lib.argparser as p

basepath = os.path.dirname(__file__)
homepath = os.path.abspath(os.path.join(basepath,""))
logpath = os.path.abspath(os.path.join(basepath,"data","runlogs"))
miscratpath = os.path.abspath(os.path.join(logpath,"miscRATruns"))
ljpath = os.path.abspath(os.path.join(logpath,"json"))
prpath = m.prpath
zdabpath = m.zdpath
drpath = m.drpath

#LOAD CONFIG
RATSRC = c.RATSRC
dcopts = {"getclean":c.getclean,"getdirty":c.getdirty}
procopts = {"fullprocess":c.fullprocess, "ntuple":c.procntuple}
#/LOAD CONFIG


zdabname = p.zdabname
run = p.run
RUNRANGE = p.runrange
zdabopts = [run,RUNRANGE,zdabname]
procroot = p.procroot
cleanall = p.cleanall
dcaproc = p.dcaproc
occupancy = p.occupancy
delproc=p.delproc
jobnum=p.jobnum
aoc = p.actonclean
dcaocc1 = p.dcaocc
ISSLURM = p.isslurm
#/PARSERUTILS


#FILENAMES
FIRSTPASS = "firstpass_"+str(jobnum)+".mac"
PROCMAIN = "processing_"+str(jobnum)+".mac"
DCSPLIT = "CleanData_"+str(jobnum)+".mac"  #Outputs two roots per flag mask; one clean, one dirty
DCAPROC = "RunDCAProc_"+str(jobnum)+".mac" #Outputs a root with various histograms describing DC
OCCPROC = "RunOccProc_"+str(jobnum)+".mac"

PROCBATCH_NAME = "ZDABProcessRunner_"+str(jobnum)+".sh"
DCBATCH_NAME = "DCRATRunner_"+str(jobnum)+".sh"
DCABATCH_NAME = "dcaOccProcRunner_"+str(jobnum)+".sh"
#/FILENAMES


#Order is important here!  See ./templates/order.txt for reference
PROCMACRO_LIST = [FIRSTPASS, PROCMAIN]
DCMACRO_LIST = [DCSPLIT]
DCAMACRO_LIST = []
if dcaproc:
    DCAMACRO_LIST.append(DCAPROC)
if occupancy:
    DCAMACRO_LIST.append(OCCPROC)


def DoDCA(rf,subrun):
    '''
    Run the dcaProc or occproc on the input rootfile.
    If subrun is none, RAT is run from the home path.  Otherwise,
    ratlogs go to /data/runlogs/RUN_SUBRUN
    '''
    if dcaproc:
        dcamacro = m.DCAProcMacro(rf,c.types,DCAPROC,c.MATERIAL)
        dcamacro.save()
    if occupancy:
        occmacro = m.OccProcMacro(rf,OCCPROC,c.MATERIAL)
        occmacro.save()
    #Write your bashscript that runs the DC macros in order
    dcascript = b.BashScript(RATSRC,macro_list=DCAMACRO_LIST,runinfo=subrun,slurmjob=ISSLURM)
    dcascript.ScriptName(DCABATCH_NAME)
    dcascript.Set_ScriptPath(brpath)
    dcascript.write()
    dcascript.save()
    #Run the script written using bash
    try:
        dcascript.run()
    except:
        print("something went wrong running your script.  noooooo")
        raise
    #if not in debug mode, do cleanup
    if not DEBUG:
        if dcaproc:
	    dcamacro.delete()
	    del dcamacro
        if occupancy:
	    occmacro.delete()
	    del occmacro


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

#Return a dictionary of zdabs from ./data/zdab/
def getzdabdict():
    zdablist = []
    if zdabopts.count(None) < (len(zdabopts)-1):
        print("You must choose all zdabs, one zdab, one run, or a run range." + \
                "Please try defining your options again.\n")
        sys.exit(0)
    if zdabname: #Only get one zdab
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
    rundict = zdabsbyrun(zdablist) #Get only the runs in your run range
    if rundict == {}:
        print("No zdabs met the specified run/name information.  Exiting")
        sys.exit(0)
    return rundict

#Returns a list of root files from ./data/proc_roots to run data cleaning on
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
                rootlist.append(pr)
        if DEBUG:
            print("LIST OF ROOTS GOING TO CLEANING: \n")
            print(rootlist)
    return rootlist

#Given a list of rootfiles, write out the data cleaning scripts to
#Split the files to clean and dirty subfiles, then runs the macs
def CleanRoots(rootlist):
    for rootfile in rootlist:
        datacleaning = m.DCMacro(rootfile,c.analysis_type,dcopts, \
                DCSPLIT,c.MATERIAL)
        datacleaning.save()

        #Write your bashscript that runs the DC macros in order
        dcscript = b.BashScript(RATSRC,macro_list=DCMACRO_LIST,None,slurmjob=ISSLURM)
        dcscript.ScriptName(DCBATCH_NAME)
        dcscript.Set_ScriptPath(brpath)
        dcscript.write()
        dcscript.save()
        #Run the script written using bash
        try:
            dcscript.run()
        except:
            print("something went wrong running your script.  noooooo")
            raise
      

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
        
        #Generate dca/occ macros and run if input
        if occproc or occupancy:
            DoDCA(rootfile,None)
        #Remove processed root if was requested in flags
	if delproc:
	    #Remove the processed root now that cleaning is complete
            if DEBUG:
                print("DELETING PROCESSED ROOT FILE.")
            call(["rm",prpath + "/" + rootfile])

#FIXME:The processing macros are not the same as on the grid right now
def ProcessZdabs(zdabdict,outtype="ntuple"):
    for subrun in zdabdict:
        if DEBUG:
            print("BUILDING MACROS FOR ZDABS {}...".format(zdabdict[subrun]))
        fp = m.FPMacro(zdabdict[subrun],FIRSTPASS,c.MATERIAL)
        fp.save()

        sp = m.SPMacro(zdabdict[subrun],c.default_apply,procopts,PROCMAIN,c.MATERIAL)
        sp.setOutputType(outtype)
        processed_root = proc.get_procrootname()
        proc.save()

        datacleaning = m.DCMacro(processed_root,c.analysis_type, \
                dcopts,DCSPLIT,c.MATERIAL)
        datacleaning.save()
        if DEBUG:
            print("ZDAB PROCESSING AND DATACLEANING MACROS WRITTEN AND SAVED.")

        #Write your bashscript that runs processing
        procscript = b.BashScript(RATSRC,macro_list=PROCMACRO_LIST,runinfo=subrun,slurmjob=ISSLURM)
        procscript.ScriptName(PROCBATCH_NAME)
        procscript.Set_ScriptPath(brpath)
        procscript.write()
        procscript.save()
        #Write your bashscript that runs data cleaning
        dcscript = b.BashScript(RATSRC,macro_list=DCMACRO_LIST,runinfo=subrun,slurmjob=ISSLURM)
        dcscript.ScriptName(DCBATCH_NAME)
        dcscript.Set_ScriptPath(brpath)
        dcscript.write()
        dcscript.save()
        #Run the zdab -> ROOT processor
        try:
            procscript.run()
        except:
            print("something went wrong processing your zdabs.  noooooo")
            raise

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

        #Generate macros & run for dcaProcs
        if occupancy or dcaproc:
            DoDCA(processed_root,subrun)
	if delproc:
            if DEBUG:
                print("REMOVING PROCESSED ROOT FILE.")
	    #Remove the processed root now that cleaning is complete
            call(["rm",prpath + "/" + processed_root])

def dcaonclean():
    cleanfiles = glob.glob(drpath + "/*clean*.root")
    rootlist = []
    for cf in cleanfiles:
        cname = cf.replace(dcpath + "/","")
        if cname.find("ntuple") == 1:
	    continue
        else:
	    rootlist.append(cname)
    for rf in rootlist:
        DoDCA(rf,None)


if __name__ == '__main__':
    if dcaocc1:
        rf = dcaocc1
        DoDCA(rf,None)
    elif aoc:
        dcaonclean()
    elif procroot or cleanall:
        rlist = rootstoclean()
        CleanRoots(rlist)
    else:
        zdabdict = getzdabdict()
        ProcessZdabs(zdabdict)
    if DEBUG:
        print("MOVING RATLOGS")
    ratlogs = glob.glob(basepath + 'rat*log')
    for ratlog in ratlogs:
        call(["mv",ratlog,miscratpath])


