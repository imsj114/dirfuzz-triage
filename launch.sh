#!/bin/bash
# Usage: ./launch.sh <crash_dir>

docker run --rm -it -m=4g -v$1:/crashes dirfuzz-triage