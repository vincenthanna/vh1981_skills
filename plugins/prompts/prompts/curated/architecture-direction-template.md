---
title: 아키텍처 방향성 요청 템플릿
repo: curated
tags:
  - template
  - design
  - architecture
  - planning
  - reusable
curated_from:
  - general/서비스-확장-방향성-요청-프롬프트
quality_score: 4.5
created_at: '2026-02-26T00:00:00.000Z'
source: curate-prompts
---
## 목적
시스템/서비스 확장 또는 아키텍처 결정 시 방향성과 로드맵 요청

## 템플릿
```
이 {{서비스/시스템}}을 {{확장목표}}하고 싶은데, 방향성을 제시해봐라.

## 기대 응답
- 여러 방식 비교
- 각 방식의 장단점
- 구현 복잡도
- 추천 로드맵
```

## 사용 예시
```
이 서비스를 여러 사람이 사용하도록 만들고 싶은데, 방향성을 제시해봐라.

## 기대 응답
- 여러 방식 비교 (Self-hosted, SaaS, Platform App 등)
- 각 방식의 장단점
- 구현 복잡도
- 추천 로드맵
```

## 변수 설명
- `{{서비스/시스템}}`: 확장 대상 서비스나 시스템
- `{{확장목표}}`: 멀티유저, 고가용성, 글로벌 배포 등 목표
