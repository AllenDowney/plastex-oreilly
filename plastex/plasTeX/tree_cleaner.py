"""This module contains code to perform transformations on the parse
tree before rendering.

Author: Allen B. Downey
Copyright 2012 Allen B. Downey

Same license as the rest of plasTeX.
"""

import codecs
import os
import re
import subprocess

from lxml import etree

from plasTeX.Base.LaTeX.Math import MathSymbol
from plasTeX.Logging import getLogger

log = getLogger()


def clean_label(s):
    """Cleans LaTeX labels so they are legal XML.

    Replaces : with ..

    s: string

    Returns: string
    """
    s = s.strip()
    s = re.sub(':', '..', s)
    return s


class TreeCleaner(object):
    def __init__(self, tex, document):
        self.tex = tex
        self.document = document
        self.document.contains_mml = False

        with Tralics() as self.tralics:
            self.clean()

    def clean(self):
        """Walk the node tree fixing problems.

        tex:
        document: TeXDocument
        """
        fp = codecs.open('plastex.before', 'w', encoding='utf-8')
        fp.write(self.document.toXML())
        fp.close()

        #print '-----------------------'
        self.walk(self.document, self.pass_one)
        self.walk(self.document, self.pass_two)
        #print '-----------------------'

        fp = codecs.open('plastex.after', 'w', encoding='utf-8')
        fp.write(self.document.toXML())
        fp.close()

    def walk(self, node, func):
        """Walks a node tree and invokes a function on each node.

        node: Node
        func: function object
        """
        for child in node.childNodes:
            self.walk(child, func)
        func(node)

    def pass_one(self, node):
        """Checks for problems and fixes them.

        Checks for things that should not be embedded in par.

        node: Node
        """
        self.test_math(node)
        self.test_quote(node)
        self.test_par(node)

        # Nope, turns out we don't want to remove whitespace
        # self.test_text(node)

    def pass_two(self, node):
        """Checks for problems and fixes them.

        Checks for things that should not be embedded in par.

        node: Node
        """
        self.test_index(node)
        self.test_figure(node)
        self.test_label(node)

    def test_index(self, node):
        """Checks for indexterms in a par by themselves.

        node: Node
        """
        if node.nodeName not in ['par']:
            return

        children = node.childNodes

        # if there are no index commands, it's ok
        flag = False
        for child in children:
            if child.nodeName in ['index']:
                flag = True
                break

        if not flag:
            return

        # if one of the siblings is a non-empty text node, it's ok
        if self.is_legit_par(node):
            return

        #print 'Floating indexterm...',

        sib = node.nextSibling
        if self.is_legit_par(sib):
            #print 'Moving down'
            self.move_contents(node, sib)
            return

        sib = node.previousSibling
        if self.is_legit_par(sib):
            #print 'Moving up'
            self.move_contents(node, sib)
            return

        #print 'Hoisting'
        self.replace(node, children)

    def move_contents(self, node, dest):
        """Move the contents of node into dest.

        node: source Node
        dest: destination Node
        """
        children = node.childNodes
        self.remove(node)

        for i, child in enumerate(children):
            dest.insert(i, child)

    def is_legit_par(self, node):
        """Checks whether a paragraph contains any non-whitespace text.

        node: Node
        """
        if node is None:
            return False

        if node.nodeName != 'par':
            return False

        for child in node.childNodes:
            if child.nodeName == '#text':
                if child.strip():
                    return True
        return False

    def get_sibling(self, target, offset=1):
        """Finds a sibling of the given node.

        target: the node whose sibling to find
        offset: which sibling to get, relative to target
        """
        parent = target.parentNode
        for i, node in enumerate(parent):
            if node == target:
                return parent[i+offset]

    def test_id(self, node):
        """For anything that has an ID, clean the label.

        Currently not used; probably not needed.
        """
        if not hasattr(node, 'id'):
            return

        if ':' not in node.id:
            return

        node.id = clean_label(node.id)
        log.info('test_id', node.nodeName, node.id)

    def test_label(self, node):
        """For anything that has a label, cleans the label."""
        try:
            label = node.getAttribute('label')
        except AttributeError:
            return

        if label is None:
            return

        if ':' not in label:
            return

        log.warning('No colons in labels, please: %s.', label)

        label = clean_label(label)
        node.setAttribute('label', label)
        node.argSource = label

        log.info('Replacement label: %s.', label)

    def test_math(self, node):
        """Checks for math tags we can convert to mathphrases.

        node: Node
        """
        if node.nodeName not in ['math', 'displaymath',
                                 'eqnarray', 'eqnarray*']:
            return

        # translate complicated math into MathML
        if self.is_simple_math(node):
            #print 'test_math simple', node.nodeName
            new_node = self.make_mathit(node)
        else:
            #print 'test_math not simple', node.nodeName
            new_node = self.make_mathml(node)

        self.replace(node, [new_node])

    def make_mathit(self, node):
        """Translates simple math into mathit."""
        children = node.childNodes

        phrase = self.document.createElement('mathit')
        phrase.extend(children)

        return phrase

    def make_mathphrase(self, node):
        """Translates simple math into mathphrase."""
        #print 'before'
        #self.print_tree(node, '')

        children = node.childNodes

        # math becomes mathphrase, which is rendered as inlinequation
        # displaymath becomes displaymathphrase, rendered as equation
        phrase = self.document.createElement(node.nodeName + 'phrase')
        phrase.extend(children)

        #print 'after'
        #self.print_tree(phrase, '')

        return phrase

    def make_mathml(self, node):
        """Converts a math expression to MathML.

        node: tree of DOM.Element

        Returns: tree of DOM.Element
        """
        self.document.contains_mml = True

        # use tralics to generate MathML
        latex = node.source
        #print 'latex', latex
        mathml = self.tralics.translate(latex)

        #print 'mathml'
        #for line in mathml.split():
        #    print line

        # parse the MathML
        root = etree.fromstring(mathml)

        # print 'dom', root

        # strip the formula tag
        assert root.tag == 'formula'
        root = root[0]

        # convert from etree.Element to DOM.Node 
        math = self.convert_elements(root)
        # print math.toXML()

        # wrap the whole thing in the right kind of tag
        tag_dict = {'math' : 'inlineequation',
                    'displaymath' : 'informalequation',
                    'eqnarray' : 'informalequation',
                    'eqnarray*' : 'informalequation',
                    }

        tag = tag_dict[node.nodeName]
        result = self.document.createElement(tag)
        result.append(math)

        return result

    def convert_elements(self, root):
        """Converts a tree of etree.Elements to a tree of DOM.Nodes.

        root: etree.Element
        
        Returns: DOM.Node
        """
        tag = root.tag.replace('{http://www.w3.org/1998/Math/MathML}', 'mml')
        node = self.document.createElement(tag)

        if root.text is not None:
            node.append(self.document.createTextNode(root.text))

        for child in root:
            node.append(self.convert_elements(child))

        return node

    def is_simple_math(self, node):
        """Decides if a math expression is simple enough to make into
        a mathphrase, rather than translating into MathML.

        node: DOM.Node

        Returns: boolean
        """
        # TODO: if there's a superscript and subscript on the same
        # character, it's not simple

        # TODO: expand this list of bad commands, or invert the logic
        # and enumerate acceptable commands

        # if it's a bad command, it's not simple
        if node.nodeName in ['sum', 'int', 'frac', 'cases', 'matrix', 
                             'pmatrix', 'eqnarray', 'eqnarray*']:
            #print node.nodeName
            return False

        # if it's text, it's simple
        if node.nodeName == '#text':
            #print '#text', node
            return True

        # if it's a math symbol with known Unicode, it's simple;
        # if we don't know the Unicode, it's not
        if isinstance(node, MathSymbol):
            #print 'MathSymbol', node.unicode
            if node.unicode is not None:
                return True
            else:
                return False

        # if any of the children are not simple, it's not simple
        for child in node.childNodes:
            if not self.is_simple_math(child):
                return False

        # if we get this far, it's simple
        return True
                
    def test_figure(self, node):
        """Checks for bad paragraphs inside figures.

        node: Node
        """
        if node.nodeName != 'figure':
            return

        # if the first node is a par, unpack it
        child = node.firstChild
        if child.nodeName != 'par':
            return

        self.unpack(child)

    def test_quote(self, node):
        """Checks for quote text not wrapped in a paragraph.

        node: Node
        """
        if node.nodeName not in ['quote', 'quotation', 'exercise']:
            return

        children = node.childNodes
        if len(children) == 0:
            # this is probably not valid, but we'll pass it along
            # for now
            return

        child = children[0]
        if child.nodeName == 'par':
            return

        # if the quote contains bare text, wrap it in a par
        par = self.document.createElement('par')
        par.extend(children)
        while node.childNodes:
            node.pop(-1)
        node.insert(0, par)

    def test_ref(self, node):
        """Removes redundant text from \ref commands.

        DOESN'T WORK!

        node: Node
        """
        if node.nodeName not in ['ref']:
            return

        #print '------------ref'
        #self.print_attributes(node)

        parent = node.parentNode
        #self.print_tree(parent)

        for i, sib in enumerate(parent):
            if sib == node:
                index = i

        #print 'index', index
        bad_list = ['Chapter', 'Section', 'Figure', 'Exercise', 'Example']

        for i in range(0, index):
            older_sib = parent[i]
            for term in bad_list:
                if older_sib.endswith(term):
                    for j in range(i, index):
                        parent.pop(i)

        #self.print_tree(parent)

    def print_node(self, node):
        print node.nodeName
        for child in node.childNodes:
            print '    ', child.nodeName

    def print_tree(self, node, prefix=''):
        if node.nodeName == '#text':
            print prefix + '#text', len(node), node[:20]
        else:
            print prefix + node.nodeName

        for child in node.childNodes:
            self.print_tree(child, prefix + '   ')

    def print_attributes(self, node):
        print node.nodeName
        for key, val in sorted(node.attributes.iteritems()):
            print '   ', key, val

    def print__dict__(self, node):
        print node.nodeName
        for key, val in sorted(node.__dict__.iteritems()):
            print '   ', key, val

    def test_par(self, node):
        """Checks for things that should not be embedded in par.

        node: Node
        """
        if node.nodeName != 'par':
            return

        children = node.childNodes
        if len(children) == 0:
            return

        first = children[0]
        if first.nodeName == '#text':
            return

        # list of nodeNames that should not be embedded in par
        bad_names = set(['itemize', 'description', 'enumerate', 'quote',
                         'verbatim', 'par', 'figure', 'centerline', 'label',
                         'table'])

        if first.nodeName not in bad_names:
            # print 'Allowing embedded', first.nodeName
            return

        self.replace(node, children)

    def unpack(self, node):
        """Replaces a node with its children.

        node: Node
        """
        self.replace(node, node.childNodes)

    def remove(self, child):
        """Removes a child from its parent node.

        Modifies the parent of child.

        child: Node
        """
        self.replace(child, [])

    def replace(self, child, replacements):
        """Replaces a node with a list of nodes.

        Modifies the parent of child.

        child: Node
        replacement: list of Nodes
        """
        parent = child.parentNode

        for i, node in enumerate(parent):
            if node == child:
                parent.pop(i)
                for j, replacement in enumerate(replacements):
                    parent.insert(i+j, replacement)
                return
        raise ValueError('Child not found.')


class Tralics(object):
    """Wrapper around a Tralics subprocess."""

    def __init__(self, executable='/usr/local/bin/tralics'):
        """Create a subprocess to communicate with Tralics.

        executable: string full path to tralics executable
        """
        self.process = None
        self.executable = executable
        if not os.path.exists(executable):
            raise ValueError('Unable to locate the executable ' +
                             self.executable)

    def __enter__(self):
        """Creates the subprocess (for use with the with statement)."""
        return self

    def __exit__(self, kind, value, traceback):
        """Terminates the subprocess (for use with the with statement)."""
        if self.process == None:
            return

        #print 'Terminating tralics...',
        self.process.terminate()
        # output = self.process.stdout.readline()
        # print 'close', output
        # self.process.stdin.write('y')
        self.process.wait()
        #print 'Done.'

    def start_tralics(self):
        """Starts the tralics subprocess."""
        cmd = [self.executable, 
               '-interactivemath',
               '-noconfig',
               '-entnames=no']
        self.process = subprocess.Popen(cmd, 
                                        shell=False, 
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        )
        for i in range(4):
            output = self.process.stdout.readline()
            # print 'enter', output

        err = self.process.stdout.readline()
        # print 'enter', err

    def stop_tralics(self):
        """Stops the tralics subprocess."""
        self.process.terminate()
        self.process.wait()
        self.process = None

    def translate(self, latex):
        """Translates a LaTeX math expression into MathML.

        latex: string

        Returns: string XML
        """
        latex = latex.strip()

        self.start_tralics()
        self.process.stdin.write(latex + '\n')
           
        while True:
            #print 'Waiting for tralics...',
            output = self.process.stdout.readline()

            if output.startswith('<formula'):
                break
            if output.startswith('Error'):
                print 'tralics:', output,
                output = self.process.stdout.readline()
                print 'tralics:', output,

        self.stop_tralics()
        return output.strip()

    def translate2(self, latex):
        """Translates a LaTeX math expression into MathML.

        latex: string

        Returns: string XML
        """
        self.start_tralics()

        latex = latex.strip()
        #print 'Waiting for tralics...'

        # this doesn't work because I can't figure out the input sequence
        # that makes tralics do one translation and then stop.
        output, error = self.process.communicate(latex + '\n')
        #print 'translate output', output
        #print 'translate error', error

        return output.strip()


def main():
    tralics = Tralics()

    print tralics.translate('$\int_0^{\infty} x^{-2} dx$')
    print tralics.translate('\[ x + 1 \]')
    print tralics.translate('$\int_0^{\infty} x^{-2} dx$')
    tralics.close()


if __name__ == '__main__':
    main()
