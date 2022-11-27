#!/bin/bash
URL="http://ftp.gnu.org/gnu/binutils/binutils-2.26.tar.gz"
DIRNAME="binutils-2.26"
ARCHIVE=$DIRNAME".tar.gz"
CONFIG_OPTIONS="--disable-shared --disable-gdb \
                 --disable-libdecnumber --disable-readline \
                 --disable-sim --disable-ld"
DEFAULT_FLAGS="-g -fno-omit-frame-pointer -Wno-error"
ASAN_FLAGS="-fsanitize=address"
PATCH="/benchmark/patch"

function build_patched() {
    export CC="clang"
    export CXX="clang++"
    export CFLAGS="$DEFAULT_FLAGS $ASAN_FLAGS"
    export CXXFLAGS="$DEFAULT_FLAGS $ASAN_FLAGS"
    
    wget $URL -O $ARCHIVE

    for TARGET in $1; do
        rm -rf $DIRNAME
        tar -xzf $ARCHIVE || exit 1
        cd $DIRNAME
        patch -p2 < $PATCH/binutils-2.26/$TARGET.patch
        ./configure $CONFIG_OPTIONS || exit 1
        ## Parallel building according to https://github.com/aflgo/aflgo/issues/59
        ## Altohough an issue with parallel building is observed in libxml (https://github.com/aflgo/aflgo/issues/41), 
        ## We have not yet encountered a problem with binutils.
        make -j || exit 1
        cd -
        cp $DIRNAME/binutils/cxxfilt /benchmark/bin/patched/cxxfilt-patch-$TARGET || exit 1
    done

    rm -f $ARCHIVE && rm -rf $DIRNAME
}

mkdir -p /benchmark/bin/patched
build_patched "2016-4487 2016-4489 2016-4490 2016-4491 2016-4492 2016-4492-old 2016-6131"