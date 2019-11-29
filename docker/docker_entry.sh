#!/bin/sh
#

destaddr="127.0.0.1"
ruledir=/CRS/tests
cmd_args="--ruledir_recurse "

while getopts "Dd:f:FP:p:" opt; do
    case $opt in
        F)
            cmd_args="$cmd_args --destaddr_as_host "
            ;;
        f)
            if [ "$OPTARG" != "-" ]; then
                ruledir=$OPTARG
            else
                T=`mktemp -d -t rules.XXXXXX`
                while IFS= read -r LINE; do
                    echo -E "$LINE" >> /$T/rules.yaml
                done
                ruledir=$T
            fi
            cmd_args="$cmd_args  --ruledir $ruledir "
            ;;
        D)
            set -x
            ;;
        d)
            destaddr=$OPTARG
            cmd_args="$cmd_args --destaddr $destaddr "
            ;;
        p)
            port=$OPTARG
            cmd_args="$cmd_args --port $port"
            ;;
        P)
            proto=$OPTARG
            cmd_args="$cmd_args --protocol $proto"
            ;;
    esac
done

if [ "$ruledir" = "/CRS/tests" ]; then
    cmd_args="$cmd_args --ruledir $ruledir "
fi

export PYTHONUNBUFFERED=1
python /opt/ftw/tools/build_journal.py $cmd_args
if [ $? -ne 0 ]; then
    echo "[errors] execution of the test fixture(s) failed"
    exit 1
fi
