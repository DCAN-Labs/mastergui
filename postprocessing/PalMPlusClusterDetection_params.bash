#!/bin/bash
#Paths for external packages
MatlabCIFTI=/mnt/max/shared/code/internal/utilities/Matlab_CIFTI/ #path to MATLAB CIFTI repository needed to manipulate ciftis and giftis
MatlabGIFTI=/mnt/max/shared/code/external/utilities/gifti-1.6/ #path to MATLAB GIFTI repository needed to manipulate giftis
CIFTIPath=/mnt/max/shared/code/internal/utilities/CIFTI/ #path to CIFTI repository needed to read and write CIFTIs
PalmDir=/mnt/max/shared/code/external/analyses/PALM/ #path to PALM repository needed to run cluster detection and read surface file
WorkbenchCommand=wb_command #binary exectuable workbench command file -- full path is not needed
CIFTIScalarPath=/mnt/max/shared/projects/FAIR_users/Feczko/code_in_dev/CIFTIScalarAnalysis/ #path to CIFTIScalarAnalysis repository
FSPath=/mnt/max/shared/code/external/utilities/freesurfer-5.3.0-HCP/ #path to freesurfer -- used to load surface structures into PALM
#inputs
InputCIFTI=/mnt/max/shared/projects/MyStudy/MyData/stat_map.dscalar.nii #input statistical map
	pvalue_correction=0 #if set to a non-zero will replace any zeros in the statistical map with a nonzero of this value
InputStructure=/mnt/max/shared/projects/MyStudy/MyData/midthickness.gii
	StructureType='surface'
estimate_test_statistic='false' #if set to true, one can estimate 0 P values from a test statistic file
	test_statistic_CIFTI='NONE' #the full path to the test statistic file, if 'NONE' is specified then this step will be skipped
#outputs
OutputCIFTI=/mnt/max/shared/projects/MyStudy/MyData/zscore_map.dscalar.nii #output statistical map/
OutputPrefix='FDR' #prefix used to name the files that are output
#MC parameters
CorrectionType='FDR' #type of MC correction, can be one of: FDR, extent,mass,density,tippet,or pivotal
CorrectionThresh=0.05
nperms=0 #number of permutations to run for random field theory p-value calcuation -- used for cluster discovery only
