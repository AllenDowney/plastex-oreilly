"""This module contains code to perform transformations on the parse
tree before rendering.

Author: Allen B. Downey
Copyright 2012 Allen B. Downey

Same license as the rest of plasTeX.
"""

import codecs

class TreeCleaner(object):
    def __init__(self, tex, document):
        self.tex = tex
        self.document = document
        self.clean()

    def clean(self):
        """Walk the node tree fixing problems.

        tex:
        document: TeXDocument
        """
        fp = codecs.open('plastex.before', 'w', encoding='utf-8')
        fp.write(self.document.toXML())
        fp.close()

        print '-----------------------'
        self.walk(self.document, self.test_node)
        print '-----------------------'

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

    def test_node(self, node):
        """Checks for problems and fixes them.

        Checks for things that should not be embedded in par.

        node: Node
        """
        self.test_par(node)
        self.test_quote(node)
        self.test_figure(node)
        self.test_math(node)

    def test_math(self, node):
        """Checks for math tags we can convert to mathphrases.

        node: Node
        """
        if node.nodeName not in ['math', 'displaymath']:
            return

        print 'before'
        self.print_tree(node, '')

        children = node.childNodes

        # math becomes mathphrase, which is rendered as inlinequation
        # displaymath becomes displaymathphrase, rendered as equation
        #phrase = self.document.createElement(node.nodeName + 'phrase')
        phrase = self.document.createElement('mathphrase')
        phrase.extend(children)
        self.replace(node, [phrase])

        print 'after'
        self.print_tree(phrase, '')
                
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
        child = children[0]
        if child.nodeName == 'par':
            return

        # if the quote contains bare text, wrap it in a par
        par = self.document.createElement('par')
        par.extend(children)
        while node.childNodes:
            node.pop(-1)
        node.insert(0, par)

    def print_node(self, node):
        print node.nodeName
        for child in node.childNodes:
            print '    ', child.nodeName

    def print_tree(self, node, prefix):
        if node.nodeName == '#text':
            print prefix + node
        else:
            print prefix + node.nodeName

        for child in node.childNodes:
            self.print_tree(child, prefix + '   ')

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
                         'verbatim', 'par', 'figure', 'centerline', 'label'])

        if first.nodeName not in bad_names:
            print 'Allowing embedded', first.nodeName
            return

        self.replace(node, children)

    def unpack(self, node):
        """Replaces a node with its children.

        node: Node
        """
        self.replace(node, node.childNodes)

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


