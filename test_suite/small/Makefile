# Before running plastex, add the current directory to PYTHONPATH
# export PYTHONPATH=$PYTHONPATH:.

plastex:
	rm -rf book/.svn
	python preprocess.py book.tex > book.pre.tex
	plastex --renderer=DocBook --theme=book --filename=book.xml --dir=book book.pre.tex
	rm -rf book/.svn

lint:
	xmllint --xinclude --postvalid --noout book/book.xml

xxe:
	# install xxe from http://www.xmlmind.com/xmleditor/download.shtml
	~/xxe-perso-5_3_0/bin/xxe book/book.xml

install:
	cd ../../plastex; make install


TEST_REPO = ../../test_repo

test_repo:
	rsync -a book/ $(TEST_REPO)
	rsync -a figs/* $(TEST_REPO)/figs
	cd $(TEST_REPO); svn ci -m "Testing; orm:commitpdf"

dropbox:
	rsync -a book /home/downey/Dropbox/plastex-oreilly
