# scheduler.py
from crontab import CronTab
import os
import logging

class ScannerScheduler:
    def __init__(self, username=None):
        self.cron = CronTab(user=username)
        self.log_dir = os.path.join(os.path.dirname(__file__), 'cron_logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
    def add_job(self, scan_type, schedule, parameters=None):
        """Add a new cron job"""
        job = self.cron.new(
            command=self._build_command(scan_type, parameters),
            comment=f"SecurityScan::{scan_type}"
        )
        job.setall(schedule)
        self.cron.write()
        return job

    def _build_command(self, scan_type, parameters):
        """Build the command line for cron job"""
        base_cmd = f"python3 {os.path.join(os.path.dirname(__file__), 'scanner.py')}"
        log_file = os.path.join(self.log_dir, f"{scan_type}.log")
        
        commands = {
            'nmap': f"{base_cmd} --cron --nmap {parameters} >> {log_file} 2>&1",
            'lynis': f"{base_cmd} --cron --lynis >> {log_file} 2>&1",
            'bandit': f"{base_cmd} --cron --bandit {parameters} >> {log_file} 2>&1",
            'gobuster': f"{base_cmd} --cron --gobuster {parameters} >> {log_file} 2>&1"
        }
        return commands.get(scan_type, base_cmd)

    def list_jobs(self):
        """List all security scan jobs"""
        return [job for job in self.cron if job.comment.startswith('SecurityScan::')]

    def remove_job(self, scan_type=None, job_id=None):
        """Remove jobs by type or ID"""
        removed = 0
        for job in self.cron:
            if job.comment.startswith('SecurityScan::'):
                if scan_type and scan_type in job.comment or job_id and job.identifier == job_id:
                    self.cron.remove(job)
                    removed += 1
        self.cron.write()
        return removed

    def remove_all_jobs(self):
        """Remove all security scan jobs"""
        return self.remove_job(scan_type='SecurityScan')