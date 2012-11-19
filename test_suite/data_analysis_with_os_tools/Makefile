# Before running plastex, add the current directory to PYTHONPATH
# export PYTHONPATH=$PYTHONPATH:.

plastex:
	rm -rf master/.svn
	plastex --renderer=DocBook --theme=book --filename=master.xml master.tex
	rm -rf master/.svn

lint:
	xmllint --xinclude --postvalid --noout master/master.xml

debug:
	rm -rf master/.svn
	python -m pdb /usr/local/bin/plastex --renderer=DocBook --theme=book --filename=master.xml master.tex
	rm -rf master/.svn

xxe:
	# install xxe from http://www.xmlmind.com/xmleditor/download.shtml
	~/xxe-perso-5_3_0/bin/xxe master/master.xml

install:
	cd ../../plastex; make install


TEST_REPO = ../../test_repo

test_repo:
	rsync -a master/ $(TEST_REPO)
	rsync -a figs/* $(TEST_REPO)/figs
	cd $(TEST_REPO); svn ci -m "Testing; orm:commitpdf"

