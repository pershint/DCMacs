#Scripts written by: Teal Pershing
#March 13th, 2017

Usage help: $python main.py --help

These python scripts take raw zdabs from SNO+, process the data as done on the
SNO+ grid, and then split events based on the data cleaning mask chosen in 
main.py.  The final result is two .root files; one with a "clean" data set
(i.e. events did not have any of the data cleaning flags specified in config.py)
and a "dirty" data set (i.e. events had one or more of the data cleaning flags
specified in main.py).

./config/config.py is the home to all knobs the user would want to turn.  The 
mask used in the Data Cleaning step can be adjusted here.  The types of outputs
contained in the .root from running the dcaProc are adjusted using the "types"
mask. 

"masks" array in config.py usage:
For each mask, a "clean" and a "dirty" version of the processed root will be output.
Events in the clean output are not flagged with the input.  The dirty output 
have one or more or these flags. You can also put "default" as one of the masks; 
the clean output will have none of the flags in the default mask, the dirty events
 have one or more flag.  Lastly, you can also put an integer into the mask that
corresponds with a particular bitmask ("muontag", "ringoffire", and "qvtcut" would
be integer ).


When not in debug mode, macros that run the processing through RAT and the main
batch script are deleted after use.  In debug mode, the batch script will stay in
the ./batchscripts diretory and macros will stay in ./outmacs after running.

Dependencies:

  - Python
  - RAT (can be acquired from https://github.com/snoplus/rat)

TO PORT TO YOUR MACHINE:

 - In ./lib/batchwrite.py, the "ratpath" variable must be changed to point to the
machine's home rat directory relative to wherever DCmacs will live.
 - In ./lib/macwrite.py, the default zdab directory is ./zdabs.  If you
want to point to another directory you already have set up, you
must correct the directory path.

