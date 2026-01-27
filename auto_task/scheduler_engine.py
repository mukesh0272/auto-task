from __future__ import annotations

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import AppConfig
from .runner import run_task

log = logging.getLogger("auto_task.scheduler")


class SchedulerEngine:
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg
        self.scheduler = BackgroundScheduler()

    def start(self) -> None:
        for sched in self.cfg.schedules:
            task = self.cfg.tasks[sched.task]

            if sched.trigger == "cron":
                trigger = CronTrigger.from_crontab(sched.cron)  # 5-field crontab
                self.scheduler.add_job(
                    func=run_task,
                    trigger=trigger,
                    args=[task],
                    id=f"cron:{sched.task}:{sched.cron}",
                    replace_existing=True,
                    misfire_grace_time=30,
                    max_instances=1,
                )
                log.info("Scheduled task '%s' with cron '%s'", sched.task, sched.cron)

            elif sched.trigger == "interval":
                self.scheduler.add_job(
                    func=run_task,
                    trigger="interval",
                    seconds=sched.seconds,
                    args=[task],
                    id=f"interval:{sched.task}:{sched.seconds}",
                    replace_existing=True,
                    misfire_grace_time=30,
                    max_instances=1,
                )
                log.info("Scheduled task '%s' every %s seconds", sched.task, sched.seconds)

        self.scheduler.start()
        log.info("Scheduler started with %d jobs", len(self.scheduler.get_jobs()))

    def stop(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            log.info("Scheduler stopped")
