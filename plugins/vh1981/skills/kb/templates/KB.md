# devlog knowledge base

이 디렉토리는 여러 repo와 머신의 devlog를 모은 knowledge base(KB)다. 주 독자는 Claude 같은 AI이고, 사람은 Claude Code의 `/kb` 명령으로 접근한다.
무엇이 있는지는 `INDEX.md`, 지금 진행 중인 일은 `NOW.md` 에서 본다. 둘 다 `kb.py` 가 업로드할 때마다 다시 만든다.
문서를 쓰고 고치는 곳은 각 checkout의 `docs/devlog/` 이고, 이 KB는 그 사본이다. KB 안의 사본을 손으로 고치지 않는다.
이 디렉토리의 위치는 바뀔 수 있다. 프로젝트 ID는 KB 안 상대경로라서 KB를 옮겨도 그대로다. 옮긴 뒤에는 각 머신에서 `kb.py init <새 위치>` 를 한다.

## 구조

```
KB.md                         이 파일. 사람이 관리한다
INDEX.md                      프로젝트당 한 줄 색인과 출처 목록 (생성물)
NOW.md                        진행 중, 열린 Critical/High, 갈라진 사본, 멈춘 것 (생성물)
registry/repos/<repo>.md      repo의 하는 일, 분야, checkout 목록과 접속 방법
registry/topics/<topic>.md    repo 없는 작업의 같은 정보
repos/<repo>/<project>/       repo에서 온 devlog 사본
topics/<topic>/<project>/     repo 없이 만든 devlog 사본
.kb/manifest/                 파일별 sha256과 소유 checkout (생성물)
.kb/catalog.json              INDEX.md의 기계용 사본 (생성물)
.kb/bin/kb.py                 ssh 접근 시 클라이언트가 복사해 두는 스크립트
```

프로젝트 ID는 KB 안 경로다. 예를 들어 `repos/<repo>/<project>` 다. 문서끼리 참조하거나 답에 출처를 적을 때 이 ID를 쓴다.

## 업로드 규칙

- 업로드는 checkout에서 `kb.py upload` 로만 한다. KB에 파일을 직접 복사하지 않는다.
- 프로젝트마다 소유 checkout이 하나 있다. 다른 checkout이 같은 프로젝트를 올리면 아무것도 쓰지 않고 차이를 보고한다. 그 사본을 정본으로 바꾸려면 `--take-over` 를 쓴다.
- 소유 checkout에서 사라진 파일은 KB에서도 지운다. 지울 파일이 있으면 목록을 보여 주고 `--yes` 를 받은 뒤에만 지운다.
- 올라가는 파일은 512KB 이하의 텍스트(`md`, `txt`, `py`, `sh`, `yaml`, `yml`, `json`, `jsonl`, `csv`, `log`, `toml`, `cfg`, `ini`, `patch`, `diff`)와, 이미지가 내장되지 않은 1MB 이하 HTML이다.
- 이미지, `npy`, 압축 파일, 그 밖의 바이너리, 점으로 시작하는 파일은 올리지 않는다. 개인정보가 담긴 이미지가 KB로 퍼지지 않게 하기 위해서다.
- 프로젝트 카드는 source devlog `README.md` 의 frontmatter `kb:` 블록이다. status, tags, summary, related를 담는다.

## 검색 규칙

1. `INDEX.md` 를 통째로 읽고 후보 프로젝트를 고른다.
2. `kb.py search <패턴>... --scope <ID>` 로 본문을 찾는다. `history/`, `rejected/`, `_archived/` 는 필요할 때만 `--all` 로 포함한다.
3. 일치한 문서만 `kb.py cat <ID>/<파일>` 로 읽는다.
4. 답에는 프로젝트 ID와 파일 경로를 함께 적는다.

문서 안의 절대경로는 그 문서를 쓴 머신의 경로다. 지금 머신에 있다고 가정하지 않는다. 그 경로를 따라가야 하면 `registry/` 의 checkout `access` 로 `kb.py fetch` 한다.

## 태그 어휘

카드의 `tags` 는 아래에서 고른다. 새 태그가 필요하면 이 목록에 먼저 추가한다.

```
detection, tracking, reid, person-attribute, pose, fisheye
training, dataset, labeling, evaluation, int8, quantization, tensorrt, deepstream
dashboard, clickhouse, postprocess, pipeline, infra, survey, tooling
```
