# Don't print the Make recipe lines
.SILENT:


setup:
	python3 -m pip install -r requirements.txt -t ./lib/ --upgrade