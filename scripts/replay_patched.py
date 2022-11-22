import sys, os, time, csv
from common import run_cmd, run_cmd_in_docker, check_cpu_count, fetch_works

IMAGE_NAME = "benchmark-patched"
CONTAINER_NAME = "test-triage"

BENCHMARK = {
    "cxxfilt": ("2016-4487 2016-4489 2016-4490 2016-4491 2016-4492 2016-6131", "", "stdin"),
    "swftophp-4.7": ("2016-9827 2016-9829 2016-9831 2017-9988 2017-11728 2017-11729", "@@", "file")
}

def spawn_container(crash_dir):
    cmd = "docker run --tmpfs /box:exec --rm -m=4g -v%s:/crashes -it -d --name %s %s" \
            % (crash_dir, CONTAINER_NAME, IMAGE_NAME)
    run_cmd(cmd)
    
def run_triage(benchmark):
    targets, cmdline, src = BENCHMARK[benchmark]
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

def store_replay(name):
    cmd = "docker cp %s:/output output/%s" % (CONTAINER_NAME, name)
    run_cmd(cmd)

def cleanup_container():
    cmd = "docker kill %s" % CONTAINER_NAME
    run_cmd(cmd)

def main():
    if len(sys.argv) != 3:
        print("Usage: %s <benchmark> <outdir>" % sys.argv[0])
        exit(1)
    benchmark = sys.argv[1]
    outdir = os.path.abspath(sys.argv[2])

    dirs = sorted(os.listdir(outdir), key=lambda x:int(x.split('-')[-1]))
    for d in dirs[66:]:
        crash_dir = os.path.join(outdir, d, 'crashes')
        # Run in docker
        spawn_container(crash_dir)
        run_triage(benchmark)
        wait_finish()
        store_replay(d)
        cleanup_container()
        # Save replay_
        run_cmd("cp %s output/%s/replay_log_orig.txt" % (os.path.join(outdir, d, "replay_log.txt"), d))


if __name__ == "__main__":
    main()