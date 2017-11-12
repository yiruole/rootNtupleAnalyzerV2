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

eos = '/usr/bin/eos'

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
         metavar="moveFiles",default=True,action="store_false")
    parser.add_option("-i", "--ignoreCache", dest="ignoreMulticrabCache",
         help=("don't use cache file to skip checking status of jobs already done"),
         metavar="ignoreCache",default=False,action="store_true")
    parser.add_option("-r", "--noAutoResubmit", dest="noAutoResubmit",
         help=("don't automatically run the resub commands"),
         metavar="noAutoResub",default=False,action="store_true")
    parser.add_option("-p", "--doCrabPurge", dest="doCrabPurge",
         help=("run crab purge for completed tasks"),
         metavar="doCrabPurge",default=False,action="store_true")
    parser.add_option("-f", "--resubmitCERN", dest="resubmitCERN",
         help=("force to resubmit to CERN T2 only"),
         metavar="resubmitCERN",default=False,action="store_true")

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

#FIXME rewrite to use regular cp and '*'
def MoveFiles(outputFilesNotMoved,taskName):
  global eos
  for fn in outputFilesNotMoved:
    #print '\t',fn
    #cmd = eos+' cp /eos/cms'+fn+' '+taskName+'/'
    # on lxplus, eos is mounted
    cmd = 'cp /eos/cms'+fn+' '+taskName+'/'
    ret = subprocess.call(cmd.split())
    #print cmd
    if ret != 0:
      print 'did not manage to copy: /eos/cms'+fn,' to',taskName+'/','; cp had return code of',ret
      continue
    #cmd = eos+' rm /eos/cms'+fn
    # on lxplus, eos is mounted
    cmd = 'rm /eos/cms'+fn
    subprocess.call(cmd.split())
    #print cmd
    if ret == 0:
      outputFilesNotMoved.remove(fn)
  return outputFilesNotMoved


def MoveFilesCp(taskName):
  return


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

    tasksStatusDict = {}
    # Execute the command with its arguments for each task.
    for task in os.listdir(options.projDir):
        task = os.path.join(options.projDir, task)
        if not os.path.isdir(task):
            continue
        # ignore non-crab dirs
        if 'workdir' in task or 'cfgfiles' in task or 'output' in task:
          continue
        if task in completedTasksFromCache:
          print "Don't check status of task, was already completed:",task
          continue
        ## XXX SIC TEST
        #tasksStatusDict[task] = 'FAILED'
        ## XXX SIC TEST
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
        except Exception as e:
          print 'Got an exception:',
          print(e)
          print 'Skipping this task...'
          tasksStatusDict[task] = 'CAUGHT_EXCEPTION'
          continue

        if options.crabCmd != 'status':
          continue
        #print 'res=',res
        #print 'res[jobPerStatus]=',res['jobsPerStatus']
        #print 'res[status]=',res['status']
        #exit(0)
        if res['status']=='QUEUED':
            tasksStatusDict[task] = 'QUEUED'
            continue
        tasksStatusDict[task] = 'COMPLETED'
        #print res
        #for jobStatus in res[1]['jobList']:
        #print 'res[jobsPerStatus].keys()=',res['jobsPerStatus'].keys()
        for jobStatus in res['jobsPerStatus'].keys():
          if 'failed' in jobStatus:
            tasksStatusDict[task] = 'FAILED' # if there's at least one failed job, count task as FAILED so we resubmit
            break
          elif 'running' in jobStatus:
            tasksStatusDict[task] = 'SUBMITTED'
          elif 'idle' in jobStatus:
            tasksStatusDict[task] = 'SUBMITTED'
          elif 'transferring' in jobStatus:
            tasksStatusDict[task] = 'SUBMITTED'
        if tasksStatusDict[task] != 'FAILED' and 'failed' in res['status'].lower():
          tasksStatusDict[task] = res['status']
        print 'taskStatus=',tasksStatusDict[task]
        #if 'failed' in res['jobsPerStatus'].keys():
        #  tasksStatusDict[task] = 'FAILED' # if there's at least one failed job, count task as FAILED so we resubmit
        #else:

    if options.crabCmd != 'status':
      exit(0)
    totalTasks = len(tasksStatusDict)
    tasksCompleted = [task for task in tasksStatusDict if tasksStatusDict[task]=='COMPLETED']
    tasksSubmitted = [task for task in tasksStatusDict if tasksStatusDict[task]=='SUBMITTED']
    tasksSubmitFailed = [task for task in tasksStatusDict if tasksStatusDict[task]=='SUBMITFAILED']
    tasksFailed = [task for task in tasksStatusDict if tasksStatusDict[task]=='FAILED']
    tasksOther = [task for task in tasksStatusDict if task not in tasksCompleted and task not in tasksSubmitted and task not in tasksFailed and task not in tasksSubmitFailed]

    ourCacheFile = open(os.path.abspath('./multicrab.cache'),'a')
    exceptionTasks = []
    # move files for completed tasks
    if options.moveFiles and options.projDir is not None:
      if options.projDir[-1] != '/':
        options.projDir+='/'
      for taskName in tasksCompleted:
      # XXX SIC move dat files for all tasks, even partially completed ones
      #for taskName in tasksStatusDict.keys():
        # redirect the dump output so it doesn't fill up the screen
        print 'getting output file list for task:',taskName
        sys.stdout = open(os.devnull,'w')
        try:
          res = crabCommand('getoutput',taskName,'--dump')
        except HTTPException, hte:
          sys.stdout = sys.__stdout__
          print '-----> there was a problem running crab getoutput --dump %s see below.'%taskName
          print hte.headers
          exceptionTasks.append(taskName)
          continue
        except:
          print '-----> there was a problem running crab getoutput --dump %s see below.'%taskName
          exceptionTasks.append(taskName)
          continue
        sys.stdout = sys.__stdout__
        #print res
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
        tries = 0
        while len(outputFilesNotMoved) >= 1 and tries < 5:
          outputFilesNotMoved = MoveFiles(outputFilesNotMoved,taskName)
          print 'taskName:',taskName,'still has',len(outputFilesNotMoved),'output files to move; try again'
          tries+=1
        # XXX SIC disable
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
    if len(tasksFailed) > 0:
      #print 'Tasks failed:',len(tasksFailed),'/',totalTasks
      #for task in tasksFailed:
      #  try:
      #    res = crabCommand('status',task)
      #  except HTTPException, hte:
      #    print '-----> there was a problem running crab status %s; see below.'%taskName
      #    print hte.headers
      print 'commands to resubmit failed tasks (or tasks with failed jobs):'
      for task in tasksFailed:
        resubmitCmd = 'crab resubmit '
        if options.resubmitCERN:
          resubmitCmd+="--sitewhitelist=T2_CH_CERN "
        resubmitCmd+=task  
        print
        print '\t'+resubmitCmd
        if not options.noAutoResubmit:
          print 'Automatically resubmitting...'
          subprocess.call(resubmitCmd.split())
    if len(tasksCompleted) > 0 or len(completedTasksFromCache) > 0:
      print 'Tasks completed:',len(tasksCompleted)+len(completedTasksFromCache),'/',totalTasks
    if len(tasksSubmitFailed) > 0:
      print 'WARNING: submission failed for:'
      for task in tasksSubmitFailed:
        print '\tTask:',task,'\tStatus:',tasksStatusDict[task]

if __name__ == '__main__':
    main()


