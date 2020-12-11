results.txt: square.py test_square.py makefile
	echo '$ python -m unittest test_square.py' > results.txt
	python3 -m unittest test_square.py 2>&1 | tee -a results.txt
