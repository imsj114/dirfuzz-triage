from triage import *

# (target bin, target cmdline, input src, additional option, triage function)

FUZZ_TARGETS = [
    ("swftophp-4.7-2016-9827", "@@", "file", check_swftophp_2016_9827),
    ("swftophp-4.7-2016-9829", "@@", "file", check_swftophp_2016_9829),
    ("swftophp-4.7-2016-9831", "@@", "file", check_swftophp_2016_9831),
    ("swftophp-4.7-2017-9988", "@@", "file", check_swftophp_2017_9988),
    ("swftophp-4.7-2017-11728", "@@", "file", check_swftophp_2017_11728),
    ("swftophp-4.7-2017-11729", "@@", "file", check_swftophp_2017_11729),
    ("swftophp-4.7.1-2017-7578", "@@", "file", check_swftophp_2017_7578),
    ("swftophp-4.8-2018-7868", "@@", "file", check_swftophp_2018_7868),
    ("swftophp-4.8-2018-8807", "@@", "file", check_swftophp_2018_8807),
    ("swftophp-4.8-2018-8962", "@@", "file", check_swftophp_2018_8962),
    ("swftophp-4.8-2018-11095", "@@", "file", check_swftophp_2018_11095),
    ("swftophp-4.8-2018-11225", "@@", "file", check_swftophp_2018_11225),
    ("swftophp-4.8-2018-20427", "@@", "file", check_swftophp_2018_20427),
    ("swftophp-4.8-2019-12982", "@@", "file", check_swftophp_2019_12982),
    ("swftophp-4.8.1-2019-9114", "@@", "file", check_swftophp_2019_9114),
    ("lrzip-ed51e14-2018-11496", "-t @@", "file", check_lrzip_2018_11496),
    ("cxxfilt-2016-4487", "", "stdin", check_cxxfilt_2016_4487),
    ("cxxfilt-2016-4489", "", "stdin", check_cxxfilt_2016_4489),
    ("cxxfilt-2016-4490", "", "stdin", check_cxxfilt_2016_4490),
    ("cxxfilt-2016-4491", "", "stdin", check_cxxfilt_2016_4491),
    ("cxxfilt-2016-4492", "", "stdin", check_cxxfilt_2016_4492),
    ("cxxfilt-2016-6131", "", "stdin", check_cxxfilt_2016_6131),
    ("objdump-2017-8392", "-SD @@", "file", check_objdump_2017_8392),
    ("objdump-2017-8396", "-W @@", "file", check_objdump_2017_8396),
    ("objdump-2017-8397", "-W @@", "file", check_objdump_2017_8397),
    ("objdump-2017-8398", "-W @@", "file", check_objdump_2017_8398),
    ("objcopy-2017-8393", "--compress-debug-sections @@ out", "file", \
        check_objcopy_2017_8393),
    ("objcopy-2017-8394", "-Gs @@ out", "file",  \
        check_objcopy_2017_8394),
    ("objcopy-2017-8395", "--compress-debug-sections @@ out", "file", \
        check_objcopy_2017_8395),
    ("xmllint-2017-5969", "--recover @@", "file", check_xmllint_2017_5969),
    ("xmllint-2017-9047", "--valid @@", "file", check_xmllint_2017_9047),
    ("xmllint-2017-9048", "--valid @@", "file", check_xmllint_2017_9048),
    ("xmllint-2017-9049", "--memory --oldxml10 @@", "file", check_xmllint_2017_9049),
    ("cjpeg-1.5.90-2018-14498", "-outfile /dev/null @@", "file", \
        check_cjpeg_2018_14498),
    ("cjpeg-2.0.4-2020-13790", "-outfile /dev/null @@", "file", \
        check_cjpeg_2020_13790),
    ("pngimage-2018-13785", "@@", "file", check_pngimage_2018_13785),
]


SLICE_TARGETS = {
    'swftophp-4.7': {
        'frontend':'cil',
        'entry_point':'main',
        'bugs': ['2016-9827', '2016-9829', '2016-9831', '2017-9988', '2017-11728', '2017-11729']
    },
    'swftophp-4.7.1': {
        'frontend':'cil',
        'entry_point':'main',
        'bugs': ['2017-7578']
    },
    'swftophp-4.8': {
        'frontend':'cil',
        'entry_point':'main',
        'bugs': ['2018-7868', '2018-8807', '2018-8962', '2018-11095', '2018-11225', '2018-20427', '2019-12982']
    },
    'swftophp-4.8.1': {
        'frontend':'cil',
        'entry_point':'main',
        'bugs': ['2019-9114']
    },
    'lrzip-ed51e14': {
        'frontend':'clang',
        'entry_point':'main',
        'bugs': ['2018-11496']
    },
    'objdump': {
        'frontend':'cil',
        'entry_point':'main',
        'bugs': ['2017-8392', '2017-8396', '2017-8397', '2017-8398']
    },
    'objcopy': {
        'frontend':'cil',
        'entry_point':'main',
        'bugs': ['2017-8393', '2017-8394', '2017-8395']
    },
    'cxxfilt': {
        'frontend':'cil',
        'entry_point':'main',
        'bugs': [
            '2016-4487', '2016-4489', '2016-4490', '2016-4491', '2016-4492',
            '2016-6131'
        ]
    },
    'xmllint': {
        'frontend':'cil',
        'entry_point':'main',
        'bugs': ['2017-5969', '2017-9047', '2017-9048', '2017-9049'],
        'additional_opt': ["-max_pre_iter", "10"]
    },
    'cjpeg-1.5.90': {
        'frontend':'cil',
        'entry_point':'main',
        'bugs': ['2018-14498']
    },
    'cjpeg-2.0.4': {
        'frontend':'cil',
        'entry_point':'main',
        'bugs': ['2020-13790']
    },
    'pngimage': {
        'frontend':'cil',
        'entry_point':'main',
        'bugs': ['2018-13785']
    },
}


def generate_fuzzing_worklist(benchmark, iteration):
    worklist = []
    for (targ_prog, cmdline, src, _) in FUZZ_TARGETS:
        if benchmark == targ_prog:
            if src not in ["stdin", "file"]:
                print("Invalid input source specified: %s" % src)
                exit(1)
            for i in range(iteration):
                iter_id = "iter-%d" % i
                worklist.append((targ_prog, cmdline, src, iter_id))
            break
    return worklist


def generate_slicing_worklist(benchmark):
    if benchmark == "all":
        worklist = list(SLICE_TARGETS.keys())
    elif benchmark in SLICE_TARGETS:
        worklist = [benchmark]
    else:
        print("Unsupported benchmark: %s" % benchmark)
        exit(1)
    return worklist


def check_targeted_crash(targ, replay_buf):
    for (targ_prog, _, _, crash_checker) in FUZZ_TARGETS:
        if targ_prog == targ:
            return crash_checker(replay_buf)
    print("Unknown target: %s" % targ)
    exit(1)
