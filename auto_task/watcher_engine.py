from __future__ import annotations

import logging
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from .config import AppConfig, Watcher
from .runner import run_task
from .utils import Debouncer, abspath

log = logging.getLogger("auto_task.watcher")


class _Handler(PatternMatchingEventHandler):
    def __init__(self, watcher: Watcher, task, *args, **kwargs) -> None:
        super().__init__(
            patterns=watcher.patterns or ["*"],
            ignore_patterns=watcher.ignore_patterns or [],
            ignore_directories=False,
            case_sensitive=False,
        )
        self.watcher = watcher
        self.task = task
        self.debouncer = Debouncer(watcher.debounce_ms)

    def on_any_event(self, event):
        # We usually want to respond to modified/created/moved; ignore opened/closed noise
        et = getattr(event, "event_type", "")
        if et not in ("modified", "created", "moved", "deleted"):
            return

        if not self.debouncer.allow():
            return

        log.info("File event (%s) -> task '%s' | %s", et, self.task.name, getattr(event, "src_path", ""))
        run_task(self.task)


class WatcherEngine:
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg
        self.observer = Observer()

    def start(self) -> None:
        for w in self.cfg.watchers:
            task = self.cfg.tasks[w.task]
            handler = _Handler(w, task)
            watch_path = abspath(w.path)
            self.observer.schedule(handler, watch_path, recursive=w.recursive)
            log.info(
                "Watching '%s' (recursive=%s, debounce_ms=%s) -> task '%s'",
                watch_path, w.recursive, w.debounce_ms, w.task
            )

        self.observer.start()
        log.info("Watcher started")

    def stop(self) -> None:
        self.observer.stop()
        self.observer.join(timeout=5)
        log.info("Watcher stopped")
