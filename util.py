import os, time, subprocess, io, sys, re, argparse
import numpy as np

py_version = sys.version.split('.')[0]
if py_version == '2':
	open = io.open
else:
	unicode = str

def makedirs(fld):
	if not os.path.exists(fld):
		makedirs(fld)