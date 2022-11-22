FROM directed-benchmark-final:support-asan

WORKDIR /benchmark

# Build patched binutils-2.26
RUN mkdir /benchmark/patch
COPY patch/binutils-2.26 /benchmark/patch/binutils-2.26
COPY docker-setup/build_binutils.sh /benchmark
RUN ./build_binutils.sh
# Build patched libming-4.7
COPY patch/binutils-2.26 /benchmark/patch/binutils-2.26
COPY docker-setup/build_libming.sh /benchmark
RUN ./build_libming.sh

COPY docker-setup/replay_patched.sh /tool-script

WORKDIR /