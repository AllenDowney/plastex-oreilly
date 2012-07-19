# Before running plastex, add the current directory to PYTHONPATH
# export PYTHONPATH=$PYTHONPATH:.

plastex:
	rm -rf book/.svn
	plastex --renderer=DocBook --theme=book --image-resolution=300 --filename=book.xml book.tex
	rm -rf book/.svn

xxe:
	# install xxe from http://www.xmlmind.com/xmleditor/download.shtml
	~/xxe-perso-5_3_0/bin/xxe book/book.xml

install:
	cd ../../plastex; make install


