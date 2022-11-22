FROM directed-benchmark-final:resume_with_asan

WORKDIR /benchmark

COPY benchmark/binutils-2.26-patched /benchmark/project/binutils-2.26-patched
COPY benchmark/libming-4.7-patched /benchmark/project/libming-4.7-patched

# Build patched benchmarks
RUN mkdir /benchmark/bin/patched
COPY docker-setup/build_binutils.sh /benchmark
RUN ./build_binutils.sh
COPY docker-setup/build_libming.sh /benchmark
RUN ./build_libming.sh

COPY docker-setup/replay_patched.sh /tool-script

WORKDIR /