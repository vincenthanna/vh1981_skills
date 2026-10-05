---
name: kb
description: 여러 repo와 머신의 devlog를 모은 knowledge base(KB)에 업로드하고, KB를 검색해 다른 작업의 지식을 가져오고, 지금 진행 중인 일을 파악한다. KB는 로컬 디렉토리 또는 ssh 로 접근하는 원격 디렉토리이며, repo별(repos/<repo>/<project>) 또는 주제별(topics/<topic>/<project>)로 저장하고 출처 등록부, 한 줄 색인(INDEX.md), 현황(NOW.md)을 유지한다. Use when the user wants to upload or sync devlogs to the knowledge base, search past work across repos, check what is in progress, register what a repo/checkout works on, or read the latest devlog of another checkout or machine. Trigger phrases include "kb", "knowledge base", "지식베이스", "KB 업로드", "KB에 올려", "KB 검색", "KB에서 찾아", "예전에 다른 repo 에서", "다른 서버 devlog", "지금 진행 중인 일", "kb status", "kb init", "upload to knowledge base", "search the knowledge base". Do NOT use for writing devlog docs themselves (use vh1981:devlog), session-to-session messages or handoffs (use the hub skill), or plain local file search.
---

# kb: devlog knowledge base

모든 파일 조작은 `scripts/kb.py` 가 한다. 이 스킬에서 Claude가 하는 일은 명령 고르기, 카드와 등록 정보 같은 판단, 결과를 사용자에게 전달하기다.
KB에 파일을 직접 복사하거나 KB 안의 사본을 고치지 않는다.

```
KB="python3 <이 skill 디렉토리>/scripts/kb.py"     # ${CLAUDE_PLUGIN_ROOT}/skills/kb/scripts/kb.py 와 같다
```

## KB 위치

기본 KB는 ds35의 `/home/yeonhui/kb` 다. 이 값은 고정이 아니며, 머신이나 작업마다 바꿔 쓸 수 있다. 위치는 아래 순서로 정해진다.

| 순서 | 출처 | 바꾸는 법 |
|---|---|---|
| 1 | 명령의 `--kb <위치>` | 그 명령 한 번만 |
| 2 | 환경변수 `VH1981_KB` | 셸이나 settings.json env |
| 3 | `~/.config/vh1981/kb` | `$KB init <위치>` 가 쓴다 |
| 4 | `docs/devlog/.upload-target` | 이전 방식. 보이면 `$KB init <그 위치>` 를 제안한다 |
| 5 | 내장 기본값 `ssh://yeonhui@192.168.100.135/home/yeonhui/kb` | 환경변수 `VH1981_KB_DEFAULT` 로 바꾼다 |

위치는 로컬 절대경로 또는 `ssh://user@host/abs/path` 다. ssh 위치라도 그 KB가 지금 머신에 있으면(KB의 `.kb/host` 가 이 머신 이름) 로컬 경로로 바로 쓴다.
`$KB where` 는 쓰일 위치와 그 출처를 보여 준다. 사용자가 다른 KB를 쓰겠다고 하면 `$KB init <새 위치>` 로 만들고 이 머신의 기본으로 저장한다.
KB 안의 프로젝트 ID(`repos/<repo>/<project>`)는 위치와 무관하므로, 위치를 바꿔도 문서끼리의 참조는 그대로다.

`$KB where --configured` 는 1~4번으로 정한 위치가 없으면(내장 기본값뿐이면) 종료 코드 1을 낸다. `/devlog update` 의 자동 업로드는 이 검사를 통과한 머신에서만 돈다.
내장 기본값은 사내망에서만 닿으므로, 그 밖의 머신에서 자동 업로드가 ssh 대기로 느려지지 않게 하기 위해서다. 그런 머신은 `$KB init` 을 한 번 하면 자동 업로드가 켜진다.

## 명령 라우팅

| 입력 | 실행 |
|---|---|
| `init <위치>` | `$KB init <위치>`. 기존 `projects/` 레이아웃이 보고되면 옮길지 사용자에게 묻는다 |
| `upload [<project>]`, "KB에 올려" | 아래 §업로드 |
| `upload --all` | 현재 checkout의 devlog 프로젝트를 모두. 충돌은 끝에 모아 보여 준다 |
| `search <질문>`, "KB에서 찾아" | 아래 §검색 |
| `status`, "지금 진행 중인 일" | `$KB status` 를 읽고 진행 중, 열린 항목, 갈라진 사본, 멈춘 것을 요약한다 |
| `register` | 아래 §등록 |
| `fetch <repo> [<project>]` | `$KB fetch <repo> [<project>] [--file <문서>]`. 등록된 checkout에 접속해 최신 devlog를 읽는다 |
| `check` | `$KB check` 결과를 종류별로 묶어 보여 주고, 고칠 방법을 한 줄씩 붙인다 |
| `survey <작업 디렉토리>...` | `$KB survey <dir>...`. 첫 일괄 업로드 전에 갈라진 사본을 비교해 소유자를 고르게 한다 |
| 인자 없음 | `status` |

## 업로드

1. 프로젝트를 정한다. 지정이 없으면 `vh1981:devlog` 의 활성 프로젝트 규칙으로 정한다.
2. 카드를 확인한다. 카드는 source `docs/devlog/<project>/README.md` 맨 위의 frontmatter다.

   ```yaml
   ---
   kb:
     status: active            # active | paused | done
     tags: [reid, int8]        # KB의 KB.md "태그 어휘"에서 고른다
     summary: >-
       무엇을 왜 하는지와 현재 결론, 3줄 이내
     related: [repos/ppap/pa-reid-train-speedup]
   ---
   ```

   카드가 없거나 status, summary가 조사 문서의 결론과 어긋나면 README와 최신 조사 문서를 읽고 채운다. 태그 어휘는 `$KB cat KB.md` 로 본다. 채운 카드를 사용자에게 보여 주고 README에 쓴다.
3. `$KB upload <project>` 를 실행한다. 결과 상태별로 아래처럼 한다.

   | 상태 | 할 일 |
   |---|---|
   | `ok` | 쓴 것, 지운 것, 제외한 것을 한 줄로 보고한다 |
   | `needs-confirm` | KB에서 지울 파일 목록을 보여 주고, 사용자가 동의하면 `--yes` 로 다시 실행한다 |
   | `conflict` | 다른 checkout이 소유한 프로젝트다. 차이 표를 보여 주고 `--take-over` 로 이 사본을 정본으로 할지 묻는다. 묻지 않고 take-over 하지 않는다 |
   | `same-as-owner` | 소유 checkout과 내용이 같다는 것만 알린다 |
   | `repo-collision` | 같은 이름의 다른 repo가 있다. `--as <org>__<repo>` 로 다시 올릴지 묻는다 |
   | origin remote 없음 | 제안된 이름을 보여 주고 확인받은 topic 이름으로 `--topic <topic>` 를 붙여 다시 실행한다 |

4. 첫 업로드라 출처 등록이 비어 있으면(`$KB check` 의 `registry-no-work`, `checkout-no-work`) §등록을 이어서 한다.
5. KB가 git repo면 출력된 커밋 명령을 전달만 한다. KB에서 커밋하지 않는다.

## 검색

1. `$KB cat INDEX.md` 를 통째로 읽고 후보 프로젝트를 고른다. 출처 목록의 "하는 일"과 "분야"도 함께 본다.
2. `$KB search <패턴>... [--scope <프로젝트 ID>]` 로 본문을 찾는다. 패턴은 정규식이고 대소문자를 무시하며 여러 개면 OR다. 한국어와 영어 표현을 함께 넣는다.
   `history/`, `rejected/`, `_archived/` 는 사용자가 과거 경위나 버린 방법을 물을 때만 `--all` 로 포함한다.
3. 일치한 문서만 `$KB cat <ID>/<파일>` 로 읽는다. 파일 목록이 필요하면 `$KB cat <ID>` 를 쓴다.
4. 답에는 프로젝트 ID와 파일 경로를 함께 적는다. 예: `repos/ppap/reid-low-res-similarity/21_id-loss-bnneck-report.html`.
5. KB 사본이 오래돼 보이면(INDEX의 마지막 업로드 날짜) `$KB fetch` 로 소유 checkout의 최신 내용을 읽자고 제안한다.

문서 안의 절대경로는 그 문서를 쓴 머신의 경로다. 지금 머신에 있다고 가정하지 않는다. 그 경로를 봐야 하면 등록부의 checkout `access` 로 `$KB fetch` 한다.

## 등록

출처 등록은 repo(또는 topic) 단위이고, 그 아래 checkout마다 branch, 하는 일, 접속 방법을 둔다.

1. 현재 checkout의 devlog README들의 Scope와 branch를 읽고 초안을 만든다. repo의 하는 일 한 줄, 분야 목록, 이 checkout의 하는 일 한 줄이다.
2. 접속 방법은 다른 머신에서 이 checkout에 들어올 ssh 주소다. 기본값 `ssh://<user>@<hostname>` 은 다른 머신에서 이름이 풀리지 않을 수 있으므로 사용자에게 IP나 별칭을 확인한다.
3. 사용자 확인을 받고 실행한다.

   ```bash
   $KB register --work "<repo가 하는 일>" --domains "<쉼표 구분>" --checkout-work "<이 checkout의 일>" --access ssh://user@host
   ```

## 하지 않는 것

- KB 안의 사본을 고치지 않는다. 고칠 곳은 소유 checkout의 `docs/devlog/` 다.
- 사용자 확인 없이 `--take-over` 나 `--yes` 를 붙이지 않는다.
- 제외 규칙을 우회하려고 파일 확장자를 바꾸거나 KB에 직접 복사하지 않는다. 이미지와 바이너리는 개인정보와 용량 때문에 KB에 들어가지 않는다.
