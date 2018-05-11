#!/bin/bash

#PalMPlusClusterDetection_wrapper.sh requires an external parameter file.(e.g. PalMPlusClusterDetection_wrapper.sh PalMPlusClusterDetection_params.bash). See the example parameter file: "CIFTIStatMapToZscore_params.bash" for more information regarding the different parameters.

source $1

#if parameters are missing use defaults
MatlabCIFTI=${MatlabCIFTI:-'/mnt/max/shared/code/internal/utilities/Matlab_CIFTI/'}
MatlabGIFTI=${MatlabGIFTI:-'/mnt/max/shared/code/external/utilities/gifti-1.6/'}
CIFTIPath=${CIFTIPath:-'/mnt/max/shared/code/internal/utilities/CIFTI/'}
WorkbenchCommand=${WorkbenchCommand:-'wb_command'}
CIFTIScalarPath=${CIFTIScalarPath:-'/mnt/max/shared/projects/FAIR_users/Feczko/code_in_dev/CIFTIScalarAnalysis/'}
FSPath=${FSPath:-'/mnt/max/shared/code/external/utilities/freesurfer-5.3.0-HCP/'}
PalmDir=${PalmDir:-'/mnt/max/shared/code/external/analyses/PALM/'}
pvalue_correction=${pvalue_correction:-0}
estimate_test_statistic=${estimate_test_statistic:-'false'}
test_statistic_CIFTI=${test_statistic_CIFTI:-'NONE'}
nperms=${nperms:-0}
OutputPrefix=${OutputPrefix:-'adahn'}

#check for flags and set appropriate parameters
if ${estimate_test_statistic}; then echo 'estimating p values using test statistics'; else test_statistic_CIFTI='NONE'; fi
#call matlab command and execute

matlab -nodisplay -nosplash -r "addpath(genpath('"$CIFTIScalarPath"')); PalMPlusClusterDetection('InputCIFTI','"$InputCIFTI"','OutputCIFTI','"$OutputCIFTI"','MatlabCIFTI', '"$MatlabCIFTI"','MatlabGIFTI','"$MatlabGIFTI"','CIFTIPath','"$CIFTIPath"', 'WorkbenchCommand','"$WorkbenchCommand"','PalmDir','"$PalmDir"','InputStructure', '"$InputStructure"','StructureType','"$StructureType"','CorrectionType','"$CorrectionType"', 'CorrectionThresh',"$CorrectionThresh",'FSPath','"$FSPath"','PvalueCorrection', "$pvalue_correction",'EstimateCorrection','"$test_statistic_CIFTI"','NPermutations',"$nperms",'OutputPrefix','"$OutputPrefix"'); exit"