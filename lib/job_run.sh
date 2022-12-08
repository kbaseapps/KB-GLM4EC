#!/bin/bash
#SBATCH --job-name=sdk
#SBATCH --partition=math-alderaan
#SBATCH --time=7-00:00:00  

# run tensorflow in singularity container
# redirect output to a file so that it can be inspected before the end of the job
singularity exec /home/ceas/davoudis/tensorflow_nvidia.sif python3 RunGLM4EC.py >& RunGLM4EC.log 
cat RunGLM4EC.log 