#!/usr/bin/env python
import os
import sys
import subprocess
from optparse import OptionParser

#
# Use commands like ./multicrab.py -c status -d runBetaOneLQ1MC/testTag_2015Jul13_104935/
#   This will check the status of the submitted crab jobs over multiple datasets.

try:
  from CRABAPI.RawCommand import crabCommand
except ImportError:
  print
  print 'ERROR: Could not load CRABClient.UserUtilities.  Please source the crab3 setup:'
  print 'source /cvmfs/cms.cern.ch/crab3/crab.sh'
  exit(-1)

from CRABClient.ClientExceptions import CachefileNotFoundException
from CRABClient.ClientExceptions import ConfigurationException
from httplib import HTTPException

eos = '/afs/cern.ch/project/eos/installation/pro/bin/eos.select'

def getOptions():
    """
    Parse and return the arguments provided by the user.
    """
    usage = ('usage: %prog -c CMD -d DIR [-o OPT]\nThe multicrab command'
                   ' executes "crab CMD OPT" for each task contained in DIR\nUse'
                   ' multicrab -h for help"')

    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--crabCmd", dest="crabCmd",
         help=("The crab command you want to execute for each task in "
               "the DIR"), metavar="CMD")
    parser.add_option("-d", "--projDir", dest="projDir",
         help="The directory where the tasks are located", metavar="DIR")
    parser.add_option("-o", "--crabCmdOptions", dest="crabCmdOptions",
         help=("The options you want to pass to the crab command CMD"
               "tasklistFile"), metavar="OPT", default="")
    parser.add_option("-m", "--moveFiles", dest="moveFiles",
         help=("move non-skim files from EOS to local outputdir"),
         metavar="moveFiles",default=True,action="store_true")
    parser.add_option("-i", "--ignoreCache", dest="ignoreMulticrabCache",
         help=("don't use cache file to skip checking status of jobs already done"),
         metavar="ignoreCache",default=False,action="store_true")
    parser.add_option("-r", "--noAutoResubmit", dest="noAutoResubmit",
         help=("don't automatically run the resub commands"),
         metavar="noAutoResub",default=False,action="store_true")
    parser.add_option("-p", "--doCrabPurge", dest="doCrabPurge",
         help=("run crab purge for completed tasks"),
         metavar="doCrabPurge",default=False,action="store_true")
    parser.add_option("-t", "--tasksToCopy", dest="tasksToCopy",
         help="The completed tasks to copy files from (in format \"['taskName',task2,...]\")", metavar="TASKS")

    (options, args) = parser.parse_args()

    if args:
        parser.error("Found positional argument(s) %s." % args)
    if not options.crabCmd:
        parser.error("(-c CMD, --crabCmd=CMD) option not provided")
    if not options.projDir:
        parser.error("(-d DIR, --projDir=DIR) option not provided")
    if not os.path.isdir(options.projDir):
        parser.error("Directory %s does not exist" % options.projDir)

    return options


def MoveFiles(outputFilesNotMoved,taskName):
  global eos
  for fn in outputFilesNotMoved:
    #print '\t',fn
    cmd = eos+' cp /eos/cms'+fn+' '+taskName+'/'
    ret = subprocess.call(cmd.split())
    #print cmd
    if ret != 0:
      continue
    cmd = eos+' rm /eos/cms'+fn
    subprocess.call(cmd.split())
    #print cmd
    if ret == 0:
      outputFilesNotMoved.remove(fn)
  return outputFilesNotMoved


def main():
    """
    Main
    """
    global eos
    options = getOptions()

    completedTasksFromCache = []
    if not options.ignoreMulticrabCache:
      # read our cache file (don't check status for completed tasks each time)
      if os.path.isfile(os.path.abspath('./multicrab.cache')):
        ourCacheFile = open(os.path.abspath('./multicrab.cache'),'r')
        for line in ourCacheFile:
          completedTasksFromCache.append(line.strip())
        ourCacheFile.close()

    if options.crabCmd != 'copyTaskFiles':
      tasksStatusDict = {}
      # Execute the command with its arguments for each task.
      tasksSkipped = []
      for task in os.listdir(options.projDir):
          task = os.path.join(options.projDir, task)
          if not os.path.isdir(task):
            continue
          # ignore non-crab dirs
          if 'workdir' in task or 'cfgfiles' in task or 'output' in task:
            continue
          if task in completedTasksFromCache:
            tasksSkipped.append(task)
            continue
          print
          print ("Executing (the equivalent of): crab %s %s %s" %
                (options.crabCmd, task, options.crabCmdOptions))
          try:
            res = crabCommand(options.crabCmd, task, *options.crabCmdOptions.split())
          except HTTPException, hte:
            print '-----> there was a problem. see below.'
            print hte.headers
            tasksStatusDict[task] = 'httpException'
            continue
          except CachefileNotFoundException:
            print 'task:',task,'has no .requestcache file; something wrong (or deleted dir?) continue'
            tasksStatusDict[task] = 'noCacheFile'
            continue
          except ConfigurationException:
            print 'Got a ConfigurationException; continue to next task anyway.'
            continue

          if options.crabCmd != 'status':
            continue
          tasksStatusDict[task] = 'COMPLETED'
          #print res
          #for jobStatus in res[1]['jobList']:
          for jobStatus in res['shortResult']['jobList']:
            if 'failed' in jobStatus:
              tasksStatusDict[task] = 'FAILED' # if there's at least one failed job, count task as FAILED so we resubmit
              break
            if 'running' in jobStatus:
              tasksStatusDict[task] = 'SUBMITTED'
              break
            if 'idle' in jobStatus:
              tasksStatusDict[task] = 'SUBMITTED'
              break
            if 'transferring' in jobStatus:
              tasksStatusDict[task] = 'SUBMITTED'
              break

      print 'skipped tasks:',tasksSkipped
      if options.crabCmd != 'status':
        exit(0)
      totalTasks = len(tasksStatusDict)
      tasksCompleted = [task for task in tasksStatusDict if tasksStatusDict[task]=='COMPLETED']
      tasksSubmitted = [task for task in tasksStatusDict if tasksStatusDict[task]=='SUBMITTED']
      tasksSubmitFailed = [task for task in tasksStatusDict if tasksStatusDict[task]=='SUBMITFAILED']
      tasksFailed = [task for task in tasksStatusDict if tasksStatusDict[task]=='FAILED']
      tasksOther = [task for task in tasksStatusDict if task not in tasksCompleted and task not in tasksSubmitted and task not in tasksFailed and task not in tasksSubmitFailed]
      print 'tasks completed',tasksCompleted
      #print 'getting files'
    else:
      tasksCompleted = [task.replace("'","").strip() for task in options.tasksToCopy.strip('[]').split(',')]
      #print tasksCompleted
      tasksCompletedFiltered = []
      for task in tasksCompleted:
        if task not in completedTasksFromCache:
          tasksCompletedFiltered.append(task)
      tasksCompleted = tasksCompletedFiltered
      tasksFailed = []
      totalTasks = -1
      tasksSubmitted = []
      tasksSubmitFailed = []
      tasksOther = []

    # resubmit failed tasks first
    if len(tasksFailed) > 0:
      #print 'Tasks failed:',len(tasksFailed),'/',totalTasks
      #for task in tasksFailed:
      #  try:
      #    res = crabCommand('status',task)
      #  except HTTPException, hte:
      #    print '-----> there was a problem running crab status %s; see below.'%taskName
      #    print hte.headers
      for task in tasksFailed:
        resubmitCmd = 'crab resubmit '+task  
        if not options.noAutoResubmit:
          print 'Automatically resubmitting '+task
          subprocess.call(resubmitCmd.split())

    ourCacheFile = open(os.path.abspath('./multicrab.cache'),'a')
    exceptionTasks = []
    # move files for completed tasks
    if options.moveFiles and options.projDir is not None:
      if options.projDir[-1] != '/':
        options.projDir+='/'
      for taskName in tasksCompleted:
        # redirect the dump output so it doesn't fill up the screen
        #print 'getting output file list for task:',taskName
        print 'run crab getoutput',taskName,'--dump'
        sys.stdout = open(os.devnull,'w')
        try:
          res = crabCommand('getoutput',taskName,'--dump')
        except HTTPException, hte:
          sys.stdout = sys.__stdout__
          print '-----> there was a problem running crab getoutput --dump %s see below.'%taskName
          print hte.headers
          exceptionTasks.append(taskName)
          continue
        sys.stdout = sys.__stdout__
        try:
          outputFileLFNs = res['lfn']
        except KeyError:
          print 'ERROR: no key called "lfn" found in result for task',taskName,'.'
          print 'result looks like:',res
          print "can't move files; continue"
          continue
        outputFilesToMove = [name for name in outputFileLFNs if not 'reduced_skim' in name]
        if len(outputFilesToMove) == 0:
          # if all files have "reduced_skim" in them, assume this is a skim of a reduced skim
          outputFilesToMove = [name for name in outputFileLFNs if not 'reduced_skim_skim' in name]
        outputFilesNotMoved = [fname for fname in outputFilesToMove if not os.path.isfile(taskName+'/'+fname.split('/')[-1])]
        print 'outputFilesToMove length=',len(outputFilesToMove)
        print 'outputFilesNotMoved length=',len(outputFilesNotMoved)
        # why check this? sometimes we move files but don't write to cache for some reason
        #if len(outputFilesNotMoved) == 0:
        #  continue
        #print 'outputFilesNotMoved[0]:',outputFilesNotMoved[0]
        #print 'os.path.isfile('+taskName+'/'+outputFilesNotMoved[0].split('/')[-1]+')',os.path.isfile(taskName+'/'+outputFilesNotMoved[0].split('/')[-1])
        #exit(-1)
        print 'completed task:',taskName
        print '      moving',len(outputFilesNotMoved),'files to',taskName
        #print outputFilesNotMoved
        #exit(-1)
        while len(outputFilesNotMoved) >= 1:
          outputFilesNotMoved = MoveFiles(outputFilesNotMoved,taskName)
          print 'taskName:',taskName,'still has',len(outputFilesNotMoved),'output files to move; try again'
        print '      Successfully moved all files; write to cache.'
        # check again, shouldn't be necessary
        # if we moved the files, call it OK even if purge fails later
        if not taskName in completedTasksFromCache:
          ourCacheFile.write(taskName+'\n')
    ourCacheFile.close()

    if len(exceptionTasks) > 0:
      print 'The following tasks had exceptions on crab getoutput:'
      for taskn in exceptionTasks:
        print taskn
      print

    # redefine completed tasks
    tasksCompleted = [task for task in tasksCompleted if not task in exceptionTasks]

    # crab purge
    purgeExceptionTasks = []
    if options.doCrabPurge:
      for taskName in tasksCompleted:
        try:
          res = crabCommand('purge',taskName)
        except HTTPException, hte:
          print '-----> there was a problem running crab purge %s see below.'%taskName
          try:
            print hte.headers
          except AttributeError:
            continue
          purgeExceptionTasks.append(taskName)
          continue
        except ConfigurationException:
          print '-----> there was a problem running crab purge %s see below.'%taskName
          print hte.headers
          purgeExceptionTasks.append(taskName)
          continue

      if len(purgeExceptionTasks) > 0:
        print 'The following tasks had exceptions on crab purge:'
        for taskn in purgeExceptionTasks:
          print taskn
        print

    # copy files even if purge failed

    # summary and resubmit commands
    totalTasks+=len(completedTasksFromCache)
    print
    print
    print 'SUMMARY'
    if len(tasksSubmitted) > 0:
      print 'Tasks submitted:',len(tasksSubmitted),'/',totalTasks
      print 'commands to get status:'
      for task in tasksSubmitted:
        print '\tcrab status',task
    if len(tasksOther) > 0:
      print 'Tasks with other status:',len(tasksOther),'/',totalTasks
      for task in tasksOther:
        print '\tTask:',task,'\tStatus:',tasksStatusDict[task]
    if len(tasksCompleted) > 0 or len(completedTasksFromCache) > 0:
      print 'Tasks completed:',len(tasksCompleted)+len(completedTasksFromCache),'/',totalTasks
    if len(tasksSubmitFailed) > 0:
      print 'WARNING: submission failed for:'
      for task in tasksSubmitFailed:
        print '\tTask:',task,'\tStatus:',tasksStatusDict[task]
    if len(tasksFailed) > 0 and options.noAutoResubmit:
      print 'commands to resubmit failed tasks (or tasks with failed jobs):'
      print
      print '\t'+resubmitCmd

if __name__ == '__main__':
    main()


