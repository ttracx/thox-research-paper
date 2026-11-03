"""Linux ABI coverage at the ThoxInux pin, by area, and against a traced agent loop.

Part A (observed artifact). Parse the upstream Ginux compatibility ledger at
the commit ThoxInux pins (36503bda2d87465765e1b94e65f9d100f27ed5be), fetched
from GitHub on 2026-11-03, and classify its 375 dispatched syscalls into areas
by name. The status vocabulary (Complete, Partial, Policy-denied, Missing) and
every status value are the ledger's; the area classification is this paper's.

Part B (measured on the authoring host, not on ThoxInux). Run a small
reference agent loop written for this paper (read a config, append a log,
spawn a child process and wait, open a TCP connection to a local listener,
poll, handle a signal, map a file) under strace on the authoring host's Linux,
collect the distinct syscalls it issues, and join them with the ledger
statuses. This says which of the syscalls a plain Python loop issues are
Complete, Partial or Policy-denied at the pin. It does not run on Ginux and it
does not establish that the loop would work there.

Outputs exp/results/syscalls.json.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import textwrap
from collections import Counter
from pathlib import Path

RESULTS = Path(__file__).with_name("results") / "syscalls.json"
LEDGER = Path("/home/claude/ginux_ledger/LINUX-COMPATIBILITY.md")
PIN = "36503bda2d87465765e1b94e65f9d100f27ed5be"

AREAS = [
    ("process", r"^(clone|clone3|fork|vfork|execve|execveat|exit|exit_group|wait4|waitid|getpid|getppid|gettid|set_tid_address|prctl|arch_prctl|kill|tkill|tgkill|pidfd_|process_|sched_|setpriority|getpriority|nice|personality|unshare|setns|ptrace|rt_sig|sig|pause|restart_syscall|vhangup|modify_ldt|set_thread_area|get_thread_area|futex|set_robust_list|get_robust_list|membarrier|rseq|getrusage|times|setrlimit|getrlimit|prlimit64|getcpu|uname|sysinfo)"),
    ("memory", r"^(mmap|munmap|mprotect|mremap|msync|madvise|mincore|brk|mlock|munlock|mlock2|mlockall|munlockall|remap_file_pages|process_vm_|pkey_|mbind|set_mempolicy|get_mempolicy|migrate_pages|move_pages|memfd_|userfaultfd|cachestat|map_shadow_stack)"),
    ("files", r"^(read|write|open|openat|openat2|close|close_range|stat|fstat|lstat|newfstatat|statx|lseek|pread64|pwrite64|readv|writev|preadv|pwritev|preadv2|pwritev2|access|faccessat|faccessat2|dup|dup2|dup3|fcntl|flock|fsync|fdatasync|sync|syncfs|sync_file_range|truncate|ftruncate|getdents|getdents64|getcwd|chdir|fchdir|rename|renameat|renameat2|mkdir|mkdirat|rmdir|creat|link|linkat|unlink|unlinkat|symlink|symlinkat|readlink|readlinkat|chmod|fchmod|fchmodat|fchmodat2|chown|fchown|lchown|fchownat|umask|utime|utimes|utimensat|futimesat|mknod|mknodat|statfs|fstatfs|ustat|fadvise64|readahead|splice|tee|vmsplice|sendfile|copy_file_range|fallocate|name_to_handle_at|open_by_handle_at|getxattr|setxattr|listxattr|removexattr|lgetxattr|lsetxattr|llistxattr|lremovexattr|fgetxattr|fsetxattr|flistxattr|fremovexattr|inotify|fanotify|ioctl|poll|ppoll|select|pselect6|epoll|eventfd|signalfd|timerfd|pipe|pipe2|io_|mount|umount2|pivot_root|chroot|open_tree|move_mount|fsopen|fsconfig|fsmount|fspick|mount_setattr|quotactl|fsinfo|listmount|statmount|lookup_dcookie)"),
    ("network", r"^(socket|socketpair|bind|listen|accept|accept4|connect|shutdown|sendto|recvfrom|sendmsg|recvmsg|sendmmsg|recvmmsg|getsockname|getpeername|getsockopt|setsockopt)"),
    ("ipc", r"^(shmget|shmat|shmctl|shmdt|semget|semop|semctl|semtimedop|msgget|msgsnd|msgrcv|msgctl|mq_)"),
    ("time", r"^(time|gettimeofday|settimeofday|clock_|nanosleep|alarm|getitimer|setitimer|timer_|adjtimex|clock_adjtime)"),
    ("identity", r"^(getuid|geteuid|getgid|getegid|setuid|setgid|setreuid|setregid|setresuid|setresgid|getresuid|getresgid|setfsuid|setfsgid|getgroups|setgroups|setpgid|getpgid|getpgrp|setsid|getsid|capget|capset)"),
    ("security", r"^(seccomp|landlock_|bpf|keyctl|add_key|request_key|getrandom|perf_event_open|kexec|init_module|finit_module|delete_module|reboot|acct|syslog|ioperm|iopl|swapon|swapoff|sethostname|setdomainname|_sysctl|nfsservctl|afs_syscall|security|get_kernel_syms|query_module|create_module|getpmsg|putpmsg|vserver|tuxcall|uselib|lsm_)"),
]


def area_of(name: str) -> str:
    for area, pat in AREAS:
        if re.match(pat, name):
            return area
    return "other"


def parse_ledger() -> list[dict]:
    rows = []
    for line in LEDGER.read_text().splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*`?([A-Za-z0-9_]+)`?\s*\|\s*([A-Za-z-]+)\s*\|", line)
        if m:
            rows.append({"nr": int(m.group(1)), "name": m.group(2), "status": m.group(3), "area": area_of(m.group(2))})
    return rows


AGENT_LOOP = textwrap.dedent('''
    import json, os, signal, socket, subprocess, sys, select, mmap, time, threading
    base = sys.argv[1]
    cfg = json.loads(open(os.path.join(base, "config.json")).read())
    with open(os.path.join(base, "agent.log"), "a") as log:
        log.write("start\\n")
    srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen(1)
    port = srv.getsockname()[1]
    def serve():
        c, _ = srv.accept(); c.sendall(b"hello"); c.close()
    t = threading.Thread(target=serve); t.start()
    cli = socket.create_connection(("127.0.0.1", port))
    r, _, _ = select.select([cli], [], [], 2.0)
    data = cli.recv(16); cli.close(); t.join(); srv.close()
    got = []
    signal.signal(signal.SIGUSR1, lambda *a: got.append(1))
    os.kill(os.getpid(), signal.SIGUSR1)
    p = subprocess.run(["/bin/echo", "child"], capture_output=True, check=True)
    with open(os.path.join(base, "config.json"), "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ); _ = mm[:4]; mm.close()
    time.sleep(0.01)
    with open(os.path.join(base, "agent.log"), "a") as log:
        log.write(json.dumps({"data": data.decode(), "child": p.stdout.decode().strip(), "sig": len(got), "model": cfg["model"]}) + "\\n")
    os.fsync(os.open(os.path.join(base, "agent.log"), os.O_RDONLY))
''')


def trace_agent_loop() -> dict:
    with tempfile.TemporaryDirectory() as d:
        Path(d, "config.json").write_text(json.dumps({"model": "ThoxOS-Kernel-0.8B"}))
        script = Path(d, "loop.py")
        script.write_text(AGENT_LOOP)
        counts: Counter = Counter()
        for _ in range(3):  # three runs; take the union and the median count per syscall
            proc = subprocess.run(["strace", "-f", "-qq", "-o", str(Path(d, "trace.txt")), sys.executable, "-I", str(script), d],
                                  capture_output=True, text=True, check=True)
            for line in Path(d, "trace.txt").read_text().splitlines():
                m = re.match(r"^\d+\s+([a-z0-9_]+)\(", line)
                if m:
                    counts[m.group(1)] += 1
        log = Path(d, "agent.log").read_text().strip().splitlines()[-1]
    return {"syscalls": {k: v // 3 for k, v in counts.items()}, "last_log_line": log}


def main() -> int:
    rows = parse_ledger()
    if len(rows) != 375:
        raise SystemExit(f"expected 375 ledger rows, parsed {len(rows)}")
    totals = Counter(r["status"] for r in rows)
    by_area: dict[str, Counter] = {}
    for r in rows:
        by_area.setdefault(r["area"], Counter())[r["status"]] += 1
    traced = trace_agent_loop()
    ledger_by_name = {r["name"]: r for r in rows}
    joined = []
    for name, n in sorted(traced["syscalls"].items(), key=lambda kv: -kv[1]):
        rec = ledger_by_name.get(name)
        joined.append({"name": name, "calls": n, "status": rec["status"] if rec else "not-in-pinned-table",
                       "area": rec["area"] if rec else area_of(name)})
    loop_status = Counter(j["status"] for j in joined)
    loop_weighted = Counter()
    for j in joined:
        loop_weighted[j["status"]] += j["calls"]
    out = {"evidence_label": "Part A: observed upstream ledger at the pin, area classification by this paper; Part B: strace of a reference loop on the authoring host Linux, joined with ledger statuses; neither ran on ThoxInux",
           "pin": PIN, "ledger_totals": dict(totals), "by_area": {a: dict(c) for a, c in by_area.items()},
           "rows": rows, "traced_loop": joined, "loop_distinct_by_status": dict(loop_status),
           "loop_calls_by_status": dict(loop_weighted), "loop_last_log_line": traced["last_log_line"],
           "host": {"python": sys.version.split()[0]}}
    RESULTS.write_text(json.dumps(out, indent=2))
    print("totals", dict(totals))
    for a, c in by_area.items():
        print(f"{a:10s} {dict(c)}")
    print("loop distinct", dict(loop_status), "calls", dict(loop_weighted))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
