#live the dream
import ROOT as r
import os.path
import numpy as np
import sys

import copy
import argparse
import glob

basepath = os.path.dirname(__file__)
dcapath = os.path.abspath(os.path.join(basepath,"dcas"))
occpath = os.path.abspath(os.path.join(basepath,"occs"))

parser = argparse.ArgumentParser()

parser.add_argument('-a','--dcafiles', action='store_true',dest='isdca', \
        default=False,help='Set if you are parsing all dcaProc type roots')
parser.add_argument('-O','--occfiles', action='store_true',dest='isocc',
        default=False,help='Set if you are parsing all occProc type roots')

args = parser.parse_args()

crates = list(np.arange(0,19,1))
crates.append("All")
nhittypes = {"Nhit": [10,20,40,60]}
occtypes = {"Crate": crates,"Angle":["Cos_Theta","Phi"],"%Angle":["Cos","Phi"]}

def getOccHistNames():
    histnames = []
    for thresh in nhittypes["Nhit"]:
        namebase = "Nhit_" + str(thresh)
        #Build crate space names
        for cnum in occtypes["Crate"]:
            if cnum != "All":
                histnames.append(namebase+",Crate_"+str(cnum))
            else:
                histnames.append(namebase+",All_Crate")
        #Electronic space hist name
        histnames.append(namebase+"Electronic_Space")
        #Angle types in occProc
        for ang in occtypes["Angle"]:
            histnames.append(namebase+ang)
        for pang in occtypes["%Angle"]:
            histnames.append(namebase+"Percent_"+pang)
    return histnames

def sumhists(hfilenames,histtitles):
    '''
    Takes a rootfile filled with dca/occ histograms and returns
    an array with all of the histogram objects.
    '''
    sumhists = []
    for hfilename in hfilenames:
        _file0 = r.TFile.Open(hfilename)
        if not sumhists:
            for title in histtitles:
                hist = copy.deepcopy(_file0.Get(title))
                try:
                    hist.GetSum()
                except AttributeError:
                    print("Error getting histogram for " + title + \
                            "in file " + hfilename + ". Cancelling")
                    sys.exit(0)
                sumhists.append(hist)
            continue
        else:
            for j,title in enumerate(histtitles):
                hist = copy.deepcopy(_file0.Get(title))
                try:
                    sumhists[j].Add(sumhists[j],hist,1.0,1.0)
                except AttributeError:
                    print("Error getting histogram for " + title + \
                            "in file " + hfilename + ". Stopping")
                    sys.exit(0)
    return sumhists

def writeHistsToTFile(histarr):
    outfile = r.TFile("occProcHists_Combined.root","RECREATE")
    for hist in histarr:
        outfile.Add(hist)
    #FIXME: Add a tree here that has all of the
    #Run_subrun numbers used to make the result
    return outfile

if __name__ == "__main__":
    print(args.isdca)
    print(args.isocc)
    print("LET US BEGIN")
    if args.isdca:
        histfiles = glob.glob(dcapath + "/*dcaProc*")
    if args.isocc:
        histfiles = glob.glob(occpath + "/*occProc*")
        #Build histsums using first occ
    print("FILES THAT WILL BE COMBINED: " + str(histfiles))
    output=getOccHistNames()
    print("SUMMING HISTOGRAMS FOR RUNS NOW...")
    sumhists = sumhists(histfiles,output)
    #FIXME: Make a function that changes all of the titles!
    #Could use GetSum() to add # entries for each histogram in
    sumhists[0].GetSum()
    sumhists[0].Draw()
    rootfile = writeHistsToTFile(sumhists)
    rootfile.Save()
