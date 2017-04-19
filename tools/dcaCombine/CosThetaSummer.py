#This tool takes all files in the /occ directory and outputs the
#hits in the range 0.8 < cos(theta) <1.0 for events with nhit >60.
import ROOT as r
import os.path
import numpy as np
import sys

import copy
import argparse
import glob

basepath = os.path.dirname(__file__)


Nh60CosT = "Nhit_60Cos_Theta"


#Degrees in theta, spherical coordinates you want to sum
binstosum = {"Top60": [6,10], "Top36": [0,6]}

def getczparams(hfilenames,histtitles):
    '''
    Takes a rootfile filled with dca/occ histograms and returns
    a dictionary with the run_subrun as key and the sum of cos(theta)
    from 0.8-1.0 for events w/ Nhit > 60 as the value.
    '''
    cosTdict60 = {}
    cosTdict36 = {}
    for hfilename in hfilenames:
        namesplit = hfilename.split("_")
        runnum = namesplit[1] + "_" + namesplit[2]
        _file0 = r.TFile.Open(hfilename)
        for title in histtitles:
            hist = copy.deepcopy(_file0.Get(title))
            try:
                hist.GetSum()
            except AttributeError:
                print("Error getting histogram for " + title + \
                        "in file " + hfilename + ". Cancelling")
                sys.exit(0)
            numbins = hist.GetNbinsX()
            tothits = hist.GetSum()
            if tothits == 0:
                cosTdict60[runnum] = 0
                cosTdict36[runnum] = 0
                continue
            for region in binstosum:
                neededbins = np.arange(binstosum[region][0],binstosum[region][1],1)
                print(neededbins)
                highhits = 0.0
                for c in neededbins:
                    binhits = hist.GetBinContent(numbins - c)
                    highhits+=binhits
                if region == "Top36":
                    cosTdict36[runnum] = highhits / tothits
                elif region == "Top60":
                    cosTdict60[runnum] = highhits / tothits
    return cosTdict60, cosTdict36

if __name__ == "__main__":
    #rootfile = r.TFile("occProcHists_Combined.root","RECREATE")
    histtitles = ["Nhit_60Cos_Theta"]
    c60, c36 = getczparams(histfiles,histtitles)

