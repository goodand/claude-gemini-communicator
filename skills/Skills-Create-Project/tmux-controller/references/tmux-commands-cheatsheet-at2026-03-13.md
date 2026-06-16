# tmux 커맨드 치트시트

## 세션 관리

```bash
tmux new-session -d -s myapp           # 백그라운드 세션 생성
tmux list-sessions                      # 세션 목록
tmux kill-session -t myapp              # 세션 종료
tmux has-session -t myapp 2>/dev/null   # 세션 존재 확인
```

## 앱 실행/중지

```bash
tmux send-keys -t myapp "python app.py" Enter    # 앱 실행
tmux send-keys -t myapp C-c                       # 앱 중지 (Ctrl+C)
tmux send-keys -t myapp "python app.py" Enter    # 재시작
```

## 로그 캡처

```bash
tmux capture-pane -t myapp -p                     # 현재 화면 캡처
tmux capture-pane -t myapp -p -S -100             # 최근 100줄 캡처
tmux capture-pane -t myapp -p -S - -E -           # 전체 히스토리 캡처
```

## 윈도우/패인 분할

```bash
tmux split-window -t myapp -v                     # 수평 분할
tmux split-window -t myapp -h                     # 수직 분할
tmux send-keys -t myapp:0.1 "tail -f app.log" Enter  # 하단 패인에서 로그
```

## 출력 파일 저장

```bash
tmux pipe-pane -t myapp "cat >> /tmp/myapp.log"   # 전체 출력 파일 저장
tmux pipe-pane -t myapp                            # 파이프 해제
```

## 디버깅 패턴

### 패턴 1: 서버 재시작 루프
```bash
tmux send-keys -t myapp C-c                        # 중지
# ... 코드 수정 ...
tmux send-keys -t myapp "python app.py" Enter      # 재시작
sleep 2
tmux capture-pane -t myapp -p -S -50               # 로그 확인
```

### 패턴 2: 멀티 서비스 동시 모니터링
```bash
tmux new-session -d -s stack
tmux send-keys -t stack "docker compose up" Enter
tmux split-window -t stack -v
tmux send-keys -t stack:0.1 "tail -f backend.log" Enter
```

### 패턴 3: 장시간 프로세스 감시
```bash
tmux pipe-pane -t myapp "cat >> /tmp/full.log"
# ... 시간 경과 후 ...
tail -100 /tmp/full.log                            # 최근 로그만 확인
```

### 패턴 4: 격리된 소켓으로 안전 운용
```bash
tmux -S /tmp/ai-agent.sock new-session -d -s isolated
tmux -S /tmp/ai-agent.sock send-keys -t isolated "command" Enter
tmux -S /tmp/ai-agent.sock capture-pane -t isolated -p
tmux -S /tmp/ai-agent.sock kill-server              # 완전 정리
```

## 주의사항

| 항목 | 설명 |
|------|------|
| 세션 이름 | 점(`.`) 사용 금지 — tmux가 소켓으로 해석 |
| send-keys | 반드시 `Enter` 키 포함 |
| capture-pane | 현재 화면만 캡처 → `-S -N`으로 범위 지정 |
| 패인 번호 | 0부터 시작 (`session:window.pane`) |
| 격리 소켓 | `-S` = 소켓 경로, `-L` = 소켓 이름 (혼용 주의) |
| wait-for | echo된 명령 자체가 매치되지 않도록 프로그램 출력 기준으로 대기 |
