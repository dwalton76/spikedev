clean:
	rm -rf build docs.log venv
	find . -name *.pyc | xargs rm -rf
	find . -name __pycache__ | xargs rm -rf

init:
	python3 -m venv venv
	@./venv/bin/python3 -m pip install black flake8 isort sphinx_rtd_theme sphinxcontrib.yt

format:
	@./venv/bin/isort -rc demo spikedev
	@./venv/bin/python3 -m black --config=.black.cfg demo spikedev
	@./venv/bin/python3 -m flake8 --config=.flake8.cfg demo spikedev

install:
	@./venv/bin/python3 ./utils/spike-install-spikedev.py

sphinx:
	rm -rf docs
	mkdir docs
	touch docs/.nojekyll
	@./venv/bin/sphinx-build -c docs-sphinx/ -w docs.log docs-sphinx docs
