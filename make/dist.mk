# python dist makefile

wheel := dist/$(module)-$(version)-py2.py3-none-any.whl
dependency_wheels := $(filter-out $(wildcard dist/*.whl),$(wheel))

$(wheel): $(src) pyproject.toml
	rm -f dist/$(module)-*.whl
	flit build

wheel: $(wheel) depends tox 

### build wheel 
dist: wheel 

dist-clean:
	[ -d dist ] && find dist -not -name README.md -not -name dist -exec rm -f '{}' + || true
	rm -rf build *.egg-info .eggs wheels

dist-sterile:
	@:
