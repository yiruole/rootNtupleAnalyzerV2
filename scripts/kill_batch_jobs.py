#!/usr/bin/python

import os, string, subprocess

proc = subprocess.Popen( [ 'bjobs' ], stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
output = proc.communicate()[0]
if proc.returncode != 0:
  print output
  sys.exit(1)

for i in output.splitlines():
  line = i.strip().split()
  job = line[0]
  if( job == "JOBID" ): continue
  cmd=("bkill "+job)
  print cmd
  os.system(cmd)
