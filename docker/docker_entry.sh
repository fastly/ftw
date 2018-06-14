#!/bin/sh
#

destaddr="127.0.0.1"

while getopts "d:" opt; do
    case $opt in
        d)
            destaddr=$OPTARG
            ;;
    esac
done

export PYTHONUNBUFFERED=1
python /build_journal.py --ruledir_recurse --ruledir /CRS/tests --destaddr $destaddr
if [ $? -ne 0 ]; then
    echo "[errors] execution of the test fixture(s) failed"
    exit 1
fi
