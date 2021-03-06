#===========================================================================================================================================================================
#Module description
#===========================================================================================================================================================================

"""Module for QuantDorsal for interacting with ilastik.

Contains functions for 

	* Launching ilastik.
	* Path management.
	* h5 I/O.
	
"""

#===========================================================================================================================================================================
#Importing necessary modules
#===========================================================================================================================================================================

#Numpy/Scipy
import numpy as np

#System
import sys
import inspect
import os

#Matplotlib
import matplotlib.pyplot as plt

#QuantDorsal
from term_module import *

#===========================================================================================================================================================================
#Module Functions
#===========================================================================================================================================================================

def runIlastik(files,fnOut=None,classFile="classifiers/quantDorsalDefault.ilp",channel=0,exportImg=False):
	
	"""Runs ilastik on all files in specified in files.
	
	Calls ilastik in headless mode using ``os.system``.
	
	Args:
		files (str): List of files to run ilastik on.
		
	Keyword Args:
		classFile (str): Path to classifier file.
		channel (int): Which channel to mask.
		exportImg (bool): Export prediction images.
		fnOut (str): Output filepath
		
	Returns:
		list: List of paths to output files.
		
	"""
	
	#Get ilastik binary
	ilastikPath=getIlastikBin()
	
	outFiles=[]
	
	for fn in files:
	
		#Build input data string
		regExData=" " + fn + " " 
		
		#Build basic command
		cmd = ilastikPath + " --headless" + " --project=" +classFile 
		
		#Some extra options for output
		if exportImg:
			cmd = cmd + " --export_object_prediction_img --export_object_probability_img  "
		
		if fnOut!=None:
			cmd = cmd + " --output_internal_path " + fnOut
		else:
			fnOut=fn
		
		outFiles.append(fnOut)
		
		#Add input data to command string
		cmd=cmd+" " + regExData
		
		#Print what we are about to do
		printNote("About to execute:")
		print cmd
		
		#Run command
		ret=os.system(cmd)
	
	return outFiles
	
def getConfDir():
	
	"""Returns path to configurations directory."""
	
	modulePath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	path=modulePath+"/configurations"+"/"
	return path

def getPathFile():
	
	"""Returns path to paths file."""
	
	return getConfDir()+'paths'

def getIlastikBin(fnPath=None):
	
	"""Returns path to ilastik binary."""
	
	return getPath('ilastikBin',fnPath=fnPath)


def getPath(identifier,fnPath=None):
	
	"""Extracts path with identifier from path definition file.
	
	If not defined diferently, will first look in configurations/paths,
	then configurations/paths.default.
	
	Args:
		identifier (str): Identifier of path
		
	Keyword Args:
		fnPath (str): Path to path definition file
			
	Returns:
		str: Path

	"""
	
	if fnPath==None:
		fnPath=getPathFile()
	else:
		if not os.path.isfile(fnPath):
			printWarning(fnPath+" does not exist. Will continue with paths defined in default paths files.")
			fnPath=getPathFile()
		
	path=None
	
	with  open (fnPath,'rb') as f:
		for line in f:
			if line.strip().startswith(identifier):
				ident,path=line.split('=')
				path=path.strip()
				break
		
	if path==None:
		printWarning("There is no line starting with ", identifier+"= in ", fnPath, ".")
		fnPath=getPathFile()+'.default'
		path=getPath(identifier,fnPath=fnPath)
		
	path=os.path.expanduser(path)
	
	return path

def getCenterOfMass(x,y,masses=None):
	
	r"""Computes center of mass of a given set of points.
	
	.. note:: If ``masses==None``, then all points are assigned :math:`m_i=1`.
	
	Center of mass is computed by:
	
	.. math:: C=\frac{1}{M}\sum\limits_i m_i (x_i,y_i)^T
	
	where 
	
	.. math:: M = \sum\limits_i m_i
	
	Args:
		x (numpy.ndarray): x-coordinates.
		y (numpy.ndarray): y-coordinates.
		
	Keyword Args:
		masses (numpy.ndarray): List of masses.
	
	Returns:
		numpy.ndarray: Center of mass.
	
	"""
	
	if masses==None:
		masses=np.ones(x.shape)
		
	centerOfMassX=1/(sum(massses))*sum(masses*x)
	centerOfMassY=1/(sum(massses))*sum(masses*y)
	
	centerOfMass=np.array([centerOfMassX,centerOfMassY])
	
	return centerOfMass


def readH5(fn):
    
	""" Reads HDF5 data file
	
	Args:
		fn (str): Path to h5 file
		
	Returns:
		np_data: numpy array containing trained probabilities
		[z-stack, y-coord, x-coord,(0=background, 1=foreground)]
	"""
    
	with h5py.File(fn,'r') as hf:
		print('List of arrays in this file: \n', hf.keys())
		data = hf.get(hf.keys()[0])
		np_data = np.array(data)
		print('Shape of the array: \n', np_data.shape)
	
	return np_data

def makeProbMask(array):
    
	""" Makes a mask from the trained probabilities
	
	Args:
		array (nparray): probability data
		
	Returns:
		mask (nparray): mask
	"""
	prob = np.copy(array)
	mask=np.zeros(prob.shape)
	mask[np.where(prob>0.9)]=1
	
	return mask