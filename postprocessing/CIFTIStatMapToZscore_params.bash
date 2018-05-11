#!/bin/bash
#Paths for external packages
MatlabCIFTI=/mnt/max/shared/code/internal/utilities/Matlab_CIFTI/ #path to MATLAB CIFTI repository needed to manipulate ciftis and giftis
MatlabGIFTI=/mnt/max/shared/code/external/utilities/gifti-1.6/ #path to MATLAB GIFTI repository needed to manipulate giftis
CIFTIPath=/mnt/max/shared/code/internal/utilities/CIFTI/ #path to CIFTI repository needed to read and write CIFTIs
WorkbenchCommand=wb_command #binary exectuable workbench command file -- full path is not needed
CIFTIScalarPath=/mnt/max/shared/projects/FAIR_users/Feczko/code_in_dev/CIFTIScalarAnalysis/ #path to CIFTIScalarAnalysis repository
#inputs
InputCIFTI=/mnt/max/shared/projects/MyStudy/MyData/stat_map.dscalar.nii #input statistical map
#outputs
OutputCIFTI=/mnt/max/shared/projects/MyStudy/MyData/zscore_map.dscalar.nii #output statistical map/
