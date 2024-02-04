# requirements - build requirements.txt 

requirements.txt: pyproject.toml
	tq -r '.project.dependencies|.[]' $< >$@

requirements-dev.txt: pyproject.toml
	tq -r '.project["optional-dependencies"].dev|.[]' $< >$@

docs/requirements.txt: pyproject.toml requirements.txt
	[ -e docs ] && tq -r '.project["optional-dependencies"].docs|.[]' $< >$@ || true
	cat requirements.txt >>$@


requirements: requirements.txt requirements-dev.txt docs/requirements.txt

requirements-clean:
	@:

requirements-sterile: requirements-clean
	rm -rf requirements*.txt
