Branch of plasTeX that generates DocBook 4.5 that meets O'Reilly
style guidelines.

Authors of plasTeX: Kevin Smith and Tim Arnold

Author of this branch: Allen Downey


On a fresh Ubuntu install, run:

sudo apt-get update
sudo apt-get install texlive texlive-latex-extra hevea git-core make g++ python-lxml python-imaging dvipng libxml2-utils emacs


Get and make plasTeX:

git clone https://AllenDowney@github.com/oreillymedia/plastex-oreilly
cd plastex-oreilly/
make tralics
make install_plastex
echo ‘export PYTHONPATH=$PYTHONPATH:.’ >> ~/.bashrc
. ~/.bashrc


To run a test:

cd plastex-oreilly/test_suite/small
make install
make
make lint

