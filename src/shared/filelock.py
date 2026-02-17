"""크로스플랫폼 파일 락 — fcntl(Unix) / msvcrt(Windows) 자동 분기.

표준 라이브러리만 사용. feedback.py, error_analyzer.py에서 import하여 사용.
"""

import os

if os.name == "nt":
    # Windows
    import msvcrt

    def lock_exclusive(f) -> None:
        """배타적 잠금 (쓰기용)."""
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)

    def lock_shared(f) -> None:
        """공유 잠금 (읽기용). Windows에서는 배타적 잠금으로 대체."""
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)

    def unlock(f) -> None:
        """잠금 해제."""
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)

else:
    # Unix (macOS, Linux)
    import fcntl

    def lock_exclusive(f) -> None:
        """배타적 잠금 (쓰기용)."""
        fcntl.flock(f, fcntl.LOCK_EX)

    def lock_shared(f) -> None:
        """공유 잠금 (읽기용)."""
        fcntl.flock(f, fcntl.LOCK_SH)

    def unlock(f) -> None:
        """잠금 해제."""
        fcntl.flock(f, fcntl.LOCK_UN)
