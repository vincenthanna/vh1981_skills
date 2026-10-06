---
name: kb-report
description: knowledge base(KB)에 등록된 모든 repo·작업 디렉토리에서 어제(또는 지정한 날, 지정한 주) 진행한 일을 수집해 단일 HTML daily log / weekly log 로 정리하고, KB를 루트로 하는 웹 서버에 최신순으로 올린다. KB가 있는 머신의 cron이 매일 06:30(daily)과 일요일 22:00(weekly)에 KB 디렉토리에서 headless claude로 이 스킬을 실행하며, install 명령이 그 cron을 설치한다. Use when the user wants the daily or weekly work log built or rebuilt, wants to see what was done on a given day or week across all repos as a page, or wants to install, check or remove the daily/weekly log cron. Trigger phrases include "kb-report", "daily log", "weekly log", "일일 로그", "주간 로그", "어제 한 일 정리", "이번 주 한 일 정리", "데일리 로그 만들어", "주간 보고 페이지", "daily log cron 설치". Do NOT use for a plain text list of dated entries (use `kb log` in the vh1981:kb skill), for writing devlog docs (use vh1981:devlog), or for a technical report on one topic (use vh1981:techreport).
---

# kb-report: daily / weekly log

KB에 등록된 checkout들에서 기간의 작업을 모아 사람이 읽는 단일 HTML로 만든다. 수집은 `kb.py collect` 가 하고, Claude는 그 결과를 읽고 요약해 페이지를 쓴다.
이 스킬은 KB가 있는 머신에서 KB 디렉토리를 작업 디렉토리로 하여 실행한다. cron이 띄운 무인 실행이면 질문하지 않고 끝까지 간다.

```
KBDIR=<KB 디렉토리>                          # cron 실행이면 현재 작업 디렉토리
KB="python3 $KBDIR/.kb/bin/kb.py"            # install.sh 가 복사해 둔 kb.py. 무인 실행은 이 경로만 허용된다
```

무인 실행에서 허용된 도구는 `python3 $KBDIR/.kb/bin/kb.py ...`, `bash $KBDIR/.kb/bin/serve_devlog.sh ...`, Read, Write, Edit, Glob, Grep뿐이다. `cp`, `mkdir`, `ssh` 같은 다른 명령은 쓰지 않는다. 템플릿은 Read로 읽고 Write로 쓴다.

## 명령 라우팅

| 입력 | 동작 |
|---|---|
| `daily [YYYY-MM-DD]` | 그날(기본: 어제)의 daily log. 아래 §daily |
| `weekly [YYYY-MM-DD]` | 그날로 끝나는 7일(기본: 오늘까지)의 weekly log. 아래 §weekly |
| `install [KB 디렉토리]` | KB 머신에서 `bash <이 skill 디렉토리>/scripts/install.sh [KB 디렉토리]`. cron, 서버, 실행 파일을 설치한다 |
| `uninstall` | `bash <이 skill 디렉토리>/scripts/install.sh --uninstall` |
| `status` | `$KBDIR/.kb/logs/kb-report.log` 의 마지막 20줄과 `reports/daily`, `reports/weekly` 의 최신 파일을 보여 준다 |

KB가 지금 머신에 없으면(`kb.py where` 가 `ssh://` 를 내면) 직접 만들지 않는다. KB 머신에서 실행하는 명령을 안내한다: `ssh <host> <KB 디렉토리>/.kb/bin/kb-report-run.sh daily <날짜>`.

## daily

1. 날짜 `D` 를 정한다. 인자가 없으면 어제다.
2. 수집한다.

   ```bash
   $KB collect --since D --until D --out $KBDIR/reports/.data/daily-D.json
   ```

3. JSON을 Read로 읽는다. checkout마다 `via`(live-local, live-ssh, kb-copy), `entries`(날짜 규칙으로 기록된 Done·history·Finding 항목), `modified`(그날 수정된 devlog 문서), `commits`(그 checkout 사용자의 그날 커밋)가 있다.
4. 활동한 checkout마다 무슨 일을 했는지 파악한다.
   - `entries` 와 `commits` 가 1차 근거다. 항목 문장을 결과의 말로 다듬어 쓴다.
   - `entries` 가 비어 있고 `modified` 만 있으면, 그 문서를 열어 그날 바뀐 부분을 확인한다. `via` 가 live-local이면 checkout 경로를 Read로, 그 밖이면 `$KB cat <KB ID>/<파일>` 로 읽는다. 문서를 하루에 8개 넘게 열지 않는다.
   - README 맨 위의 `kb:` 카드만 바뀐 경우처럼 내용이 없는 수정은 "문서 정리"로 한 줄만 쓰거나 생략한다.
   - 같은 프로젝트를 여러 checkout이 보고하면 소유 checkout(`projects` 에 들어 있는 쪽)의 내용을 쓰고, 사본 쪽은 다른 내용이 있을 때만 덧붙인다.
5. `<이 skill 디렉토리>/templates/log.html` 을 Read로 읽고, 채워서 `$KBDIR/reports/daily/D.html` 로 Write한다.
   - 제목은 `Daily log D (요일)`, 부제는 날짜와 수집 시각이다.
   - 요약 3~5문장, KPI 3개(활동한 프로젝트, 기록된 항목, 커밋), 활동 분포 그림, 프로젝트별 카드, 수집 범위 상자, footer를 채운다. 템플릿의 weekly 전용 주석 블록은 지운다.
   - 활동 분포 그림은 템플릿 주석의 좌표 규칙대로 인라인 SVG 막대를 그린다. 숫자는 JSON의 `entries`, `modified`, `commits` 개수 그대로이고, 그림 안에 적는다. figcaption에는 그림에서 읽을 결론 한 줄을 쓴다. 활동이 없으면 그림을 빼고 그 사실만 쓴다.
   - 프로젝트 카드 안에서도 흐름이나 전후 비교가 핵심이면 작은 표나 SVG를 더한다. 원칙은 `output-principles.md` 를 따른다. 무인 실행에서는 `<이 skill 디렉토리>/output-principles.md` (install.sh 가 복사한 사본), 대화 세션에서는 `${CLAUDE_PLUGIN_ROOT}/guidelines/output-principles.md` 다.
   - 프로젝트 카드는 활동이 많은 순서로 둔다. 카드의 각 줄 끝에 근거 파일이나 커밋 SHA를 적는다. live로 수집했으면 `LIVE`, KB 사본으로만 봤으면 `KB 사본` 태그를 단다.
   - 활동이 하나도 없으면 페이지를 그래도 만든다. 요약에 "기록된 활동이 없다"고 쓰고, 수집 범위 상자에 확인한 checkout 수를 쓴다.
6. 서버를 확인한다: `bash $KBDIR/.kb/bin/serve_devlog.sh $KBDIR 8800`. 이미 떠 있으면 그대로 두고, 새 페이지는 1분 안에 색인에 나타난다.
7. 결과를 두세 줄로 보고한다: 만든 파일, 활동한 프로젝트 수, 서버 주소.

## weekly

1. 끝날 `E` 를 정한다(기본: 오늘). 시작 `S` 는 `E` 의 6일 전이다. ISO 주 번호 `YYYY-Www` 는 `E` 기준이다.
2. 수집한다.

   ```bash
   $KB collect --since S --until E --out $KBDIR/reports/.data/weekly-YYYY-Www.json
   ```

3. 그 주의 daily log가 있으면(`$KBDIR/reports/daily/` 의 S~E 파일) 요약 부분을 읽어 참고한다. 없는 날은 JSON만 쓴다.
4. `$KB cat NOW.md` 로 열린 Critical/High 항목을 읽는다.
5. 템플릿으로 `$KBDIR/reports/weekly/YYYY-Www.html` 을 쓴다.
   - 제목은 `Weekly log YYYY-Www`, 부제는 `S ~ E` 다.
   - 요약은 그 주의 큰 흐름 3~5문장이다. 프로젝트 카드는 날짜별 나열이 아니라 그 주에 달라진 것(끝난 일, 내린 결정, 막힌 일) 위주로 쓴다.
   - 활동 분포는 날짜 7칸의 세로 막대(그날 기록 항목 + 커밋 수)로 그리고, 그 아래에 프로젝트별 가로 막대를 둔다.
   - weekly 전용 블록 두 개를 살린다. "다음으로 넘어가는 일"에는 NOW.md의 열린 항목 중 그 주에 활동한 프로젝트 것만 넣는다. "이 주의 daily log"에는 있는 daily 페이지 링크를 `/d/reports/daily/<날짜>` 형식으로 넣는다.
6. daily의 6, 7단계와 같다.

## 쓰는 규칙

- 사실은 수집 JSON과 실제로 연 문서에서만 가져온다. 없는 결과, 숫자, 날짜를 만들지 않는다. 확실하지 않은 줄은 빼거나 "추정"이라고 쓴다.
- 읽는 사람은 이 일을 하는 본인이다. 기술 용어는 그대로 쓰되 문장은 짧게 쓴다. 장식 이모지와 em dash를 쓰지 않는다.
- 이미지, 데이터 URI, 외부 CDN, 외부 폰트를 넣지 않는다. 페이지는 파일 하나로 끝난다. 서버는 이미지가 내장된 HTML을 잠근다.
- 다른 머신의 절대경로는 그대로 적되, 링크로 만들지 않는다.
- 이미 있는 같은 날짜 파일은 덮어쓴다. daily를 다시 만들면 그날 페이지가 갱신된다.

## 설치되는 것

`install.sh` 는 KB 머신에서 한 번 실행한다. 다시 실행해도 같은 결과가 된다.

| 대상 | 내용 |
|---|---|
| `$KBDIR/.kb/bin/` | `kb.py`, `serve_devlog.py`, `serve_devlog.sh`, `kb-report-run.sh` 복사본. cron은 플러그인 캐시 경로가 아니라 이 복사본을 부른다 |
| `$KBDIR/.kb/kb-report/` | 이 스킬의 `SKILL.md`, `templates/log.html`, 작성 원칙 `output-principles.md` 복사본. 무인 실행은 플러그인 버전과 상관없이 이 사본을 따른다 |
| `$KBDIR/.kb/claude-path` | 쓸 claude 경로. 버전 2 이상이고 `~/.local/bin/claude` 를 먼저 고른다 |
| crontab | `30 6 * * *` daily, `0 22 * * 0` weekly, `15 1,13 * * *` techdoc(`vh1981:kb-techdoc`), `@reboot` 서버. 줄 끝에 `# vh1981-kb-report` 표시가 있다 |
| `$KBDIR/.kb/kb-techdoc/` | kb-techdoc 스킬, techreport 스킬(본문, 템플릿, 검사 목록), 작성 원칙의 사본 |
| 서버 | `serve_devlog.sh <KB> 8800`. KB 루트에서는 Daily log, Tech docs, Weekly log를 최신순으로, 이어서 KB 프로젝트의 HTML 보고서를 보여 준다 |

시간과 포트는 `install.sh` 실행 전에 `KB_REPORT_PORT` 로, claude 경로는 `KB_REPORT_CLAUDE` 로 바꾼다. cron 시각을 바꾸려면 crontab의 표시된 줄을 고친다.
플러그인을 업데이트한 뒤에는 `install.sh` 를 다시 실행해 `.kb/bin` 의 복사본을 맞춘다.
