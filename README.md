# autoslurm
Automatic .gjf to .inp converter and .slurm creator for use of the TACC Gaussian program for quantum computing

"The Texas Advanced Computing Center at the University of Texas at Austin, United States, 
is an advanced computing research center that is based on comprehensive advanced computing 
resources and supports services to researchers in Texas and across the U.S."  Wikipedia

"Gaussian is a quantum mechanics package for calculating molecular properties from first principles."

Autoslurm.py is a python script that takes files, namely .gjf, which are usually created 
by the program GaussView, and turns them into .inp files, which are used by the program
Gaussian, which is hosted by the TACC.

In order to use gaussian, a .slurm file is needed, which contains the instruction which
Gaussian uses to be able to tell which .inp files to analyse. This tool is simply
an easier method to create slurm files for bulk molecules. 

This tool cannot do anything special except convert directly, output from
GaussView into simple .inp and .slurm.

This tool has not been tested on anything other than any simple .gjf in the form of:

Using this tool, you are assumed to have your directory beginning with /home1/

```
%chk=C:\Users\abc123\OneDrive - Hogwarts School of Magic\Documents\c-glyoxal.chk
# opt freq hf/6-31g(d) geom=connectivity

Title Card Required

0 1
 C                  0.21210108    1.48334760   -0.24843609
 H                  0.28681273    1.92319525   -1.22098543
 C                  0.13456928   -0.04747846   -0.09957246
 H                  0.15541172   -0.67125673   -0.96869056
 O                  0.04670505   -0.56477228    1.04421840
 O                  0.18758838    2.21695750    0.77371175

 1 2 1.0 3 1.0 6 2.0
 2
 3 4 1.0 5 2.0
 4
 5
 6


```

In which it removes the first line and replaces it with some key information, so then
this line,

```
%chk=C:\Users\abc123\OneDrive - Hogwarts School of Magic\Documents\c-glyoxal.chk
```
  
is replaced with, for instance,

```
%nprocshared=12
%rwf=/home1/USERID/USERNAME/gaussian/c-glyoxal.rwf
%chk=/home1/USERID/USERNAME/gaussian/c-glyoxal.chk
%mem=56GB
%NProcs=12
```
  
Which are changes youd find in a template.

The .slurm file that is created is also from the template, it would look something like this,

```
#!/bin/bash
#----------------------------------------------------
# SLURM job script for TACC Lonestar 6
#----------------------------------------------------

#SBATCH -J c-glyoxal                        # Job name
#SBATCH -o c-glyoxal.%j.out                 # Standard output file
#SBATCH -e c-glyoxal.%j.error               # Error file
#SBATCH -p normal                            # Queue name
#SBATCH -N 1                                 # Number of nodes
#SBATCH -n 1                                 # Number of tasks
#SBATCH -A CHEM123          # Project ID
#SBATCH -t 47:50:00                          # Max runtime (47.5 hours)
#SBATCH --mail-user=harry.potter01@hogwarts.edu      # Email for notifications
#SBATCH --mail-type=all                      # Send email at start and end

echo "Starting job on $(date)"
module load gaussian
module list

# Ensure Gaussian directory exists
mkdir -p /home1/USERID/USERNAME/gaussian

# Set Gaussian scratch directory to match home1 location
export GAUSS_SCRDIR=/home1/USERID/USERNAME/gaussian


# Run Gaussian
time g16 < /home1/USERID/USERNAME/gaussian/c-glyoxal.inp > /home1/USERID/USERNAME/gaussian/c-glyoxal.log
```

Happy slurming!

https://izotutor.wixsite.com/undefined
