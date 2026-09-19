"""Generate a random-looking GitHub contribution graph.

Creates backdated commits over the last N days inside this repository.
Run:  python generate.py [--days 365] [--seed 12345] [--min-per-day 1] [--dry-run]
"""

import argparse
import datetime as dt
import os
import random
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = "activity.log"

MESSAGES = [
    "chore: sync activity log",
    "chore: update log",
    "docs: refresh notes",
    "fix: small cleanup",
    "refactor: tidy up log format",
    "chore: bump activity",
    "style: format entry",
    "chore: daily log",
    "feat: add log entry",
    "chore: housekeeping",
    "docs: update readme",
    "chore: routine update",
    "fix: typo in log",
    "chore: append entry",
    "perf: minor tweak",
    "chore: log rotation",
]

REST_PROB = 0.38
COUNT_CHOICES = [1, 2, 3, 4, 5, 6, 8, 10]
COUNT_WEIGHTS = [30, 25, 16, 11, 8, 5, 3, 2]


def run(args, env=None):
    subprocess.run(
        ["git", *args],
        cwd=REPO,
        check=True,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def commit_at(when, message):
    stamp = when.strftime("%Y-%m-%d %H:%M:%S")
    env = dict(os.environ)
    env["GIT_AUTHOR_DATE"] = stamp
    env["GIT_COMMITTER_DATE"] = stamp
    run(["add", DATA_FILE], env=env)
    run(["commit", "-m", message], env=env)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--min-per-day", type=int, default=1)
    parser.add_argument("--rest-prob", type=float, default=REST_PROB)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else random.randrange(1, 10**9)
    rng = random.Random(seed)

    today = dt.date.today()
    start = today - dt.timedelta(days=args.days - 1)

    plan = []
    for offset in range(args.days):
        day = start + dt.timedelta(days=offset)
        if args.min_per_day <= 0 and rng.random() < args.rest_prob:
            count = 0
        else:
            count = rng.choices(COUNT_CHOICES, weights=COUNT_WEIGHTS, k=1)[0]
            if day == today and count > 3:
                count = 3
        count = max(count, args.min_per_day)
        plan.append((day, count))

    total = sum(c for _, c in plan)
    active = sum(1 for _, c in plan if c)
    peak = max(c for _, c in plan)
    print(f"seed       : {seed}")
    print(f"range      : {start} -> {today}")
    print(f"commits    : {total}")
    print(f"active days: {active}/{args.days}")
    print(f"busiest day: {peak} commits")

    if args.dry_run:
        return

    if not os.path.isdir(os.path.join(REPO, ".git")):
        run(["init", "-b", "main"])
        run(["config", "user.name", "Spavvvv"])
        run(["config", "user.email", "tiendat3157@gmail.com"])

    committed = 0
    for day, count in plan:
        if count == 0:
            continue
        seconds = sorted(rng.uniform(8 * 3600, 23.5 * 3600) for _ in range(count))
        for sec in seconds:
            when = dt.datetime(
                day.year,
                day.month,
                day.day,
                int(sec // 3600),
                int((sec % 3600) // 60),
                int(sec % 60),
            )
            with open(os.path.join(REPO, DATA_FILE), "a", encoding="utf-8") as handle:
                handle.write(f"{when:%Y-%m-%d %H:%M:%S} entry\n")
            commit_at(when, rng.choice(MESSAGES))
            committed += 1
            if committed % 50 == 0:
                print(f"  ... {committed}/{total}")

    print(f"done: {committed} commits created (seed {seed})")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.stderr.decode(errors="replace") if exc.stderr else str(exc))
