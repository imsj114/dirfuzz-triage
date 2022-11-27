import sys, os
from benchmark import check_targeted_crash, check_targeted_crash_patch

REPLAY_ORIG_FILE = "replay_log_orig.txt"
FUZZ_LOG_FILE = "fuzzer_stats"
REPLAY_ITEM_SIG = "Replaying crash - "
ADDITIONAL_INFO_SIG = " is located "
FOUND_TIME_SIG = "found at "


def replace_none(tte_list, timeout):
    list_to_return = []
    for tte in tte_list:
        if tte is not None:
            list_to_return.append(tte)
        elif timeout != -1:
            list_to_return.append(timeout)
        else:
            print("[ERROR] Should provide valid T/O sec for this result.")
            exit(1)
    return list_to_return


def average_tte(tte_list, timeout):
    has_timeout = None in tte_list
    tte_list = replace_none(tte_list, timeout)
    avg_val = sum(tte_list) / len(tte_list)
    prefix = "> " if has_timeout else ""
    return "%s%d" % (prefix, avg_val)


def median_tte(tte_list, timeout):
    tte_list = replace_none(tte_list, timeout)
    tte_list.sort()
    n = len(tte_list)
    if n % 2 == 0: # When n = 2k, use k-th and (k+1)-th elements.
        i = int(n / 2) - 1
        j = int(n / 2)
        med_val = (tte_list[i] + tte_list[j]) / 2
        half_timeout = (tte_list[j] == timeout)
    else: # When n = 2k + 1, use (k+1)-th element.
        i = int((n - 1) / 2)
        med_val = tte_list[i]
        half_timeout = (tte_list[i] == timeout)
    prefix = "> " if half_timeout else ""
    return "%s%d" % (prefix, med_val)


def min_max_tte(tte_list, timeout):
    has_timeout = None in tte_list
    tte_list = replace_none(tte_list, timeout)
    max_val = max(tte_list)
    min_val = min(tte_list)
    prefix = "> " if has_timeout else ""
    return ("%d" % min_val, "%s%d" % (prefix, max_val))


def get_experiment_info(outdir):
    targ_list = []
    max_iter_id = 0
    for d in os.listdir(outdir):
        if d.endswith("-iter-0"):
            targ = d[:-len("-iter-0")]
            targ_list.append(targ)
        iter_id = int(d.split("-")[-1])
        if iter_id > max_iter_id:
            max_iter_id = iter_id
    iter_cnt = max_iter_id + 1
    return (targ_list, iter_cnt)

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


def parse_tte(targ, triage, targ_dir):
    log_orig = os.path.join(targ_dir, REPLAY_ORIG_FILE)
    with open(log_orig, "r", encoding="latin-1") as f:
        replay_orig = split_replay(f.read())
    # Parse with log_orig
    if triage == 'asan':
        for i in range(len(replay_orig)):
            if check_targeted_crash(targ, replay_orig[i]):
                found_time = int(replay_orig[i].split(FOUND_TIME_SIG)[1].split()[0])
                return found_time
        return None
    # Parse with log_patch
    log_patch = os.path.join(targ_dir, f"replay_log_patch_{triage}.txt")
    with open(log_patch, "r", encoding="latin-1") as f:
        replay_patch = split_replay(f.read())
    if len(replay_orig) != len(replay_patch):
        print("Length of replay file does not match")
        print(len(replay_orig), len(replay_patch))
        exit(1)
    for i in range(len(replay_orig)):
        if check_targeted_crash_patch(targ, replay_orig[i], replay_patch[i]):
            found_time = int(replay_orig[i].split(FOUND_TIME_SIG)[1].split()[0])
            return found_time
    return None

def analyze_targ_result(outdir, triage, timeout, targ, iter_cnt):
    tte_list = []
    for iter_id in range(iter_cnt):
        targ_dir = os.path.join(outdir, "%s-iter-%d" % (targ, iter_id))
        tte = parse_tte(targ, triage, targ_dir)
        tte_list.append(tte)
    print("(Result of %s)" % targ)
    print("Time-to-error: %s" % tte_list)
    print("Avg: %s" % average_tte(tte_list, timeout))
    print("Med: %s" % median_tte(tte_list, timeout))
    print("Min: %s\nMax: %s" % min_max_tte(tte_list, timeout))
    if None in tte_list:
        print("T/O: %d times" % tte_list.count(None))
    print("------------------------------------------------------------------")


def main():
    if len(sys.argv) not in [3, 4]:
        print("Usage: %s <output dir> <triage type> (timeout of the exp.)" % sys.argv[0])
        exit(1)
    outdir = sys.argv[1]
    triage = sys.argv[2]
    timeout = int(sys.argv[3]) if len(sys.argv) == 4 else -1
    targ_list, iter_cnt = get_experiment_info(outdir)
    targ_list.sort()
    for targ in targ_list:
        analyze_targ_result(outdir, triage, timeout, targ, iter_cnt)


if __name__ == "__main__":
    main()
