#!/usr/bin/env python2

import sys, os, getopt
sys.path.append('../../../src/')
import numpy as np
import subprocess
import mscgfm_check as check
import shutil 


############################### config #####################################

opts, args = getopt.getopt(sys.argv[1:], "e:")

mscg_exe = ''
mscg_suffix = ''
for opt, arg in opts:
    if opt == '-e':
        mscg_exec = arg

input_ref_traj = '../trajectories/lj_dimer_mixture.lammpstrj'
input_cg_traj = '../trajectories/lj_dimer_mixture_REM_trial.lammpstrj'

output_dir ='output/'
input_dir  ='input/'
reference_dir ='reference/'

filesToCheck = ['1_1.dat', '1_2.dat', '1_3.dat', '1_4.dat', '2_2.dat', '2_3.dat', '2_4.dat', '3_3.dat', '3_4.dat', '4_4.dat']

############################### run ########################################


## Make sure exectubles exist
if not os.path.isfile(mscg_exec):
    raise Exception('Could not find mscg executable\n')

# Make sure trajectory file exists
if not os.path.isfile(input_ref_traj):
    raise Exception('Could not find trajectory %s\n', input_ref_traj)
if not os.path.isfile(input_cg_traj):
    raise Exception('Could not find trajectory %s\n', input_cg_traj)

shutil.copy2(input_dir+'rmin.in',    output_dir)
shutil.copy2(input_dir+'rmin_b.in',  output_dir)
shutil.copy2(input_dir+'control.in', output_dir)
shutil.copy2(input_dir+'top.in',     output_dir)
shutil.copy2(input_dir+'b-spline-previous.out',     output_dir)


#############################
try: 
    test_output = subprocess.check_output([mscg_exec, '-l_cg', '../'+input_cg_traj, '-l_ref', '../'+input_ref_traj], cwd=output_dir, stderr= subprocess.STDOUT)
except subprocess.CalledProcessError as e:
    print e.output
    print "MSCG Did not complete! Please check the output\n"
    sys.exit(check.check_result_to_exitval(False))

lastLine  = test_output.split('\n')[-2]
if 'Freeing' not in lastLine:
    print "MSCG Did not complete! Please check the output\n"
    sys.exit(check.check_result_to_exitval(False))

result = True

for fileCheck in filesToCheck:
    dat1 = np.loadtxt(output_dir + fileCheck, unpack=True)
    dat2 = np.loadtxt(reference_dir + fileCheck, unpack=True)
    myResult = check.mscg_content_equality(dat1, dat2, prefix=fileCheck+" Data File equality: ")
    if myResult == False:
        result = False


sys.exit(check.check_result_to_exitval(result))
