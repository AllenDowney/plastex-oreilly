import sys, os
from glob import glob

def pipe(cmd):
    fp = os.popen(cmd)
    res = fp.read()
    stat = fp.close()
    return res, stat
 

for filename in glob('*.tex'):
    dest = filename + '.unix'

    cmd = r"perl -p -e 's/\r/\n/g'  < %s > %s" % (filename, dest)
    print cmd

    res, cmd = pipe(cmd)
    print res

    cmd = r"mv %s %s" % (dest, filename)
    print cmd

    res, cmd = pipe(cmd)
    print res

