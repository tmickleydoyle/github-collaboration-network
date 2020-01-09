PYTHON_MODULES := github-collaboration-network

PYTHON=/usr/local/bin/python3.7
PIP=/usr/local/bin/pip3.7
ENV=.env

default: server

env:
	virtualenv -p ${PYTHON} ${ENV}
	. ${ENV}/bin/activate
	${PIP} install -r requirements.txt
main: env
	python main.py
server: main
	python -m http.server
server_only:
	python -m http.server
