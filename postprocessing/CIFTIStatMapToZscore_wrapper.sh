#!/bin/bash

#CIFTIStatMapToZscore_wrapper.sh requires an external parameter file.(e.g. CIFTIStatMapToZscore_wrapper.sh CIFTIStatMapToZscore_params.bash). See the example parameter file: "CIFTIStatMapToZscore_params.bash" for more information regarding the different parameters.

source $1

#if parameters are missing use defaults
MatlabCIFTI=${MatlabCIFTI:-'/mnt/max/shared/code/external/utilities/Matlab_CIFTI/'}
MatlabGIFTI=${MatlabGIFTI:-'/mnt/max/shared/code/external/utilities/gifti-1.6/'}
CIFTIPath=${CIFTIPath:-'/mnt/max/shared/code/internal/utilities/CIFTI/'}
WorkbenchCommand=${WorkbenchCommand:-'wb_command'}
CIFTIScalarPath=${CIFTIScalarPath:-'/mnt/max/shared/projects/FAIR_users/Feczko/code_in_dev/CIFTIScalarAnalysis/'}
#call matlab command and execute

matlab -nodisplay -nosplash -r "addpath('"$CIFTIScalarPath"'); CIFTIStatMapToZScore('InputCIFTI','"$InputCIFTI"','OutputCIFTI','"$OutputCIFTI"','MatlabCIFTI', '"$MatlabCIFTI"','MatlabGIFTI','"$MatlabGIFTI"','CIFTIPath','"$CIFTIPath"','WorkbenchCommand','"$WorkbenchCommand"'); exit"
