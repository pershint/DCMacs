import argparse 

#PARSERUTILS
parser = argparse.ArgumentParser(description="Parser for Data Cleaning "+\
        "macro generator and runner")

parser.add_argument("-d","--debug",action="store_true",dest="debug",
        default=False,
        help="Turn on debug mode")
parser.add_argument("-g","--generate_tables",action="store_true",dest="generate_tables",
        default=False,
        help="If this flag is given, the first pass of data cleaning (which "+\
                "generates the RATDB data cleaning tables) will be run.")
parser.add_argument("-z","--zdab",action="store",dest="zdabname",
        default=None,
        help="Input name of one particular zdab to process from ./zdabs")

parser.add_argument("-r","--run",action="store",dest="run",
        default=None,
        help="Input a run number to process zdabs in ./zdabs for that run")
parser.add_argument("-R","--runrange",action="store",dest="runrange",
        default=None,
        help="Input a run range to process zdabs in ./zdabs for each run in" + \
                "range. Input as min-max (inclusive)")
parser.add_argument("-p","--procroot",action="store",dest="procroot",
        default=None,
        help="Give a name of a file in ./data/proc_roots to run ONLY" + \
                "data cleaning on")
parser.add_argument("-P","--cleanall",action="store_true",dest="cleanall",
        default=False,
        help="Runs data cleaning on all of the processed roots in" + \
                "./data/proc_roots")
parser.add_argument("-D","--delproc",action="store_true",dest="delproc",
	default=False,
	help="Permanently delete the processed root after splitting into" + \
		"clean and dirty DC rootfiles")
parser.add_argument("-a","--dcaproc",action="store_true",dest="dcaproc",
        default=False,
        help="Run dcaproc (runs on all outputs from zdab processing, or a" + \
                 "single file fed in with the -u flag")
parser.add_argument("-O","--occupancy",action="store_true",dest="occupancy",
        default=False,
        help="Run the 'occupancy' configuration of the dcaproc after" + \
                "each data cleaning macro is run")
parser.add_argument("-u","--dcaocc",action="store",dest="dcaocc",
        default=None,
        help="If the -a or -O flag is activated, only run the dcaProc on" + \
		"the filename given located in /data/proc_roots")
parser.add_argument("-C","--actonclean",action="store_true",dest="actonclean",
        default=False,
        help="If the -a or -O flag is activated, only run the dcaProc on" + \
		"files in /data/proc_roots with clean in the filename")
parser.add_argument("-s","--slurm",action="store_true",dest="isslurm",
        default=False, help="Give flag if submitting jobs on slurm.  Will add"+\
                "the necessary headers to bash scripts generated")
parser.add_argument("-j","--jobnum",action="store",dest="jobnum",
        default=0, help="Job number appended to macro names and bashscript" + \
                "names")
args = parser.parse_args()


DEBUG = args.debug

generate_tables = args.generate_tables
zdabname = args.zdabname
run = args.run
runrange = args.runrange
procroot = args.procroot
cleanall = args.cleanall
dcaproc = args.dcaproc
occupancy = args.occupancy
delproc=args.delproc
jobnum=args.jobnum
actonclean = args.actonclean
dcaocc = args.dcaocc
isslurm = args.isslurm
#/PARSERUTILS

