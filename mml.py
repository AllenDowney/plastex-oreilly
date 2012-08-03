"""This module generates class definitions and templates for
MathML presentation tags.

To be pasted into 

Base/LaTeX/Math.py
Renderers/DocBook/Math.zpts

Author: Allen B. Downey
Copyright 2012 Allen B. Downey

Same license as the rest of plasTeX.
"""

import csv

fp = open('mml_tags.csv')
reader = csv.reader(fp)

tags = []
for t in reader:
    tags.append(t[0])


for tag in tags:
    print 'name: mml%s' % tag
    print '<mml:%s tal:content="self"></mml:%s>' % (tag, tag)
    print

for tag in tags:
    print 'class mml%s(Command):' % tag
    print '    args = "self"'
    print


