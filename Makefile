export MEMORIOUS_CONFIG_PATH=src
export MMMETA=data

all: install mmmeta.pull run mmmeta.generate mmmeta.push

run:
	memorious run sehrgutachten

mmmeta.pull:
	aws s3 sync --exclude "*db-shm" --exclude "*db-wal" s3://dokukratie-dev/sehrgutachten/_mmmeta data/_mmmeta

mmmeta.push:
	aws s3 sync --exclude "*db-shm" --exclude "*db-wal" --acl public-read data/_mmmeta s3://dokukratie-dev/sehrgutachten/_mmmeta

mmmeta.%:
	mmmeta $*

install:
	pip install -e .
	mkdir -p data
	mkdir -p data/_mmmeta

