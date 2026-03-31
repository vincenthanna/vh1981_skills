# 다른 프로젝트에서 이 레퍼런스를 사용하는 방법

이 문서는 `claude_skills_storage`를 다른 프로젝트의 Claude Code 세션에서 참조하는 방법을 설명합니다.

---

## 방법 1: CLAUDE.md에서 직접 참조 (권장)

가장 간단한 방법. 대상 프로젝트의 `CLAUDE.md`에 이 저장소의 경로를 참조 규칙으로 추가합니다.

### 설정

대상 프로젝트의 `CLAUDE.md`에 다음을 추가:

```markdown
## 외부 레퍼런스

Claude AI 에코시스템 레퍼런스가 `/Users/yeonhuigim/workspace/claude_skills_storage/`에 있다.
SDK, 에이전트, 스킬, 통합, 안전 관련 질문에 답할 때 해당 디렉토리의 문서를 참조하라.

### 참조 라우팅

| 키워드 | 참조 경로 |
|--------|----------|
| SDK, API 클라이언트 | /Users/yeonhuigim/workspace/claude_skills_storage/01_SDK/ |
| Claude Code, Agent SDK | /Users/yeonhuigim/workspace/claude_skills_storage/02_Product/ |
| 에이전트 정의, subagent_type | /Users/yeonhuigim/workspace/claude_skills_storage/07_Agent/ |
| 워크플로우 스킬 | /Users/yeonhuigim/workspace/claude_skills_storage/08_Workflow/ |
```

### 장점
- 설정이 가장 간단
- Claude Code가 필요할 때 파일을 직접 읽어 참조
- 항상 최신 상태 반영

### 단점
- 절대 경로 의존 (다른 머신에서는 경로 변경 필요)
- Claude Code의 컨텍스트 윈도우를 추가로 소비

---

## 방법 2: 심볼릭 링크

대상 프로젝트 내에 심볼릭 링크를 만들어 로컬 디렉토리처럼 접근합니다.

### 설정

```bash
# 대상 프로젝트 루트에서
ln -s /Users/yeonhuigim/workspace/claude_skills_storage ./claude-ref

# 특정 카테고리만 링크
ln -s /Users/yeonhuigim/workspace/claude_skills_storage/07_Agent ./.claude/ref-agents
ln -s /Users/yeonhuigim/workspace/claude_skills_storage/08_Workflow ./.claude/ref-workflows
```

대상 프로젝트의 `CLAUDE.md`에 추가:

```markdown
## 외부 레퍼런스

`./claude-ref/` 디렉토리에 Claude AI 에코시스템 레퍼런스가 있다.
관련 질문 시 해당 디렉토리의 README.md를 먼저 읽고, 적절한 파일을 참조하라.
```

### 장점
- 상대 경로로 접근 가능
- `.gitignore`에 추가하면 git에 영향 없음
- 선택적 카테고리만 링크 가능

### 단점
- 심볼릭 링크가 OS별로 다르게 동작할 수 있음
- 팀원 간 경로 불일치 가능

---

## 방법 3: ~/.claude/CLAUDE.md (글로벌 설정)

모든 프로젝트에서 자동으로 레퍼런스를 참조하도록 글로벌 CLAUDE.md에 설정합니다.

### 설정

`~/.claude/CLAUDE.md`에 추가:

```markdown
## 글로벌 레퍼런스

Claude AI 에코시스템 레퍼런스: /Users/yeonhuigim/workspace/claude_skills_storage/

### 사용 규칙
- Anthropic SDK, Claude Code, MCP, 에이전트 관련 질문 시 위 경로의 문서를 참조하라
- 참조 전에 해당 카테고리의 README.md를 먼저 읽어 적절한 파일을 판단하라
- 전체 목차: /Users/yeonhuigim/workspace/claude_skills_storage/README.md
```

### 장점
- 모든 프로젝트에서 자동 적용
- 프로젝트별 설정 불필요

### 단점
- 무관한 프로젝트에서도 컨텍스트 소비
- 프로젝트별 커스터마이징 불가

---

## 방법 4: /import_from_project 스킬로 동기화

이 저장소에 포함된 `/import_from_project` 스킬을 사용하여, 다른 프로젝트의 스킬/에이전트를 이 레퍼런스에 지속적으로 동기화합니다.

### 사용법

```bash
# claude_skills_storage 디렉토리에서 Claude Code 실행
cd /Users/yeonhuigim/workspace/claude_skills_storage

# 다른 프로젝트의 스킬/에이전트를 가져와 문서화
/import_from_project /Users/yeonhuigim/workspace/다른프로젝트

# Anthropic 공식 저장소 문서 업데이트
/update_skill_docs
```

### 장점
- 여러 프로젝트의 스킬을 한곳에 통합 관리
- 문서가 일관된 형식으로 정리됨
- 중복 감지 및 그룹핑 자동화

### 단점
- 수동 실행 필요 (자동 동기화 아님)
- 원본 스킬이 변경되면 재실행 필요

---

## 방법 5: .claude/rules/ 파일로 참조 규칙 주입

대상 프로젝트의 `.claude/rules/` 디렉토리에 참조 규칙 파일을 배치합니다.

### 설정

```bash
# 대상 프로젝트에 rules 디렉토리 생성
mkdir -p .claude/rules
```

`.claude/rules/external-reference.md` 파일 생성:

```markdown
# 외부 레퍼런스 참조 규칙

다음 키워드가 포함된 작업 시, 지정된 경로의 문서를 먼저 읽고 답변에 활용하라.

## 참조 매핑

| 키워드 | 참조 경로 |
|--------|----------|
| SDK, pip install anthropic, npm install | /Users/yeonhuigim/workspace/claude_skills_storage/01_SDK/ |
| Claude Code, Agent SDK | /Users/yeonhuigim/workspace/claude_skills_storage/02_Product/ |
| MCP, GitHub Action | /Users/yeonhuigim/workspace/claude_skills_storage/05_Integration/ |
| 서브에이전트, subagent_type | /Users/yeonhuigim/workspace/claude_skills_storage/07_Agent/ |
| 커밋, PR, 릴리스 워크플로우 | /Users/yeonhuigim/workspace/claude_skills_storage/08_Workflow/ |

## 참조 절차

1. 해당 카테고리의 README.md를 읽어 적절한 파일 판단
2. 해당 .md 파일을 읽어 상세 정보 확인
3. 답변에 구체적인 설치 방법, 코드 예시, 설정 방법을 포함
```

### 장점
- `CLAUDE.md`를 수정하지 않아도 됨
- 규칙 파일 단위로 추가/제거 가능
- `.gitignore`로 개인 설정화 가능

### 단점
- 절대 경로 의존

---

## 권장 조합

| 상황 | 권장 방법 |
|------|----------|
| 개인 작업, 단일 머신 | **방법 3** (글로벌) + **방법 4** (동기화) |
| 팀 프로젝트, 공유 설정 | **방법 2** (심볼릭 링크) + **방법 1** (CLAUDE.md) |
| 특정 프로젝트에서만 사용 | **방법 1** (CLAUDE.md) 또는 **방법 5** (rules) |
| 여러 프로젝트의 스킬 통합 관리 | **방법 4** (/import_from_project) |
