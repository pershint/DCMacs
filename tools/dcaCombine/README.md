#This tool is intended to be used with files output from running SNOrat's
#dcaProc on SNO+ processed data.  Files named "dcaProcHists" output from
#DCMacs are the RAT dcaProc using the "flagged" and "timediff" types.
#Files named "occProcHists" output from DCMacs are the RAT dcaProc using
#the "slot","crate", and "channel" types.  

#Usage of this tool:

TO COMBINE DCAPROC OUTPUTS:
  1. Put all of your dcaProcHists.root files into ./dcas you wish to
     combine.
  2. at terminal: python dcaCombine.py -a
  3. Your combined output should be in ./output

TO COMBINE OCCPROC OUTPUTS:
  1. Put all of your occProcHists.root files into ./occs you wish to
     combine.
  2. at terminal: python dcaCombine.py -O
  3. Your combined output should be in .output

Note that this tool expects file names of the type (either occ or dca):

DCMProcessed_RUNNUMBER_SUBRUN_occProcHists.root

RUNNUMBER: ten digit run number.  EX: "run 1033" would be 0000001033
SUBRUN: three digit run subfile number.

#If you want to change this, you'll have to adjust the logic used in
#dcaCombine.py that adds the "run and subrun" record included with the
#outputted root.
