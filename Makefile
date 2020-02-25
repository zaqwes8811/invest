
all:
	ENVVAR := 10
	export ENVVAR
	# ="$(PYTHONPATH):$(shell pwd)/python"
	# export PYTHONPATH=/my/path:${PYTHONPATH}; \
	PYTHONPATH=.. python -m top.py