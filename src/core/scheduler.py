"""Scheduler 레이어 — 비동기 작업 추적 + 상태 관리.

async_runner.py가 실행하는 백그라운드 작업의 상태를 추적한다.
작업 등록/조회/완료 처리를 제공하며, JSONL 버스에 이벤트를 기록한다.
"""

import json
import time
from pathlib import Path

from src.shared.config import PROJECT_ROOT
from src.shared.filelock import lock_exclusive, lock_shared, unlock

_JOBS_PATH = PROJECT_ROOT / ".scheduler_jobs.json"


def _load_jobs() -> dict:
    """작업 상태 파일을 로드한다 (공유 락)."""
    if not _JOBS_PATH.exists():
        return {"jobs": {}}
    try:
        with open(_JOBS_PATH, "r", encoding="utf-8") as f:
            lock_shared(f)
            try:
                return json.load(f)
            finally:
                unlock(f)
    except (json.JSONDecodeError, IOError):
        return {"jobs": {}}


def _save_jobs(data: dict) -> None:
    """작업 상태 파일을 저장한다 (배타적 락)."""
    with open(_JOBS_PATH, "w", encoding="utf-8") as f:
        lock_exclusive(f)
        try:
            json.dump(data, f, ensure_ascii=False, indent=2)
        finally:
            unlock(f)


def register_job(job_id: str, job_type: str, target_agent: str,
                 metadata: dict | None = None) -> dict:
    """새 비동기 작업을 등록한다.

    Returns:
        등록된 작업 정보 dict
    """
    data = _load_jobs()
    job = {
        "job_id": job_id,
        "job_type": job_type,
        "target_agent": target_agent,
        "status": "pending",
        "created_at": time.time(),
        "completed_at": None,
        "metadata": metadata or {},
    }
    data["jobs"][job_id] = job
    _save_jobs(data)
    return job


def complete_job(job_id: str, result_summary: str = "") -> bool:
    """작업을 완료 상태로 변경한다.

    Returns:
        True: 성공, False: 작업을 찾지 못함
    """
    data = _load_jobs()
    if job_id not in data["jobs"]:
        return False
    data["jobs"][job_id]["status"] = "completed"
    data["jobs"][job_id]["completed_at"] = time.time()
    if result_summary:
        data["jobs"][job_id]["result_summary"] = result_summary
    _save_jobs(data)
    return True


def fail_job(job_id: str, error: str = "") -> bool:
    """작업을 실패 상태로 변경한다."""
    data = _load_jobs()
    if job_id not in data["jobs"]:
        return False
    data["jobs"][job_id]["status"] = "failed"
    data["jobs"][job_id]["completed_at"] = time.time()
    if error:
        data["jobs"][job_id]["error"] = error
    _save_jobs(data)
    return True


def get_job(job_id: str) -> dict | None:
    """특정 작업의 상태를 조회한다."""
    data = _load_jobs()
    return data["jobs"].get(job_id)


def list_jobs(status: str | None = None) -> list:
    """작업 목록을 반환한다. status 필터 가능."""
    data = _load_jobs()
    jobs = list(data["jobs"].values())
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    return sorted(jobs, key=lambda j: j.get("created_at", 0), reverse=True)


def cleanup_old_jobs(max_age_seconds: int = 86400) -> int:
    """오래된 완료/실패 작업을 정리한다.

    Returns:
        정리된 작업 수
    """
    data = _load_jobs()
    now = time.time()
    to_remove = []
    for job_id, job in data["jobs"].items():
        if job["status"] in ("completed", "failed"):
            completed_at = job.get("completed_at", 0)
            if now - completed_at > max_age_seconds:
                to_remove.append(job_id)
    for job_id in to_remove:
        del data["jobs"][job_id]
    if to_remove:
        _save_jobs(data)
    return len(to_remove)


def summarize_jobs() -> dict:
    """작업 현황 요약을 반환한다."""
    data = _load_jobs()
    jobs = data["jobs"]
    by_status = {}
    by_target = {}
    for job in jobs.values():
        s = job["status"]
        by_status[s] = by_status.get(s, 0) + 1
        t = job.get("target_agent", "unknown")
        by_target[t] = by_target.get(t, 0) + 1
    return {
        "total": len(jobs),
        "by_status": by_status,
        "by_target": by_target,
    }
