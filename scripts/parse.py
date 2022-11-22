import sys, os, re
from benchmark import check_targeted_crash

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

def parse_result(targ, targ_dir):
    log_file = os.path.join(targ_dir, REPLAY_LOG_FILE)
    f = open(log_file, "r", encoding="latin-1")
    buf = f.read()
    f.close()
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
        if check_targeted_crash(targ, replay_buf):
            found_time = int(replay_buf.split(FOUND_TIME_SIG)[1].split()[0])
            return found_time
    # If not found, return a high value to indicate timeout. When computing the
    # median value, should confirm that such timeouts are not more than a half.
    return None

def triage(benchmark, targ, outdir):
    # 1. Triage with ASAN log (original)
    with_asan = []
    replays = []
    log_file = os.path.join(outdir, REPLAY_LOG_ORIG_FILE)
    f = open(log_file, "r", encoding="latin-1")
    buf = f.read()
    f.close()
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
        with_asan.append(check_targeted_crash(f"{benchmark}-{targ}", replay_buf))
        replays.append(replay_buf)
    
    # 2. Triage with patched binary (new)
    with_patch = []
    log_file = os.path.join(outdir, f"replay_log_patch_{targ}.txt")
    f = open(log_file, "r", encoding="latin-1")
    buf = f.read()
    f.close()
    i = 0
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
        with_patch.append(not (('stack-overflow' in replays[i] and 'stack-overflow' in replay_buf) \
            or (get_crash_location(replays[i]) == get_crash_location(replay_buf))))
        i += 1
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
        fp_list, fn_list = [], []
        for k in range(66):
            with_asan, with_patch = triage(benchmark, targ, "output/cxxfilt-2016-4487" + f"-iter-{k}")
            if len(with_asan) != len(with_patch):
                print("Number of crashes does not match")
                print(k, targ)
                exit(1)
            total += len(with_asan)
            for i in range(len(with_asan)):
                if with_asan[i] and with_patch[i]:
                    tp += 1
                elif not with_asan[i] and not with_patch[i]:
                    tn += 1
                elif with_asan[i] and not with_patch[i]:
                    fp += 1
                    fp_list.append(f"iter-{k}-{i}")
                else:
                    fn += 1
                    fn_list.append(f"iter-{k}-{i}")
        # Print result
        print(f"{benchmark}-{targ}: total={total}, tp={tp}, tn={tn}, fp={fp}, fn={fn}")
        if DEBUG:
            if fp: print("fp_list: ", fp_list)
            if fn: print("fn_list: ", fn_list)

if __name__ == "__main__":
    main()
