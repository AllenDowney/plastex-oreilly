#!/usr/bin/env python
import re
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer

class DocBook(_Renderer):
    """ Renderer for DocBook documents """
    fileExtension = '.xml'
    imageTypes = ['.png','.jpg','.jpeg','.gif']
    vectorImageTypes = ['.svg']

    def cleanup(self, document, files, postProcess=None):
        res = _Renderer.cleanup(self, document, files, postProcess=postProcess)
        return res

    def processFileContent(self, document, s):
        s = _Renderer.processFileContent(self, document, s)

        # Force XHTML syntax on empty tags
        s = re.sub(r'(<(?:hr|br|img|link|meta|col)\b.*?)\s*/?\s*(>)',
                   r'\1 /\2',
                   s,
                   re.I|re.S)

        s = re.sub(r'xml:id', r'id',s)

        # replace the first chapter with a preface
        s = re.sub(r'<chapter', r'<preface', s, count=1)
        s = re.sub(r'</chapter>', r'</preface>', s, count=1)

        # no space before an indexterm
        s = re.sub(r' <indexterm', r'<indexterm', s)
        s = re.sub(r'indexterm> ', r'indexterm>', s)

        # remove newlines in programlistings
        s = re.sub(r'\s*(<programlisting>)\n', r'\1', s)
        s = re.sub(r'\n(</programlisting>)\s*', r'\1', s)

        # remove para around bookinfo
        s = re.sub(r'<para>\s*(<bookinfo>)', r'\1', s)
        s = re.sub(r'(</bookinfo>)\s*</para>', r'\1', s)

        # remove pointless anchors
        s = re.sub(r'\s*(<anchor[^>]*>)\s*', r'',s)

        # get rid of empty paragraphs
        s = re.sub(r'\s*<para>\s*</para>\s*',  r'', s)
        s = re.sub(r'\s*<para>\s*</para>\s*',  r'', s)
        s = re.sub(r'\s*<para>\s*</para>\s*',  r'', s)

        return s
    
def or_terms(t):
    return '|'.join(['(%s)' % s for s in t])

Renderer = DocBook
