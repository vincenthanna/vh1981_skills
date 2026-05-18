# 🔄 Workflow — 개발 워크플로우 스킬 & 템플릿

Claude Code 커스텀 스킬과 개발 프로세스 템플릿 모음.
소프트웨어 개발 라이프사이클(코딩 → 커밋 → 테스트 → PR → 릴리스)을 자동화한다.

## 스킬 목록

### Git & 코드 관리

- [commit](./commit.md) — Conventional Commits 형식의 원자적 커밋 생성
- [pr](./pr.md) — GitHub PR 생성/업데이트, 시각적 diff 다이어그램 포함

### 개발

- [develop](./develop.md) — 멀티 에이전트 합의 기반 기능 개발 오케스트레이션
- [review-claudemd](./review-claudemd.md) — 대화 히스토리 분석으로 CLAUDE.md 자동 개선

### 테스트 & QA

- [testbranch](./testbranch.md) — 라이브 설치본에 브랜치 코드 마운트 및 검증
- [qa](./qa.md) — RC 태그 릴리스 검증 루프

### 릴리스 관리

- [releasebranch](./releasebranch.md) — 릴리스 후보(RC) 태그 생성
- [release](./release.md) — 최종 릴리스 발행 및 브랜치 관리

### 프로세스 템플릿

- [phased-development](./phased-development.md) — 대규모 코드 변경을 단계별로 설계/구현/검증하는 프로세스 템플릿
