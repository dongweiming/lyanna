checkfiles = views models *.py

help:
	@echo  "Lyanna development makefile"
	@echo
	@echo  "usage: make <target>"
	@echo  "Targets:"
	@echo  "    deps	Ensure dev/test dependencies are installed"
	@echo  "    lint	Reports all linter violations"
	@echo  "    style	Auto-formats the code"

deps:
	@pip install -r dev_requirements.txt

lint: deps
	flake8 $(checkfiles) || (echo "Please run 'make style' to try fix style issues" && false)
	bandit -r $(checkfiles) -s B403,B301,B104,B105,B311,B602,B404
	mypy $(checkfiles)

style: deps
	isort -rc $(checkfiles)
	autopep8 -i -r $(checkfiles)
