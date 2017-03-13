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
logpath = os.path.abspath(os.path.join(basepath,"log"))
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
(options,args) = parser.parse_args()

DEBUG = options.debug
zdabname = options.zdabname
runrange = options.runrange
#/PARSERUTILS


#FILENAMES
FIRSTPASS = "firstpass.mac"
PROCMAIN = "processing.mac"
DCSPLIT = "CleanData.mac"  #Outputs two roots per flag mask; one clean, one dirty
DCAPROC = "RunDCAProc.mac" #Outputs a root with various histograms describing DC

BATCH_NAME = "BatchRunner.sh"
#Order is important here!  See ./templates/order.txt for reference
MACRO_LIST = [FIRSTPASS, PROCMAIN, DCSPLIT, DCAPROC]
#/FILENAMES


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
        zdablist = []
        for zdab in zdabpaths:
            zdablist.append(zdab.lstrip(zdabpath + "/"))
        if DEBUG:
            print("LIST OF ZDABS CHOSEN TO PROCESS: \n")
            print(zdablist)
        return zdablist

if __name__ == '__main__':
    zdablist = getzdabnames()
    for zdabname in zdablist:
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

        #Write your batchscript that runs all of these macros in order
        script = b.BatchScript(BATCH_NAME,MACRO_LIST)
        script.save()
        #Run the script written using bash
        try:
            script.run()
        except:
            print("something went wrong running your script.  noooooo")
            raise
       

        #if not in debug mode, do cleanup
        if not DEBUG:
            script.delete()
            del script
            fp.delete()
            del fp
            proc.delete()
            del proc
            datacleaning.delete()
            del datacleaning
            dcaproc.delete()
            del dcaproc

    print("MOVING RATLOGS")
    ratlogs = glob.glob(basepath + 'rat*log')
    for ratlog in ratlogs:
        call(["mv",ratlog,logpath])


