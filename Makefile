clean:
	rm -rf build
	find . -name *.pyc | xargs rm -rf

format:
	isort -rc demo spikedev
	python3 -m black --config=.black.cfg demo spikedev
	python3 -m flake8 --config=.flake8.cfg demo spikedev

install:
	ampy --port /dev/ttyACM0 mkdir spikedev
	ampy --port /dev/ttyACM0 put spikedev/__init__.py spikedev/__init__.py
	ampy --port /dev/ttyACM0 put spikedev/logging.py spikedev/logging.py
	ampy --port /dev/ttyACM0 put spikedev/motor.py spikedev/motor.py
	ampy --port /dev/ttyACM0 put spikedev/tank.py spikedev/tank.py
	ampy --port /dev/ttyACM0 put spikedev/unit.py spikedev/unit.py
	ampy --port /dev/ttyACM0 put spikedev/wheel.py spikedev/wheel.py

install-lite:
	ampy --port /dev/ttyACM0 put spikedev/__init__.py spikedev/__init__.py
	ampy --port /dev/ttyACM0 put spikedev/logging.py spikedev/logging.py
	ampy --port /dev/ttyACM0 put spikedev/motor.py spikedev/motor.py
	ampy --port /dev/ttyACM0 put spikedev/tank.py spikedev/tank.py
	ampy --port /dev/ttyACM0 put spikedev/unit.py spikedev/unit.py
	ampy --port /dev/ttyACM0 put spikedev/wheel.py spikedev/wheel.py

sphinx:
	rm -rf docs
	sphinx-build -c docs-sphinx/ -w docs.log docs-sphinx docs
	touch docs/.nojekyll
