#!/pkg/python/3.7.4/bin/python3
from all_helpers import *
import sys

gtag = sys.argv[1]
algo = sys.argv[2]
p, _ = run_blant(gtag, alph=True, algo=algo, lDEG=2, overwrite=False)

if p != None:
    p.wait()
