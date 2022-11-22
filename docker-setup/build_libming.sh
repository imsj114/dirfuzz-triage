#!/bin/bash
GIT_URL="https://github.com/libming/libming.git"
TAG_NAME="ming-0_4_7"
RELEVANT_BINARIES="swftophp"
DEFAULT_FLAGS="-g -fno-omit-frame-pointer -Wno-error"
ASAN_FLAGS="-fsanitize=address"
PATCH="/benchmark/patch"

function build_patched() {
    export CC="clang"
    export CXX="clang++"
    export CFLAGS="$DEFAULT_FLAGS $ASAN_FLAGS -fcommon"
    export CXXFLAGS="$DEFAULT_FLAGS $ASAN_FLAGS -fcommon"

    git clone $GIT_URL SRC
    cd SRC
    git checkout $TAG_NAME
    cd ..

    for TARGET in $1; do
        rm -rf BUILD
        cp -rf SRC BUILD
        cd BUILD
        patch -p2 < $PATCH/libming-4.7/$TARGET.patch
        ./autogen.sh && ./configure --disable-shared --disable-freetype && make
        cd ..
        cp BUILD/util/swftophp /benchmark/bin/patched/swftophp-4.7-patch-$TARGET || exit 1
    done

    rm -rf BUILD && rm -rf SRC
}

build_patched "2016-9827 2016-9829 2016-9831 2017-9988 2017-11728 2017-11729"