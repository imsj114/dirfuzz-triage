#!/bin/bash

function build_patched() {
    DEFAULT_FLAGS="-g -fno-omit-frame-pointer -Wno-error"
    ASAN_FLAGS="-fsanitize=address"

    export CC="clang"
    export CXX="clang++"
    export CFLAGS="$DEFAULT_FLAGS $ASAN_FLAGS -fcommon"
    export CXXFLAGS="$DEFAULT_FLAGS $ASAN_FLAGS -fcommon"

    for BUG_NAME in $1; do
        echo $BUG_NAME
        DIRNAME="project/libming-4.7-patched/libming-4.7-patch-$BUG_NAME"

        cd $DIRNAME
        ./autogen.sh && ./configure --disable-shared --disable-freetype && make
        cd -
        cp $DIRNAME/util/swftophp /benchmark/bin/patched/swftophp-4.7-patch-$BUG_NAME || exit 1
    done
}

build_patched "2016-9827 2016-9829 2016-9831 2017-9988 2017-11728 2017-11729"