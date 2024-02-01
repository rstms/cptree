# top-level Makefile 

usage: short-help

### local install in editable mode for development
dev: uninstall 
	pip install --upgrade -e .[dev]

### install to the local environment from the source directory
install: 
	pip install --upgrade .

### remove module from the local python environment
uninstall: 
	pip install -U pip setuptools wheel flit
	pip uninstall -yqq $(module)

### remove all build, test, coverage and Python artifacts
clean: 
	for clean in $(call included,clean); do ${MAKE} $$clean; done
	rm -rf tests/data; mkdir tests/data

### test data targets

tests/data/src:
	cd $(dir $@); gh release download v0.0.3 --archive tar.gz --output - | tar zx
	mv tests/data/cptree-0.0.3 $@
	
tests/data/file_list: tests/data/src
	find $< -type f >$@

tests/data/file_list.sha256: tests/data/file_list
	xargs <$< -n 1 sha256sum >$@

testdata: tests/data/file_list.sha256
	mkdir -p tests/data/dst

include $(wildcard make/*.mk)
