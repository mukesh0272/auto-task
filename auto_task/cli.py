from __future__ import annotations

import argparse
import logging
import signal
import sys
import time

from .config import load_config
from .scheduler_engine import SchedulerEngine
from .utils import read_json_file, setup_logging
from .watcher_engine import WatcherEngine

log = logging.getLogger("auto_task.cli")


def _cmd_run(args: argparse.Namespace) -> int:
    raw = read_json_file(args.config)
    cfg = load_config(raw)

    setup_logging(cfg.log_level)
    log.info(
        "Loaded config: tasks=%d schedules=%d watchers=%d",
        len(cfg.tasks),
        len(cfg.schedules),
        len(cfg.watchers),
    )

    scheduler = SchedulerEngine(cfg)
    watcher = WatcherEngine(cfg)

    stop = {"flag": False}

    def _handle(_sig, _frame):
        stop["flag"] = True

    signal.signal(signal.SIGINT, _handle)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle)

    scheduler_started = False
    watcher_started = False

    # Start engines
    if cfg.schedules:
        scheduler.start()
        scheduler_started = True
    if cfg.watchers:
        watcher.start()
        watcher_started = True

    if not cfg.schedules and not cfg.watchers:
        log.error("Nothing to do: no schedules or watchers configured.")
        return 2

    try:
        while not stop["flag"]:
            time.sleep(0.2)
    finally:
        # Stop only what we started. (watchdog's Observer is a thread; joining an
        # unstarted thread can raise RuntimeError.)
        if watcher_started:
            try:
                watcher.stop()
            except Exception:
                log.exception("Failed to stop watcher cleanly")

        if scheduler_started:
            try:
                scheduler.stop()
            except Exception:
                log.exception("Failed to stop scheduler cleanly")

    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="auto-task", description="Local automation: cron scheduling + file watching")
    sub = parser.add_subparsers(dest="command", required=True)

    runp = sub.add_parser("run", help="Run scheduler + watcher from a JSON config")
    runp.add_argument("config", help="Path to config JSON file (e.g. config.json)")
    runp.set_defaults(func=_cmd_run)

    args = parser.parse_args(argv)
    code = int(args.func(args))
    sys.exit(code)
