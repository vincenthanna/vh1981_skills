---
name: kb-techdoc
description: knowledge base(KB)에 쌓인 devlog를 훑어 기술문서로 만들 가치가 있는 프로젝트를 골라, KB 내용에 기초 논문과 외부 자료를 더한 단일 HTML 기술 보고서(용어집, 검증된 논문 요약과 링크, 검증 기록 포함)를 만들고 KB 웹 서버의 Tech docs에 올린다. KB가 있는 머신의 cron이 12시간마다 KB 디렉토리에서 headless claude로 실행하며, 한 번에 한 편을 만든다. Use when the user wants technical documents generated from accumulated KB devlogs, wants to see or refresh the candidate list, or wants a tech doc for a specific KB project. Trigger phrases include "kb-techdoc", "KB 기술문서", "기술문서 자동 생성", "devlog 로 기술문서", "tech docs 만들어", "기술문서 후보". Do NOT use for a report on the current session's own work (use vh1981:techreport), the daily/weekly work log (use vh1981:kb-report), or editing devlog docs.
---

# kb-techdoc: KB에서 기술문서 만들기

KB의 프로젝트 문서는 작업 기록이라 그 분야를 모르는 사람이 읽기 어렵다. 이 스킬은 그중 쓸 만한 지식을 골라, 외부의 기초 논문과 자료를 붙여 혼자 읽히는 기술문서로 다시 쓴다.
문서 형식과 품질 기준은 전부 techreport 스킬을 따른다. 이 스킬이 더하는 것은 후보 선정, KB 문서 읽기, 외부 자료 조사, 결과 기록이다.

```
KBDIR=<KB 디렉토리>                         # cron 실행이면 현재 작업 디렉토리
KB="python3 $KBDIR/.kb/bin/kb.py"
TR=<이 skill 디렉토리>/techreport           # techreport 스킬 사본: SKILL.md, templates/report.html, reference/checklist.md
```

무인 실행에서 허용된 도구는 `$KB ...`, `bash $KBDIR/.kb/bin/serve_devlog.sh ...`, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch뿐이다. 다른 셸 명령은 쓰지 않는다.
대화 세션에서는 techreport 스킬 본문이 `${CLAUDE_PLUGIN_ROOT}/skills/techreport/` 에 있다.

## 명령 라우팅

| 입력 | 동작 |
|---|---|
| 인자 없음, `run` | 후보 하나를 골라 기술문서 한 편을 만든다(아래 §절차). cron이 이렇게 부른다 |
| `<KB 프로젝트 ID>` | 그 프로젝트로 바로 만든다. 가치 판단(2단계)은 건너뛴다 |
| `list` | `$KB candidates` 를 보여 준다 |
| `install` | `vh1981:kb-report` 의 `install.sh` 를 실행한다. KB 머신의 cron(daily, weekly, techdoc 12시간)을 함께 설치한다 |

## 절차

### 1. 후보 고르기

```bash
$KB candidates --json --limit 5
```

후보는 md 문서가 3개 이상이고, 지난번 처리(만듦 또는 건너뜀) 이후 새로 업로드된 프로젝트다. 점수가 높은 순서로 하나씩 2단계를 본다. 한 번 실행에 기술문서는 **한 편만** 만든다. 후보가 없으면 그 사실만 보고하고 끝낸다.

### 2. 만들 가치가 있는지 판단

`$KB cat <ID>` 로 파일 목록을 보고, README와 조사 문서를 읽는다. 문서는 KB 디렉토리 안(`$KBDIR/<ID>/`)에 있으므로 Read로 바로 읽는다. `history/` 는 읽지 않는다.

아래를 모두 만족하면 만든다.

- 근거가 있는 결론이 하나 이상 있다(측정값, 재현한 결과, 코드로 확인한 기전).
- 그 프로젝트 밖의 사람에게도 쓸모 있는 지식이다(원리, 방법, 교훈, 비교).
- 기초 개념을 외부 자료로 설명할 수 있다.

운영 기록, 할 일 목록, 아직 결론 없는 초기 조사는 만들지 않는다. 그런 경우 이유를 한 줄로 남기고 다음 후보로 간다.

```bash
$KB mark <ID> skipped --reason "<한 줄 이유>"
```

이미 만든 적이 있는 프로젝트가 다시 후보가 되면(새 업로드), 같은 파일을 새 내용으로 다시 쓴다.

### 3. 문서 설계

쓰기 전에 아래를 정한다.

- 이 문서가 답하는 질문 한 문장.
- 읽는 사람은 그 분야를 모르는 개발자다. 0장의 비유와 그 비유가 깨지는 지점.
- 절 구성. techreport의 순서(00 쉬운 설명, 01 한 장 요약, 본문, 실행 계획, 검증 기록, 참고 문헌, 용어집)를 따른다.
- 그림 4~8개의 목록. 각 그림이 없으면 읽는 사람이 무엇을 놓치는지 한 줄씩.

### 4. 외부 자료 붙이기

KB 내용만으로 쓰지 않는다. 문서의 기초 개념마다 근거가 되는 논문과 자료를 찾아 붙인다.

- WebSearch로 핵심 개념의 원 논문, 대표 논문, 공식 문서를 찾는다. 논문은 2~6편이 보통이다.
- arXiv 논문은 techreport §5 대로 API로 번호와 제목을 직접 확인한다. 제목이 일치한 것만 싣는다.

  ```
  WebFetch https://export.arxiv.org/api/query?id_list=<쉼표로 나열>&max_results=30
  ```

- arXiv가 아닌 자료(공식 문서, 표준, 위키백과)는 WebFetch로 실제로 열리는지 확인하고 싣는다.
- 참고 문헌 항목마다 제목, 저자나 출처, 링크, 3~4줄 요약, "이 문서에서 어디에 썼는지" 한 줄을 쓴다. 본문에는 `<sup class="c"><a href="#r3">[3]</a></sup>` 로 단다.
- KB 문서의 주장과 외부 자료가 다르면 둘 다 적고, 어느 쪽이 이 프로젝트의 측정으로 확인됐는지 밝힌다.

### 5. 쓰기

`$TR/SKILL.md` 를 읽고 그대로 따른다. 다만 techreport의 저장 위치(devlog 프로젝트 안)와 호스팅 절(§6, §8의 9단계)은 이 스킬의 5단계와 7단계로 대신하고, 질문하지 않는다. `$TR/templates/report.html` 을 Read로 읽어 채우고 아래 경로에 Write한다.

```
$KBDIR/reports/techdocs/<ID의 / 를 __ 로 바꾼 이름>.html     # 예: repos__plusinsight__barrier-aware-clustering.html
```

- 용어집을 이해하는 순서로 채우고, 본문에서 처음 나오는 용어에 팝업 링크를 단다. 팝업 문구는 따로 쓰지 않는다.
- 검증 기록 절에 KB 문서의 주장 중 직접 확인한 것, 확인하지 못한 것(미검증), 외부 자료와 어긋난 것을 표로 남긴다. 무인 실행에서는 코드를 다시 돌릴 수 없으므로, 확인 수단은 KB 문서 안의 측정 기록과 외부 자료다.
- 머리말에 출처를 적는다: KB 프로젝트 ID, 읽은 문서 목록, 생성 날짜, "KB devlog와 외부 자료를 바탕으로 자동 생성" 문구.
- 문체와 그림은 `output-principles.md` 를 따른다(무인 실행이면 `<이 skill 디렉토리>/output-principles.md`). 이미지와 외부 CDN은 쓰지 않는다.

### 6. 검사

```bash
$KB htmlcheck $KBDIR/reports/techdocs/<파일>.html
```

`ok` 가 `true` 가 될 때까지 고친다. 끊긴 앵커, 없는 인용, 쓰지 않은 참고문헌, 이미지, 남은 `{{` 자리표시자, 외부 스크립트, 스크립트 문법 오류가 검사 대상이다. `info.domains` 에는 참고 문헌으로 실은 사이트만 있어야 한다. `$TR/reference/checklist.md` 의 눈으로 보는 항목도 확인한다.

### 7. 기록과 게시

```bash
$KB mark <ID> made --file reports/techdocs/<파일>.html
bash $KBDIR/.kb/bin/serve_devlog.sh $KBDIR 8800
```

서버는 KB 루트를 서빙하고, 새 문서는 1분 안에 색인의 Tech docs에 나타난다. 결과는 두세 줄로 보고한다: 만든 문서, 다룬 질문, 참고 문헌 수, 건너뛴 후보와 이유.

## 하지 않는 것

- KB 안의 devlog 사본이나 source checkout의 문서를 고치지 않는다.
- 확인하지 않은 논문 번호, 수치, 인용을 싣지 않는다.
- 한 번 실행에 두 편 이상 만들지 않는다. 12시간마다 한 편씩 쌓는다.
