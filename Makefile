export MEMORIOUS_CONFIG_PATH=src
export MMMETA=data/sehrgutachten

all: install mmmeta.pull run mmmeta.generate mmmeta.push

run:
	memorious run sehrgutachten --threads=2

mmmeta.pull:
	aws s3 sync --exclude "*db-shm" --exclude "*db-wal" s3://dokukratie-dev/sehrgutachten/_mmmeta data/sehrgutachten/_mmmeta

mmmeta.push:
	aws s3 sync --exclude "*db-shm" --exclude "*db-wal" --acl public-read data/sehrgutachten/ s3://dokukratie-dev/sehrgutachten

mmmeta.%:
	mmmeta $*

install:
	pip install -e .
	mkdir -p data
	mkdir -p data/sehrgutachten
	mkdir -p data/sehrgutachten/_mmmeta

