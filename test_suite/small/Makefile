plastex:
	# Before running plastex, we need the current directory in PYTHONPATH
	# export PYTHONPATH=$PYTHONPATH:.
	rm -rf book/.svn
	plastex --renderer=DocBook --theme=book --image-resolution=300 --filename=book.xml book.tex
	rm -rf book/.svn

xxe:
	# install xxe from http://www.xmlmind.com/xmleditor/download.shtml
	~/xxe-perso-5_3_0/bin/xxe book/book.xml

vector:
	plastex --renderer=DocBook --theme=book --vector-imager=dvisvgm --filename=book.xml book.tex

small: small.tex
	plastex --renderer=DocBook --theme=book --image-resolution=300 --filename=small.xml small.tex

sample:
	plastex --renderer=DocBook --theme=book --image-resolution=300 --image-scale-factor=0.25 --filename=sample2e.xml sample2e.tex
	~/Downloads/xxe-perso-4_8_0/bin/xxe sample2e/sample2e.xml

clean:
	rm -f *~ *.aux *.log *.dvi *.idx *.ilg *.ind *.toc



