clean:
	rm -rf build
	find . -name *.pyc | xargs rm -rf

format:
	isort -rc demo spikedev
	python3 -m black --config=.black.cfg demo spikedev
	python3 -m flake8 --config=.flake8.cfg demo spikedev

install:
	./utils/spike-install-spikedev.py

sphinx:
	rm -rf docs
	mkdir docs
	touch docs/.nojekyll
	sphinx-build -c docs-sphinx/ -w docs.log docs-sphinx docs
