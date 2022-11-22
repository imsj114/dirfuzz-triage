import sys, os, re
from benchmark import check_targeted_crash, check_targeted_crash_patched

REPLAY_LOG_ORIG_FILE = "replay_log_orig.txt"
FUZZ_LOG_FILE = "fuzzer_stats"
REPLAY_ITEM_SIG = "Replaying crash - "
ADDITIONAL_INFO_SIG = " is located "
FOUND_TIME_SIG = "found at "

TARGETS = {
    "cxxfilt": ["2016-4487", "2016-4489", "2016-4490", "2016-4491", "2016-4492", "2016-6131"],
    "swftophp-4.7": ["2016-9827", "2016-9829", "2016-9831", "2017-9988", "2017-11728", "2017-11729"]
}

# Obtain the function where the crash had occurred.
def get_crash_location(buf):
    match = re.search(r"#0 0x[0-9a-f]+ in [\S]+", buf)
    if match is None:
        return ""
    start_idx, end_idx = match.span()
    line = buf[start_idx:end_idx]
    return line.split()[-1]

def split_replay(buf):
    replays = []
    while REPLAY_ITEM_SIG in buf:
        # Proceed to the next item.
        start_idx = buf.find(REPLAY_ITEM_SIG)
        buf = buf[start_idx + len(REPLAY_ITEM_SIG):]
        # Identify the end of this replay.
        if REPLAY_ITEM_SIG in buf:
            end_idx = buf.find(REPLAY_ITEM_SIG)
        else: # In case this is the last replay item.
            end_idx = len(buf)
        replay_buf = buf[:end_idx]
        # If there is trailing allocsite information, remove it.
        if ADDITIONAL_INFO_SIG in replay_buf:
            remove_idx = buf.find(ADDITIONAL_INFO_SIG)
            replay_buf = replay_buf[:remove_idx]
        replays.append(replay_buf)
    return replays

def triage(benchmark, targ, outdir):
    targ_full = benchmark + '-' + targ
    # 1. Split replay_orig
    log_orig = os.path.join(outdir, REPLAY_LOG_ORIG_FILE)
    f = open(log_orig, "r", encoding="latin-1")
    buf = f.read()
    f.close()
    replay_asan = split_replay(buf)
    with_asan = list(map(lambda x:check_targeted_crash(targ_full, x), replay_asan))
    
    # 2. Triage with patched binary (new)
    log_targ = os.path.join(outdir, f"replay_log_patch_{targ}.txt")
    f = open(log_targ, "r", encoding="latin-1")
    buf = f.read()
    f.close()
    replay_targ = split_replay(buf)
    if len(replay_asan) != len(replay_targ):
        print("Length of replay file does not match")
        exit(1)
    with_patch = []
    for i in range(len(replay_asan)):
        with_patch.append(check_targeted_crash_patched(targ_full, replay_asan[i], replay_targ[i]))
    return with_asan, with_patch

def main():
    if len(sys.argv) not in [3, 4]:
        print("Usage: %s <benchmark> <output dir> (-d)" % sys.argv[0])
        exit(1)
    benchmark = sys.argv[1]
    outdir = sys.argv[2]
    DEBUG = False
    if len(sys.argv) == 4:
        DEBUG = sys.argv[3] == "-d"

    for targ in TARGETS[benchmark]:
        total, tp, tn, fp, fn = 0, 0, 0, 0, 0
        if DEBUG:
            fp_list, fn_list = [], []
        outdir_list = sorted(os.listdir(outdir), key=lambda x:int(x.split('-')[-1]))
        for result_dir in outdir_list:
            idx = int(result_dir.split('-')[-1])
            result_dir = os.path.join(outdir, result_dir)
            with_asan, with_patch = triage(benchmark, targ, result_dir)
            total += len(with_asan)
            for i in range(len(with_asan)):
                if with_asan[i] and with_patch[i]:
                    tp += 1
                elif not with_asan[i] and not with_patch[i]:
                    tn += 1
                elif with_asan[i] and not with_patch[i]:
                    fp += 1
                    if DEBUG:
                        fp_list.append(f"iter-{idx}-{i}")
                else:
                    fn += 1
                    if DEBUG:
                        fn_list.append(f"iter-{idx}-{i}")
        # Print result
        print(f"{benchmark}-{targ}: total={total}, tp={tp}, tn={tn}, fp={fp}, fn={fn}")
        if DEBUG:
            if fp: print("fp_list: ", fp_list)
            if fn: print("fn_list: ", fn_list)

if __name__ == "__main__":
    main()
