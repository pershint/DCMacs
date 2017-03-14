#This will be the main script called to build the Data Cleaning Macros.

import sys
import os.path
import optparse
from subprocess import call
import lib.macwrite as m
import lib.batchwrite as b
import config.config as c
import glob

basepath = os.path.dirname(__file__)
homepath = os.path.abspath(os.path.join(basepath,""))
logpath = os.path.abspath(os.path.join(basepath,"log"))
rlpath = os.path.abspath(os.path.join(logpath,"ratlogs"))
ljpath = os.path.abspath(os.path.join(logpath,"json"))
prpath = m.prpath
zdabpath = m.zdpath


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
                "data cleaning and the dcaProc on")
(options,args) = parser.parse_args()

DEBUG = options.debug
zdabname = options.zdabname
runrange = options.runrange
procroot = options.procroot
#/PARSERUTILS


#FILENAMES
FIRSTPASS = "firstpass.mac"
PROCMAIN = "processing.mac"
DCSPLIT = "CleanData.mac"  #Outputs two roots per flag mask; one clean, one dirty
DCAPROC = "RunDCAProc.mac" #Outputs a root with various histograms describing DC

PROCBATCH_NAME = "ZDABProcessRunner.sh"
DCBATCH_NAME = "DCRATRunner.sh"
#Order is important here!  See ./templates/order.txt for reference
PROCMACRO_LIST = [FIRSTPASS, PROCMAIN]
DCMACRO_LIST = [DCSPLIT, DCAPROC]
#/FILENAMES

def procCleanUp():
    '''
    Moves files resulting from processing a zdab to their proper directory.
    ''' 
    roots = glob.glob(homepath + "/*.root")
    print(roots)
    for root in roots:
        call(["mv",root,prpath])
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
        zdablist = []
        for zdab in zdabpaths:
            zdablist.append(zdab.replace(zdabpath + "/",""))
        if DEBUG:
            print("LIST OF ZDABS CHOSEN TO PROCESS: \n")
            print(zdablist)
        return zdablist

def CleanRoot(rootfile):
        datacleaning = m.DCMacro(rootfile,c.masks,c.getdirty,DCSPLIT,c.MATERIAL)
        datacleaning.save()

        dcaproc = m.DCAProcMacro(rootfile,c.types,DCAPROC,c.MATERIAL)
        dcaproc.save()

        #Write your batchscript that runs the DC macros in order
        dcscript = b.BatchScript(DCBATCH_NAME,DCMACRO_LIST)
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
            dcaproc.delete()
            del dcaproc


def ProcessZdabs(zdablist):
    for zdabname in zdablist:
        if DEBUG:
            print("BUILDING MACROS FOR ZDAB {}...".format(zdabname))
        fp = m.FPMacro(zdabname,FIRSTPASS,c.MATERIAL)
        fp.save()

        proc = m.ProcMacro(zdabname,PROCMAIN,c.MATERIAL)
        processed_root = proc.get_procrootname()
        proc.save()

        datacleaning = m.DCMacro(processed_root,c.masks,c.getdirty,DCSPLIT,c.MATERIAL)
        datacleaning.save()

        dcaproc = m.DCAProcMacro(processed_root,c.types,DCAPROC,c.MATERIAL)
        dcaproc.save()
        if DEBUG:
            print("MACROS WRITTEN AND SAVED.")

        #Write your batchscript that runs all of these macros in order
        procscript = b.BatchScript(PROCBATCH_NAME,PROCMACRO_LIST)
        procscript.save()
        dcscript = b.BatchScript(DCBATCH_NAME,DCMACRO_LIST)
        dcscript.save()
        #Run the zdab -> ROOT processor
        try:
            procscript.run()
        except:
            print("something went wrong processing your zdabs.  noooooo")
            raise
        #Move your processed root to the ./data/proc_roots directory
        procCleanUp()
        #Run your Data Cleaning Scripts
        try:
            dcscript.run()
        except:
            print("something went wrong cleaning processed roots. noooo")
            raise

       

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
            dcaproc.delete()
            del dcaproc


if __name__ == '__main__':
    if procroot:
        CleanRoot(procroot)
    else:
        zdablist = getzdabnames()
        ProcessZdabs(zdablist)
    if DEBUG:
        print("MOVING RATLOGS")
    ratlogs = glob.glob(basepath + 'rat*log')
    for ratlog in ratlogs:
        call(["mv",ratlog,rlpath])


