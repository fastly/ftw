#!/bin/sh
#

destaddr="127.0.0.1"
ruledir=/CRS/tests

while getopts "Dd:f:" opt; do
    case $opt in
        f)
            if [ "$OPTARG" != "-" ]; then
                ruledir=$OPTARG
            else
                T=`mktemp -d /tmp/rules.XXXXX`
                while IFS= read LINE; do
                    echo "$LINE" >> $T/rules.yaml
                done
                ruledir=$T
            fi
            ;;
        D)
            set -x
            ;;
        d)
            destaddr=$OPTARG
            ;;
    esac
done

export PYTHONUNBUFFERED=1
python /opt/ftw/tools/build_journal.py --ruledir_recurse --ruledir $ruledir  --destaddr $destaddr
if [ $? -ne 0 ]; then
    echo "[errors] execution of the test fixture(s) failed"
    exit 1
fi
