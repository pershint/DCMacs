#Scripts written by: Teal Pershing
#Last updated: October 28th, 2018

Usage help: $python main.py --help


#QUICK START

Let's say you want to run data cleaning on some zdabs you have, and split them
into "dirty" and "clean" datasets.  Do the following.

i) Move all of the zdabs of interest to the directory ./data/zdabs .

ii) open ./config/config.py . Set your configurables as desired; each is
commented with a description, so read them to see what you can toggle.


ii) To process all zdabs and apply data cleaning for a run range of interest (let's say 200000 to 2000010), do:

$ python main.py -R 200000-200010

Each run will be processed, and saved into a file in ./data/proc_roots.

iii) If you want to split all the files in ./data/proc_roots 
into dirty and clean files based on the
analysis\_type specified in ./config/config.py, do:

$ python main.py -P

Each run will be scanned over and saved into a \_dirty.root and a \_clean.root in
./data/datacleaned_roots

iv) If you want to run the dcaProc on the file MyFileToProcess.root located
 in ./data/proc_roots, do

$ python --dcaproc -u MyFileToProcess.root

If you want to run the occProc, similarly do

$ python --occproc -u MyFileToProcess.root




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

"analysis_flags" array in config.py usage:
For each mask, a "clean" and a "dirty" version of the processed root will be output.
Events in the clean output are not flagged with the input.  The dirty output 
have one or more or these flags. You can also put one of the masks defined in
/data/DATACLEANING.ratdb (i.e. "muon_study","flasher_study","analysis_mask", etc.)
 as one of the masks; clean output will have none of the flags
 in the default mask, the dirty events have one or more of the flags in the mask.
 Lastly, you can also put an integer into the mask that
corresponds with a particular bitmask ("muontag", "ringoffire", and "qvtcut" would
be integer ).


When not in debug mode, macros that run the processing through RAT and the main
bash script are deleted after use.  In debug mode, the bash script will stay in
the ./bashscripts diretory and macros will stay in ./outmacs after running.

Dependencies:

  - Python
  - RAT (can be acquired from https://github.com/snoplus/rat)

TO PORT TO YOUR MACHINE:

 - In config/config.py, the "RATSRC" variable must be changed to point to the
machine's home rat directory relative to wherever DCmacs will live.
 - In ./lib/macwrite.py, the default zdab directory is ./zdabs.  If you
want to point to another directory you already have set up, you
must correct the directory path.

