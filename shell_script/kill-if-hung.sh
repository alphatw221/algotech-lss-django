#!/usr/bin/env bash
set -e

TIMEOUT=60
LAST_CHANGED="$(date +%s)"

{
    set -e
    while true; do
        sleep 1
        kill -USR1 $$
    done
} &

trap check_output USR1

check_output() {
    CURRENT="$(date +%s)"
    if [[ $((CURRENT - LAST_CHANGED)) -ge $TIMEOUT ]]; then
        echo "Process STDOUT hasn't printed in $TIMEOUT seconds"
        echo "Considering process hung and exiting"
        exit 1
    fi
}

STDOUT_PIPE=$(mktemp -u)
mkfifo $STDOUT_PIPE

trap cleanup EXIT
cleanup() {
    kill -- -$$ # Send TERM to child processes
    [[ -p $STDOUT_PIPE ]] && rm -f $STDOUT_PIPE
}

$@ >$STDOUT_PIPE || exit 2 &

while true; do
    if read tmp; then
        echo "$tmp"
        LAST_CHANGED="$(date +%s)"
    fi
done <$STDOUT_PIPE