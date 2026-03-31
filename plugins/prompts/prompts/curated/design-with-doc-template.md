---
title: 설계 요청 + 문서화 템플릿
repo: curated
tags:
  - template
  - design
  - documentation
  - reusable
curated_from:
  - dp5/cloud-mode-실시간-웹-뷰어-기능-설계-요청
quality_score: 4.0
created_at: '2026-02-26T00:00:00.000Z'
source: curate-prompts
---
## 목적
새 기능 설계 시 계획을 문서화하고, 구현 과정에서 문서를 동기화

## 템플릿
```
{{기능명}} 기능을 추가하고 싶다.

요구사항:
- {{요구사항1}}
- {{요구사항2}}
- {{요구사항3}}

계획을 markdown 파일로 저장해라.
이후 plan이 업데이트될 때마다 markdown 파일도 업데이트해라.

plan 검증 요청:
- plan 내용에 서로 맞지 않는 부분이 있는지 확인하고 fix
- 명확하지 않은 부분을 찾아서 내용을 보완하라
- 수정 계획과 실제 코드가 매치되는지 확인하라
```

## 사용 예시
```
실시간 웹 뷰어 기능을 추가하고 싶다.

요구사항:
- bbox 등 meta 정보를 그린 프레임을 스트리밍
- 출력 화면 구성 변경 (full, 2x2, 3x3)
- 수백 개 카메라 지원

계획을 markdown 파일로 저장해라.
이후 plan이 업데이트될 때마다 markdown 파일도 업데이트해라.
```

## 변수 설명
- `{{기능명}}`: 추가할 기능의 이름
- `{{요구사항N}}`: 구체적인 요구사항 목록
