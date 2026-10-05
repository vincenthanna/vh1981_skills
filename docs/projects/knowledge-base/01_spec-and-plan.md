# devlog knowledge base 사양 및 구현계획

이 문서는 여러 repo와 머신에 흩어진 devlog를 한 디렉토리(knowledge base, 이하 KB)에 모으고, 어느 세션에서나 업로드·검색·현황 조회를 할 수 있게 하는 기능의 사양과 구현계획이다.
결론은 새 스킬 `vh1981:kb` 와 결정론적 스크립트 `kb.py` 를 만들고, 기존 `/devlog upload` 는 이 스킬로 위임하는 것이다.
ds35 서버를 조사한 결과 같은 프로젝트가 여러 worktree와 clone에 갈라진 사본으로 존재했다. 그래서 업로드는 단순 미러 대신, 프로젝트마다 소유 checkout을 하나 두고 파일 manifest로 충돌을 감지하는 방식으로 바꿨다.
현재 상태는 구현과 초기 적재까지 완료다. KB는 ds35의 `/home/yeonhui/kb` 에 있고, 두 머신의 devlog 프로젝트 21개가 올라가 있다.
기본 위치는 바꿔 쓸 수 있다(`kb init`, `VH1981_KB`, `--kb`, `VH1981_KB_DEFAULT`). 대기 중인 결정은 없다. 남은 일은 카드가 없는 두 프로젝트에 README를 만드는 것이다.

## 요구사항 정리

사용자 요구를 기능 단위로 정리하면 다음 다섯 가지다.

| 번호 | 요구 | 이 문서에서의 이름 |
|---|---|---|
| R1 | devlog를 repo별로, repo가 없으면 주제별로 모아 저장한다 | 저장소(store) |
| R2 | 어떤 repo나 장소에서 무슨 일을 하고 어떤 분야와 관련되는지 등록하고, 필요하면 그곳에 직접 접속해 최신 내용을 가져온다 | 등록부(registry), live fetch |
| R3 | AI가 필요한 정보를 빠르게 찾도록 최적화하고, 사람은 Claude Code로 접근한다 | 색인(index), 카드(card), 검색 |
| R4 | devlog를 쓰는 세션은 업로드·업데이트·검색을 할 수 있고, 세션 사이 정보 교환에 맞는 구조를 가진다 | `kb upload`, `kb search` |
| R5 | 지금 이 사람이 무슨 일을 진행 중인지 파악할 수 있다 | 현황(status) |

KB 자체는 정해 둔 디렉토리일 뿐이다. 그 안의 `KB.md` 가 저장·업로드·검색 규칙을 담고, 접근은 로컬 경로와 `ssh` 두 가지로 한다.

## 현재 devlog 동작

`/devlog upload` 가 이미 KB 업로드의 원형이다. 다만 아래 한계가 있다.

```
plugins/vh1981/skills/devlog/commands/upload.md
```

| 현재 동작 | 한계 |
|---|---|
| `cp -a docs/devlog/<project>/. <target>/projects/<project>/` 로 통째로 복사한다 | 로컬 경로만 지원하고 `ssh` 는 지원하지 않는다 |
| 대상은 `docs/devlog/.upload-target` 에 repo마다 저장한다 | 머신 단위 설정이 없어 repo마다 경로를 다시 지정해야 한다 |
| 같은 이름 파일만 덮어쓰고 삭제는 동기화하지 않는다 | source에서 archive나 rename한 문서의 낡은 사본이 KB에 남는다 |
| `projects/<project>/` 한 단계로 저장한다 | 같은 프로젝트의 다른 사본이 서로 덮어쓰고, 어느 repo에서 왔는지 알 수 없다 |
| 프로젝트 디렉토리 전체를 복사한다 | 이미지, `npy`, 이미지가 내장된 HTML까지 KB로 퍼진다 |
| 색인, 등록부, 검색이 없다 | 쌓아도 찾을 방법이 grep뿐이다 |

devlog의 나머지 구조는 KB에 그대로 활용할 수 있다. 프로젝트 `README.md` 에는 Scope, Period, AUTO-GENERATED 영역(Entries, Remaining / Next)이 있어 카드의 재료가 된다.
`history/` 는 "요청할 때만 읽는다" 규칙이 있어 검색 대상에서 기본 제외하기 좋다.

## 실제 devlog 조사 결과

두 머신의 devlog를 조사했다. ds35에 대부분이 있고, 두 머신에 같은 프로젝트(`fancl-staff-journey`)가 함께 있다.

```
ds35 (ssh yeonhui@192.168.100.135, /home/yeonhui/workspace)   12개 checkout, 약 400 md, 전체 620MB
macbook (~/workspace)                                          6개 checkout, 74 md, 약 1MB
```

ds35의 checkout별 현황은 아래와 같다. 프로젝트 이름 뒤 숫자는 다른 checkout에도 같은 이름이 있는 경우의 사본 수다.

| checkout | git 관계 | 프로젝트 | md | 크기 |
|---|---|---|---|---|
| `ppap` | `DeepingSource/ppap` 본체 | reid-low-res-similarity(3), pa-reid-train-speedup(3), pa-ptq-int8-pipeline | 20 | 2.8M |
| `ppap-reid-low-res-similarity` | `ppap` 의 worktree | reid-low-res-similarity(3), pa-reid-train-speedup(3), pa-dataset-ingest-2609(2) | 61 | 419M |
| `ppap_train` | `ppap` 의 별도 clone (`git@` URL) | reid-low-res-similarity(3), pa-reid-train-speedup(3), pa-dataset-ingest-2609(2) | 43 | 177M |
| `ppap-solider`, `ppap-tao` | `ppap` 의 worktree | ppap-solider, ppap-tao | 19 | 228K |
| `plusinsight` | `DeepingSource/plusinsight` 본체 | dplatform-quantization(2) | 15 | 232K |
| `pi_od_int8_fix` | `plusinsight` 의 worktree | dplatform-quantization(2), bytetrack-kalman-predict-tlbr-bug | 27 | 5.9M |
| `new-pedestrian-detector` | `DeepingSource/new-pedestrian-detector` | od-replace-survey(2) 외 4개 | 98 | 1.3M |
| `new_od_survey` | remote 없는 git | od-replace-survey(2) | 42 | 13M |
| `fancl_works`, `od_tracker_improve_job`, `seal_model_repos` | remote 없는 git | 각 1개 | 72 | 1.1M |

이 조사에서 설계를 바꾼 사실은 다섯 가지다.

1. **같은 프로젝트가 여러 checkout에 갈라진 사본으로 있다.** `reid-low-res-similarity` 는 세 사본이 md 9개, 28개, 44개이고 README가 모두 다르다.
   사본끼리 포함 관계도 아니다. `ppap_train` 사본에만 있는 파일은 없지만, 같은 이름의 `02_`, `16_`, `README.md` 내용이 서로 다르다. 사본을 차례로 미러하면 나중에 올린 사본이 더 최신인 사본을 덮어쓴다.
2. **같은 repo가 URL 형식과 checkout 방식만 달리해 여러 번 나온다.** `https://github.com/DeepingSource/ppap.git` 과 `git@github.com:DeepingSource/ppap.git` 은 같은 repo이고, worktree는 `git rev-parse --git-common-dir` 로 본체를 가리킨다. checkout 디렉토리 이름으로는 repo를 식별할 수 없다.
3. **devlog는 거의 git에 들어가 있지 않다.** 12개 checkout 중 `od_tracker_improve_job` 만 devlog를 추적한다. 사용자는 `fancl-devlog_2026-09-20.tar.gz` 처럼 손으로 백업하고 있으므로, KB가 사실상 유일한 백업이 된다.
4. **devlog 안에 비텍스트 산출물이 많다.** jpg 5975개, png 149개, npy 38개가 있다. HTML 33개 중 5개에 `data:image` 가 내장돼 있고, 가장 많은 것은 87장이다. 반대로 `data/` 아래에는 `RESULT.md`, `.py` 77개, 작은 `json`·`yaml`·`log` 처럼 재현에 필요한 텍스트가 있다.
5. **README의 Branch / Repos 줄에 그 머신의 절대경로가 들어간다.** 예를 들어 `/home/yeonhui/workspace/new-pedestrian-detector` 다. 다른 머신에서 이 경로를 그대로 따라가면 안 되므로, 접속 방법은 등록부가 맡아야 한다.

ds35에는 `python3` 3.10과 `rsync` 가 있다. devlog가 아닌 문서 묶음(`reid_reconstruct/docs/*.md`)도 있지만 이번 범위에서는 제외한다.

기존 `hub` 플러그인(ai-hub 서버)과는 역할이 다르다. hub는 세션 사이에 메시지와 인수인계를 주고받는 수신함이고, KB는 오래 남는 지식의 저장소다. 둘을 합치지 않는다.

## 사양

### 식별자

KB는 repo, checkout, 프로젝트를 구분한다. 조사 결과 1, 2번 때문에 셋을 분리해야 한다.

| 대상 | 식별자 | 만드는 법 |
|---|---|---|
| repo | `<repo>` | origin URL을 정규화한 `<org>/<repo>` 의 `<repo>` 부분. `https://`, `git@`, `.git` 차이를 없앤다. 같은 `<repo>` 이름이 다른 org로 이미 있으면 `<org>__<repo>` |
| repo 없는 작업 | `<topic>` | remote가 없으면 checkout 디렉토리 이름을 기본값으로 제안하고, 사용자가 바꿀 수 있다 |
| checkout | `<host>:<path>` | 한 머신의 한 작업 디렉토리. worktree와 clone도 각각 하나의 checkout이다 |
| 프로젝트 | `repos/<repo>/<project>` 또는 `topics/<topic>/<project>` | KB 안 경로이자, 문서끼리 참조할 때 쓰는 안정된 주소 |

### KB 디렉토리 구조

KB 루트는 아래 구조를 가진다. `KB.md` 만 사람이 관리하고, 나머지는 `kb.py` 가 만든다.

```
<kb>/
  KB.md                         # 규칙: 구조, 업로드·검색 절차, 태그 어휘 (사람이 관리)
  INDEX.md                      # 생성물: 프로젝트당 한 줄 색인 (AI가 가장 먼저 읽는 파일)
  NOW.md                        # 생성물: 진행 중인 일과 열린 Critical/High 항목
  registry/repos/<repo>.md      # 등록: 하는 일, 분야, checkout 목록과 접속 방법
  registry/topics/<topic>.md
  repos/<repo>/<project>/       # repo에서 온 devlog 사본
  topics/<topic>/<project>/     # repo 없이 만든 devlog 사본
  .kb/
    manifest/<repo>/<project>.json   # 파일별 sha256, 크기, mtime, 쓴 checkout, 소유 checkout
    lock/                       # 색인 재생성 잠금 (mkdir 잠금)
    staging/                    # 업로드 중간 산출물
    catalog.json                # 생성물: INDEX.md와 같은 내용의 기계용 사본
```

### 프로젝트 카드

카드는 source의 devlog `README.md` 맨 위에 붙는 YAML frontmatter다. KB 쪽에 따로 파일을 두지 않으므로, 사본은 항상 소유 checkout의 내용을 그대로 비춘다.

```yaml
---
kb:
  status: active            # active | paused | done
  tags: [reid, int8]        # KB.md의 태그 어휘에서 고른다
  summary: >-               # 3줄 이내. 무엇을 왜 하는지와 현재 결론
    ...
  related: [repos/ppap/pa-reid-train-speedup]   # 관련 KB 프로젝트 ID
---
```

업로드할 때 카드가 없거나 오래됐으면 Claude가 README와 조사 문서를 읽고 채운 뒤 사용자에게 보여 준다.
devlog의 `templates/readme.md` 에 이 frontmatter를 추가하고, `create` 와 `update` 가 함께 갱신한다.

### 등록부

등록 단위는 repo(또는 topic)이고, 그 아래에 checkout 목록을 둔다. 조사 결과 worktree마다 branch와 하는 일이 달랐으므로(`ppap-solider` 는 solider, `ppap-tao` 는 tao), checkout마다 branch와 한 줄 설명을 기록한다.

등록 파일은 `kb.py` 가 관리하는 JSON 코드블록 하나와 그 뒤의 자유 서술로 이루어진다. YAML 대신 JSON을 쓴 것은 원격 KB 호스트에서 PyYAML 없이 표준 라이브러리만으로 읽고 쓰기 위해서다.

```json
{
  "id": "repos/ppap",
  "remote": "github.com/DeepingSource/ppap",
  "work": "사람 속성(PA)과 ReID 모델 학습·경량화",
  "domains": ["reid", "person-attribute", "int8", "training"],
  "checkouts": [
    {"at": "ds35:/home/yeonhui/workspace/ppap-reid-low-res-similarity",
     "access": "ssh://yeonhui@192.168.100.135", "branch": "reid-low-res-similarity",
     "work": "저해상도 ReID 유사도 평가",
     "projects": ["reid-low-res-similarity", "pa-dataset-ingest-2609"],
     "copies": [], "last_upload": "2026-10-05T12:00:00+09:00"}
  ]
}
```

`projects` 는 그 checkout이 소유한 프로젝트이고, `copies` 는 소유자가 따로 있는 사본이다.

첫 업로드 때 등록 항목이 없으면 Claude가 devlog README들의 Scope로 `work` 와 `domains` 를 채운 초안을 만들어 확인받는다. checkout이 처음이면 그 항목만 추가한다.
`kb fetch <repo> [<project>]` 는 checkout의 `access` 로 접속해 `docs/devlog/` 를 읽기 전용으로 읽는다. KB 사본보다 최신 내용이 필요할 때 쓴다.

### 업로드

업로드는 소유 checkout 모델을 따른다. KB의 프로젝트 하나는 소유 checkout 하나가 쓰고, 다른 checkout의 사본은 충돌로 다룬다. 조사 결과 1번처럼 갈라진 사본을 자동으로 합치면 어느 쪽 결론이 맞는지 판단할 수 없기 때문이다.

| 경우 | 동작 |
|---|---|
| KB에 그 프로젝트가 없다 | 업로드한 checkout이 소유자가 된다 |
| 소유 checkout이 다시 올린다 | 바뀐 파일을 덮어쓴다. 이 checkout이 썼는데 지금 source에 없는 파일은 지운다. 지울 목록을 먼저 보여 준다 |
| 다른 checkout이 같은 프로젝트를 올린다 | 쓰지 않는다. 그 사본에만 있는 파일, 내용이 다른 파일, KB에만 있는 파일을 표로 보여 주고 두 가지 중 고르게 한다 |
| 위 경우에 `--take-over` 를 고른다 | 이 checkout이 소유자가 되고 전체를 미러한다. 밀려난 쪽에만 있던 파일 목록을 출력한다 |
| 위 경우에 건너뛰기를 고른다 | 아무것도 쓰지 않는다. 등록부에는 이 checkout이 같은 프로젝트의 사본을 가졌다고 기록한다 |

파일 선별 규칙은 조사 결과 4번에 맞췄다. `data/` 를 통째로 빼지 않고 텍스트 산출물은 살린다.

| 항목 | 규칙 |
|---|---|
| 포함 | `md`, `txt`, `py`, `sh`, `yaml`, `yml`, `json`, `jsonl`, `csv`, `log`, `toml`, `cfg`, `ini`, `patch`, `diff`. 512KB 이하 |
| HTML | `data:image` 가 없고 1MB 이하일 때만 포함한다 |
| 제외 | 이미지, `npy`, 압축 파일, 그 밖의 바이너리, 크기 초과 파일, 점으로 시작하는 파일(`.active` 등) |
| 보고 | 제외한 파일을 종류별 개수와 상위 10개 경로로 출력한다 |

업로드의 나머지 규칙은 아래와 같다.

| 항목 | 규칙 |
|---|---|
| 충돌 감지 | `.kb/manifest/` 의 sha256과 비교한다. mtime은 `cp` 나 tar 압축 해제로 바뀔 수 있어 판단에 쓰지 않는다 |
| 원자성 | `.kb/staging/` 에 풀어 놓고 `rename` 으로 교체한다. 실패하면 기존 사본이 남는다 |
| 마무리 | 잠금을 잡고 `INDEX.md`, `catalog.json`, `NOW.md` 를 다시 만들고 등록부의 `last_upload` 를 갱신한다 |
| git | KB가 git repo여도 커밋하지 않는다. 커밋할 명령을 출력만 한다 |

`ssh` 접근일 때는 로컬에서 tar로 묶어 `ssh` 로 보내고, 원격에서 `python3 -` 로 같은 스크립트를 실행해 풀기, manifest 비교, 색인 재생성을 한다.
원격에는 `python3` 3.8 이상만 있으면 되고 플러그인 설치는 필요 없다. ds35는 3.10이다. macOS 기본 rsync는 openrsync라 옵션 호환이 불확실해서 쓰지 않는다.

### 검색

검색은 넓은 것에서 좁은 것으로 세 단계를 거친다. 각 단계에서 답이 나오면 멈춘다.

1. `INDEX.md` 를 통째로 읽는다. 한 줄에 ID, status, tags, 갱신일, summary가 있다. 현재 규모(두 머신을 합쳐 프로젝트 약 20개)는 물론 수백 개까지 한 번에 읽힌다.
2. 후보 프로젝트에 대해 `kb.py search` 로 본문을 grep한다. `ssh` 접근이면 grep을 원격에서 실행하고 일치한 줄만 받아 온다. `history/`, `rejected/`, `_archived/` 는 사용자가 요청할 때만 포함한다.
3. 일치한 문서만 읽는다. 답에는 KB ID와 파일 경로를 함께 적어 다음 세션이 같은 문서를 바로 열 수 있게 한다.

문서 안의 다른 머신 절대경로(조사 결과 5번)는 그 경로가 지금 머신에 있다고 가정하지 않는다. 경로를 따라가야 하면 등록부에서 그 checkout의 `access` 를 찾아 `kb fetch` 로 읽는다.

### 현황

`NOW.md` 는 업로드할 때마다 다시 만들어진다. 이 사람이 지금 하는 일을 한 화면에 보여 준다.

| 절 | 내용 |
|---|---|
| 진행 중 | `status: active` 프로젝트를 갱신일 역순으로. 소유 checkout의 host와 branch, summary 한 줄 |
| 열린 항목 | 각 README의 Remaining / Next에서 Critical과 High만 |
| 갈라진 사본 | 같은 프로젝트를 가진 checkout이 둘 이상인 경우와 마지막 비교 결과 |
| 멈춘 것 | `status: active` 인데 30일 넘게 업로드가 없는 프로젝트 |

`/kb status` 는 이 파일을 읽어 보여 준다. 업로드가 오래돼 보이면 등록부의 checkout으로 live fetch를 제안한다.

### KB 위치 설정

KB 위치는 머신 단위로 한 번 정한다. 아래 순서로 찾는다.

```
1. 명령의 --kb <위치>
2. 환경변수 VH1981_KB
3. ~/.config/vh1981/kb   (한 줄. kb init 이 쓴다)
4. docs/devlog/.upload-target   (기존 설정. 읽기만 하고, 다음 업로드 때 3번으로 옮기자고 제안)
```

위치는 로컬 절대경로(`/home/yeonhui/kb`) 또는 `ssh://user@host/abs/path` 형식이다.
devlog 대부분이 ds35에 있으므로 KB도 ds35에 두는 것을 제안한다. 그러면 ds35 세션은 로컬로, macbook 세션은 `ssh` 로 접근한다.

## 명령

| 명령 | 동작 |
|---|---|
| `/kb init <위치>` | KB 디렉토리 구조와 `KB.md` 를 만들고 이 머신의 설정에 저장한다. 이미 KB면 설정만 저장한다 |
| `/kb upload [<project>] [--topic <topic>] [--take-over]` | 프로젝트를 업로드한다. 생략하면 활성 devlog 프로젝트. remote가 없으면 topic 이름을 확인받는다 |
| `/kb upload --all` | 현재 checkout의 devlog 프로젝트를 모두 올린다. 충돌한 것은 건너뛰고 끝에 모아 보여 준다 |
| `/kb search <질문>` | 위 세 단계로 찾아 답한다 |
| `/kb status` | `NOW.md` 를 보여 준다 |
| `/kb register` | 현재 checkout의 등록 항목을 만들거나 고친다 |
| `/kb fetch <repo> [<project>]` | 등록된 checkout에 접속해 최신 devlog를 읽는다 |
| `/kb check` | 등록부와 사본의 불일치, 오래된 카드, 갈라진 사본을 점검한다 |
| `/devlog upload ...` | 기존 문법을 그대로 받아 `/kb upload` 로 넘긴다 |

## 결정 사항

| 번호 | 항목 | 상태 | 내용과 근거 |
|---|---|---|---|
| D1 | 기능 위치 | 결정됨 | 새 스킬 `vh1981:kb` 를 만든다. 검색은 devlog를 쓰지 않는 세션에서도 필요하므로 devlog 안에 두지 않는다 |
| D2 | 복사·색인 방식 | 결정됨 | 파일 선별, manifest 비교, 잠금, 색인 생성은 `kb.py` 가 한다. 요약과 태그 같은 판단만 Claude가 한다. 결정론적인 일을 프롬프트에 맡기면 세션마다 결과가 달라진다 |
| D3 | 검색 엔진 | 결정됨 | 색인 파일과 grep만 쓴다. 두 머신을 합쳐 텍스트가 수 MB라 벡터 DB는 설치 부담만 늘린다 |
| D11 | 사본 충돌 모델 | 결정됨 | 소유 checkout 하나만 쓰고, 다른 사본은 보여 주고 고르게 한다. ds35에서 갈라진 사본(같은 파일, 다른 내용)이 실제로 확인돼 자동 병합은 쓰지 않는다 |
| D12 | repo 식별 | 결정됨 | 정규화한 origin URL과 `--git-common-dir` 로 식별한다. checkout 디렉토리 이름은 repo 식별에 쓰지 않는다 |
| D4 | 소유자 업로드 시 삭제 | 결정됨 | 구현 시작 지시로 제안 기본값을 채택했다. 소유 checkout이 썼는데 사라진 파일만, 목록을 보여 주고 확인받은 뒤 지운다 |
| D5 | 업로드 파일 범위 | 결정됨 | 구현 시작 지시로 제안 기본값을 채택했다. 위 "파일 선별 규칙". 측정 CSV가 512KB를 넘는 경우가 잦으면 한도를 올린다 |
| D6 | KB의 git 처리 | 결정됨 | 구현 시작 지시로 제안 기본값을 채택했다. 커밋하지 않고 명령만 출력한다. KB가 사실상 유일한 백업이므로 KB 디렉토리를 git repo로 두고 사용자가 주기적으로 커밋하기를 권한다 |
| D7 | 카드 위치 | 결정됨 | 구현 시작 지시로 제안 기본값을 채택했다. source README의 frontmatter. KB 쪽 별도 파일로 두면 소유자 미러와 충돌한다 |
| D8 | 업로드 시점 | 결정됨 | 구현 시작 지시로 제안 기본값을 채택했다. KB가 설정돼 있으면 `/devlog update` 끝에 자동으로 올린다. devlog가 git에 없어 손 백업에 의존하고 있으므로, 빠뜨리지 않는 쪽이 낫다. 충돌이 나면 쓰지 않고 알리기만 하므로 자동이어도 안전하다 |
| D9 | 자동 검색 규칙 | 결정됨 | 초기 적재 뒤 실제 질의(재양자화, EarlyStopping, ByteTrack)가 첫 줄에 맞는 문서를 찾는 것을 확인하고 `core.md` 에 "다른 repo나 서버의 과거 작업이 관련돼 보이면 kb를 먼저 검색한다" 한 줄을 넣었다 |
| D10 | 기존 `projects/` 레이아웃 | 결정됨 | 구현 시작 지시로 제안 기본값을 채택했다. `kb init` 이 기존 KB에서 `projects/<p>` 를 발견하면 `repos/<repo>/<p>` 로 옮길지 묻는다. 어느 repo인지 알 수 없으면 `topics/legacy/` 로 옮긴다 |
| D13 | KB 위치 | 결정됨 | 기본값은 ds35의 `/home/yeonhui/kb` 이고 `kb.py` 에 내장했다. 머신마다 `kb init`, `VH1981_KB`, 명령의 `--kb` 로 바꾸고, 내장 기본값은 `VH1981_KB_DEFAULT` 로 바꾼다. 자동 업로드는 내장 기본값만으로는 돌지 않는다(`where --configured`) |
| D14 | 기존 갈라진 사본의 첫 소유자 | 결정됨 | md 수가 가장 많고 가장 최근에 수정된 사본을 소유자로 했다. 다른 사본은 모두 "이 사본에만 있는 파일 0개"여서 잃는 문서가 없다("초기 적재" 절) |

## 구현계획

### Phase 1: KB 골격, 식별자, 위치 설정
목표: 로컬과 `ssh` 위치 모두에 KB를 만들고, checkout에서 repo와 프로젝트 ID를 정확히 뽑는다.
변경 파일:
```
plugins/vh1981/skills/kb/SKILL.md
plugins/vh1981/skills/kb/templates/KB.md
plugins/vh1981/skills/kb/scripts/kb.py
```
작업 내용:
- `kb.py` 에 위치 해석(위 4단계)과 `init` 을 구현한다. `ssh` 위치는 `ssh <host> 'python3 -' < kb.py` 형태로 원격 실행하고, 스크립트는 Python 3.8 문법만 쓴다.
- `kb.py ident` 를 구현한다. origin URL 정규화, `--git-common-dir` 로 본체 판별, remote 없는 경우의 topic 후보를 출력한다.
- `KB.md` 템플릿에 디렉토리 구조, 업로드·검색 규칙, 초기 태그 어휘를 쓴다. 태그 어휘는 두 머신의 devlog README Scope에서 뽑는다.
- `SKILL.md` 는 명령 라우팅과 Claude가 판단할 부분만 담고, 파일 조작은 모두 `kb.py` 를 호출하게 한다.
완료 기준: ds35의 `ppap`, `ppap-tao`, `ppap_train` 세 checkout에서 `kb.py ident` 가 모두 `ppap` 을 내고, 임시 디렉토리와 `ssh://localhost/<임시>` 양쪽에서 `init` 이 같은 구조를 만든다.

### Phase 2: 업로드, manifest, 카드
목표: devlog 프로젝트를 소유 checkout 모델로 KB에 올리고 색인을 만든다.
변경 파일:
```
plugins/vh1981/skills/kb/scripts/kb.py
plugins/vh1981/skills/kb/SKILL.md
plugins/vh1981/skills/devlog/templates/readme.md
plugins/vh1981/skills/devlog/commands/upload.md
plugins/vh1981/skills/devlog/commands/update.md
plugins/vh1981/skills/devlog/SKILL.md
```
작업 내용:
- `kb.py upload` 에 파일 선별, manifest 비교, 소유자 판정, 충돌 표 출력, `--take-over`, staging과 rename 교체, 잠금, 색인 재생성, 등록부 갱신을 구현한다. `--dry-run` 은 쓸 파일, 지울 파일, 제외 파일만 출력한다.
- devlog README 템플릿에 `kb:` frontmatter를 추가한다. `create` 는 빈 카드를 만들고, `update` 는 status와 summary가 결론과 어긋나면 고친다.
- `/devlog upload` 를 `/kb upload` 위임으로 바꾸고 기존 인자 문법을 유지한다. D8이 자동 업로드로 결정되면 `update` 의 마지막 단계에 업로드를 넣는다.
- 첫 업로드 때 등록 항목 초안을 만들어 확인받는 흐름을 SKILL.md에 쓴다.
완료 기준: 임시 KB에 ds35의 `ppap-reid-low-res-similarity` 를 올린 뒤 `ppap_train` 을 올리면, `reid-low-res-similarity` 는 쓰이지 않고 내용이 다른 파일 3개(`02_`, `16_`, `README.md`)가 충돌 표에 나온다. 같은 업로드에서 jpg와 `data:image` HTML은 하나도 KB에 들어가지 않는다.

### Phase 3: 검색과 live fetch
목표: 어느 세션에서나 KB에서 답을 찾고, 필요하면 등록된 checkout에서 최신 내용을 읽는다.
변경 파일:
```
plugins/vh1981/skills/kb/scripts/kb.py
plugins/vh1981/skills/kb/SKILL.md
```
작업 내용:
- `kb.py search <패턴>... [--include-history]` 를 구현한다. 결과는 `<KB ID>/<파일>:<줄>: <내용>` 형식으로, 파일당 일치 수 상한을 둔다.
- SKILL.md에 세 단계 검색 절차와 답변 형식(KB ID와 경로를 함께 적기)을 쓴다.
- `kb.py fetch <repo> [<project>]` 를 구현한다. 등록부에서 checkout의 `access` 와 경로를 찾아 README와 지정 문서를 출력한다. 쓰기는 하지 않는다.
완료 기준: 두 머신의 devlog를 올린 임시 KB에서 "INT8 재양자화 최종 결과"를 물으면 `repos/plusinsight/dplatform-quantization` 의 문서 경로와 함께 답한다.

### Phase 4: 현황과 점검
목표: 진행 중인 일과 갈라진 사본을 한 번에 보고, 오래된 KB 상태를 알아챈다.
변경 파일:
```
plugins/vh1981/skills/kb/scripts/kb.py
plugins/vh1981/skills/kb/SKILL.md
```
작업 내용:
- `NOW.md` 생성 규칙(진행 중, 열린 항목, 갈라진 사본, 멈춘 것)을 구현하고 `/kb status` 로 보여 준다.
- `kb.py check` 를 추가한다. 등록부에는 있지만 사본이 없는 프로젝트, 사본은 있지만 등록부에 없는 checkout, README Period보다 오래된 카드, 같은 이름의 프로젝트가 다른 repo에도 있는 경우(`od-replace-survey`)를 보고한다.
- D10이 결정되면 기존 `projects/` 레이아웃 이전을 `init` 에 넣는다.
완료 기준: 임시 KB에서 `status: active` 인 프로젝트 하나의 `last_upload` 를 31일 전으로 바꾸면 `NOW.md` 의 "멈춘 것"에 나타나고, `kb check` 가 `od-replace-survey` 를 두 repo에 걸친 이름으로 보고한다.

### Phase 5: 테스트, 배포, 초기 적재
목표: 회귀 테스트를 갖추고 배포한 뒤, 두 머신의 기존 devlog를 KB에 처음 적재한다.
변경 파일:
```
scripts/tests/run.sh
README.md
plugins/vh1981/.claude-plugin/plugin.json
.claude-plugin/marketplace.json
```
작업 내용:
- `run.sh` 에 임시 KB를 쓰는 `init`, `upload`, 소유자 재업로드 삭제, 다른 checkout 충돌, `--take-over`, 파일 선별, 잠금 경합, `search` 테스트를 추가한다. `ssh` 경로는 `localhost` 에 접속할 수 있을 때만 돌리고, 아니면 건너뛰었다고 출력한다.
- README에 kb 절을 추가하고 `/devlog upload` 설명을 위임 구조에 맞게 고친다. 플러그인 버전을 1.9.0으로 올린다.
- 초기 적재 절차: D13의 위치에 `init` 하고, D14대로 소유자를 고른 뒤 checkout마다 `/kb upload --all` 을 한다.
완료 기준: `./scripts/tests/run.sh` 가 모두 통과하고, 초기 적재 후 `INDEX.md` 에 두 머신의 프로젝트가 모두 한 줄씩 있으며 `NOW.md` 의 갈라진 사본 절이 비어 있거나 의도한 것만 남는다.

## 검증 결과

검증은 2026-10-05에 했다. 회귀 테스트는 `./scripts/tests/run.sh` 의 kb 절 28건이며 모두 통과했다. localhost ssh가 없는 머신에서는 ssh 경우를 건너뛴다.

ds35 실데이터 검증은 `/tmp` 의 임시 KB로 했고, source devlog는 읽기만 했다.

| 확인 항목 | 결과 |
|---|---|
| Python 3.10(ds35)에서 store와 client 동작 | 통과 |
| `ppap`, `ppap-reid-low-res-similarity`, `ppap_train` 이 모두 `repos/ppap` 로 식별됨 | 통과. `survey` 가 사본 3개를 한 ID로 묶었다 |
| 소유 checkout 업로드의 파일 선별 | `reid-low-res-similarity` 에서 157개를 올리고 jpg 5964개, png 140개, npy 20개, 큰 HTML 2개를 제외했다 |
| 다른 checkout(`ppap_train`) 업로드 | 충돌로 보고하고 쓰지 않았다. 내용 다름 4개(`02_`, `16_`, `README.md`, `data/manifest_6models_260911.yaml`)와 KB에만 85개를 표시했다 |
| 같은 내용의 사본 | `pa-reid-train-speedup` 이 `same-as-owner` 로 보고됐다 |
| macbook에서 ssh로 원격 KB 사용 | `upload --dry-run`, `search`, `status`, `check`, `cat` 통과 |

구현하면서 사양을 바꾼 점은 두 가지다.

- 등록부를 YAML frontmatter 대신 JSON 블록으로 바꿨다. 원격 호스트에 PyYAML이 없어도 되게 하기 위해서다.
- ssh 연결을 ControlMaster로 재사용하고, 연결 실패(종료 코드 255)는 두 번까지 재시도한다. 연속 호출에서 ds35 sshd가 `Connection timed out during banner exchange` 로 연결을 끊었기 때문이다.


## 초기 적재

2026-10-05에 ds35의 `/home/yeonhui/kb` 를 만들고 두 머신의 devlog를 올렸다. 소유자로 고른 사본과 그 근거는 아래와 같다.

| 프로젝트 | 소유 checkout | 다른 사본과의 차이 |
|---|---|---|
| `repos/ppap/reid-low-res-similarity` | ds35 `ppap-reid-low-res-similarity` (md 44) | `ppap` 은 KB에만 143개, `ppap_train` 은 87개 적다 |
| `repos/ppap/pa-reid-train-speedup` | ds35 `ppap-reid-low-res-similarity` | `ppap_train` 은 README 카드만 다르다 |
| `repos/ppap/pa-dataset-ingest-2609` | ds35 `ppap-reid-low-res-similarity` | `ppap_train` 은 8개 적다 |
| `repos/plusinsight/dplatform-quantization` | ds35 `pi_od_int8_fix` (md 24) | `plusinsight` 는 10개 적다 |
| `topics/fancl_works/fancl-staff-journey` | ds35 `fancl_works` (md 50) | macbook 사본은 44개 적다 |

모든 다른 사본에서 "이 사본에만 있는 파일"은 0개였다. 내용이 다른 파일은 같은 문서의 이전 판이다. 이 사본들은 `NOW.md` 의 "갈라진 사본"에 남아 있다.

카드는 소유 사본 README 19개에 넣었다. status는 2주 안에 고친 것을 active, 그보다 오래됐지만 끝나지 않은 것을 paused, 끝난 것을 done으로 정했고, summary는 README의 Scope와 Remaining에서만 뽑았다.
README가 없는 `repos/new-pedestrian-detector/new-detector` 와 `topics/bytetrack_low_fps/bytetrack-low-fps` 는 카드 없이 올라가 있다. `vh1981_skills` 의 `test` 프로젝트는 시험용이라 올리지 않았다.
등록부에는 repo 4개와 topic 6개의 하는 일과 분야, checkout별 일과 접속 방법을 넣었다. macbook checkout은 외부에서 ssh로 들어올 수 없어 접속 방법을 비워 두었다.

적재 중에 두 가지를 고쳤다. 취소선(`~~[High]~~`)으로 끝낸 항목이 열린 항목으로 잡히던 것을 빼고, 검색 결과가 파일 하나에 몰리지 않도록 파일당 2줄과 "일치 수 상위 파일" 목록을 기본으로 했다.

## 위험

| 위험 | 대응 |
|---|---|
| 두 세션이 같은 프로젝트를 동시에 올린다 | 프로젝트 교체는 rename으로 원자적이고, 색인 재생성은 `mkdir` 잠금으로 하나씩 한다 |
| 갈라진 사본 중 오래된 쪽이 소유자가 된다 | 첫 적재 전에 `kb check` 로 사본을 비교해 사용자가 고른다(D14). 이후에는 `--take-over` 로만 소유자가 바뀐다 |
| 개인정보 이미지나 대용량 산출물이 KB로 퍼진다 | 파일 선별 규칙이 기본으로 막고, 제외 목록을 매번 출력한다 |
| 원격에 `python3` 가 없거나 3.8 미만이다 | `init` 이 먼저 확인하고, 없으면 어떤 명령이 실패했는지 알리고 멈춘다 |
| 카드 summary가 실제 결론과 어긋난다 | `update` 가 결론을 바꿀 때 카드도 고치게 하고, `check` 가 README Period보다 오래된 카드를 표시한다 |
| 문서 속 다른 머신 경로를 지금 머신 경로로 착각한다 | 검색 규칙에서 금지하고, 경로를 따라갈 때는 등록부의 `access` 로 `kb fetch` 한다 |
