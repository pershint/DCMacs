#Live the dream
import ROOT as r
import numpy as np

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-a','--dcafiles', action='store_true',dest='isdca', \
        default=False,help='Set if you are parsing all dcaProc type roots')
parser.add_argument('-O','--occfiles', action='store_true',dest='isocc',
        default=False,help='Set if you are parsing all occProc type roots')

args = parser.parse_args()


if __name__ == "__main__":
    print(args.isdca)
    print(args.isocc)
    print("LET US BEGIN")
