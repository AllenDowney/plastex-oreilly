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
        #s = re.sub(r'</partintro>\s*<partintro>', r'',s)

        # replace the first chapter with a preface
        s = re.sub(r'<chapter', r'<preface', s, count=1)
        s = re.sub(r'</chapter>', r'</preface>', s, count=1)
        #
        # get rid of duplicate xref gentext
        #s = re.sub(r'Chapter.<xref', r'<xref', s)
        #s = re.sub(r'Section.<xref', r'<xref', s)
        #s = re.sub(r'Exercise.<xref', r'<xref', s)
        #s = re.sub(r'Figure.<xref', r'<xref', s)

        # no space before an indexterm
        s = re.sub(r' <indexterm', r'<indexterm', s)
        s = re.sub(r'indexterm> ', r'indexterm>', s)

        s = re.sub(r'<para>\s*(<bookinfo)', r'\1', s)
        s = re.sub(r'(</bookinfo>)\s*</para>', r'\1', s)

        s = re.sub(r'<para>\s*(<figure)', r'\1', s)
        s = re.sub(r'(</figure>)\s*</para>', r'\1', s)

        s = re.sub(r'<para>\s*(<example)', r'\1', s)
        s = re.sub(r'(</example>)\s*</para>', r'\1', s)

        s = re.sub(r'<para>\s*(<itemizedlist>)', r'\1', s)
        s = re.sub(r'(</itemizedlist>)\s*</para>', r'\1', s)

        s = re.sub(r'<para>\s*(<orderedlist>)', r'\1', s)
        s = re.sub(r'(</orderedlist>)\s*</para>', r'\1', s)

        s = re.sub(r'<para>\s*(<variablelist)', r'\1', s)
        s = re.sub(r'(</variablelist>)\s*</para>', r'\1', s)

        s = re.sub(r'<para>\s*(<blockquote)', r'\1', s)
        s = re.sub(r'(</blockquote>)\s*</para>', r'\1', s)

        s = re.sub(r'<para>\s*(<informaltable)', r'\1', s)
        s = re.sub(r'(</informaltable>)\s*</para>', r'\1', s)

        # remove newlines in programlistings
        # remove <para> around programlistings
        s = re.sub(r'<para>\s*(<programlisting>)\n', r'\1', s)
        s = re.sub(r'\n(</programlisting>)\s*</para>', r'\1', s)
        #
        s = re.sub(r'<para>([^<]*<title)', r'\1',s)
        #
        s = re.sub(r'(</mediaobject>)\s*</para>', r'\1',s)
        #
        s = re.sub(r'<para>\s*(<anchor[^>]*>)\s*</para>', r'',s)
        #
        s = re.sub(r'(<para>)(\s*<para>)+', r'\1',s)
        s = re.sub(r'(</para>\s*)+(</para>)', r'\2',s)
        #
        #pattern1 = r'(<listitem>)\s*<para>'
        #pattern2 = r'</para>\s*(</listitem>)'
        #s = re.sub(pattern1,  r'\1',s)
        #s = re.sub(pattern2,  r'\1',s)
        #
        s = re.sub(r'<para>\s*</para>',  r'', s)
        #
        return s
    
def or_terms(t):
    return '|'.join(['(%s)' % s for s in t])

Renderer = DocBook
