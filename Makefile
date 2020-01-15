
format:
	isort -rc .
	python3 -m black --config=.black.cfg .
	python3 -m flake8 --config=.flake8.cfg .

install:
	# ampy --port /dev/ttyACM0 mkdir spikedev
	ampy --port /dev/ttyACM0 put spikedev/__init__.py spikedev/__init__.py
	ampy --port /dev/ttyACM0 put spikedev/logging.py spikedev/logging.py
	ampy --port /dev/ttyACM0 put spikedev/motor.py spikedev/motor.py
	ampy --port /dev/ttyACM0 put spikedev/unit.py spikedev/unit.py
	ampy --port /dev/ttyACM0 put spikedev/wheel.py spikedev/wheel.py
