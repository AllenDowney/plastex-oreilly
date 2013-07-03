tralics:
	tar -xzf tralics-src-2.14.5.tar.gz
	cd tralics-2.14.5/src; make
	cd tralics-2.14.5/src; sudo cp tralics /usr/local/bin

install_plastex:
	cd plastex; make

test_math:
	cd test_suite/math; make
