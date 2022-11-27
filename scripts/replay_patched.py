import sys, os, time, csv
from common import run_cmd, run_cmd_in_docker, check_cpu_count, fetch_works

IMAGE_NAME = "dirfuzz-triage"
CONTAINER_NAME = f"test-triage-{time.time()}"

BENCHMARK = {
    "cxxfilt": ("2016-4487 2016-4489 2016-4490 2016-4491 2016-4492 2016-6131", "", "stdin"),
    "swftophp-4.7": ("2016-9827 2016-9829 2016-9831 2017-9988 2017-11728 2017-11729", "@@", "file")
}

def spawn_container(crash_dir):
    cmd = "docker run --tmpfs /box:exec --rm -m=4g -v%s:/crashes -it -d --name %s %s" \
            % (crash_dir, CONTAINER_NAME, IMAGE_NAME)
    while run_cmd(cmd) == b'':
        time.sleep(1)
    
def run_triage(benchmark, targets):
    if targets == 'all':
        targets, cmdline, src = BENCHMARK[benchmark]
    else:
        _, cmdline, src = BENCHMARK[benchmark]
    cmd = "/tool-script/replay_patched.sh %s \"%s\" \"%s\" %s" % (benchmark, targets, cmdline, src)
    run_cmd_in_docker(CONTAINER_NAME, cmd, True)

def wait_finish():
    elapsed_min = 0
    while True:
        time.sleep(60)
        elapsed_min += 1
        print("Waited for %d min" % elapsed_min)

        stat_str = run_cmd_in_docker(CONTAINER_NAME, "cat /STATUS", False)
        if "FINISHED" in stat_str:
            print("Finished")
            break

def store_replay(outdir):
    cmd = "docker cp %s:/output %s" % (CONTAINER_NAME, outdir)
    run_cmd(cmd)

def cleanup_container():
    cmd = "docker kill %s" % CONTAINER_NAME
    run_cmd(cmd)

def main():
    if len(sys.argv) not in [5, 6]:
        print("Usage: %s <benchmark> <targets> <result_dir> <outdir> (iter)" % sys.argv[0])
        exit(1)
    benchmark = sys.argv[1]
    targets = sys.argv[2]
    result_dir = os.path.abspath(sys.argv[3])
    outdir = sys.argv[4]

    dirs = sorted(os.listdir(result_dir), key=lambda x:int(x.split('-')[-1]))
    if len(sys.argv) == 6:
        iter = int(sys.argv[5])
        dirs = dirs[:iter]
    for d in dirs:
        crash_dir = os.path.join(result_dir, d, 'crashes')
        # Run in docker
        spawn_container(crash_dir)
        run_triage(benchmark, targets)
        wait_finish()
        store_replay(os.path.join(outdir, d))
        cleanup_container()
        # Save replay_
        run_cmd("cp %s %s/replay_log_orig.txt" % (os.path.join(result_dir, d, "replay_log.txt"), os.path.join(outdir, d)))

if __name__ == "__main__":
    main()