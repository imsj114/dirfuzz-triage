#!/bin/bash

# replay_patched.sh <benchmark> <targets> <cmdline> <src>

CRASH_LIST=$(ls /crashes) || exit 1

# During the replay, set the following ASAN_OPTIONS again.
export ASAN_OPTIONS=allocator_may_return_null=1,detect_leaks=0

mkdir /output

for TARG in $2; do
    PATCHED=/benchmark/bin/patched/$1-patch-$TARG

    echo "Crash Replay log for $1-patch-$TARG" > /output/replay_log_patch_$TARG.txt

    for crash in $CRASH_LIST; do
        readarray -d , -t CRASH_ID <<<$crash

        echo -e "\nReplaying crash - ${CRASH_ID[0]} :" >> /output/replay_log_patch_$TARG.txt
        if [[ $4 == "stdin" ]]; then
            cat /crashes/$crash | timeout -k 30 15 $PATCHED 2>> /output/replay_log_patch_$TARG.txt
            
        elif [[ $4 == "file" ]]; then
            cp -f /crashes/$crash ./@@
            timeout -k 30 15 $PATCHED $3 2>> /output/replay_log_patch_$TARG.txt
        else
            echo "Invalid input source: $4"
            exit 1
        fi
    done
done

# Notify that the whole fuzzing campaign has successfully finished.
echo "FINISHED" > /STATUS
