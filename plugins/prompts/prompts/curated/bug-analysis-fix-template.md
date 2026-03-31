---
title: 버그 분석-수정-검증 템플릿
repo: curated
tags:
  - template
  - debugging
  - reusable
curated_from:
  - dp5/버그-원인-분석-및-수정방향-제시-후-구현-지시
  - dp5/imgsender-rtsp-empty-frame-flooding-진단-및-수정
quality_score: 4.5
created_at: '2026-02-26T00:00:00.000Z'
source: curate-prompts
---
## 목적
버그 발생 시 원인 분석 → 수정 방향 제시 → 단계별 구현까지 체계적으로 진행

## 템플릿
```
{{컴포넌트}}에서 {{증상}}이 발생한다.

{{상세 로그/에러 메시지}}

- 원인을 파악하라.
- 바람직한 수정방향을 제시하라.

(후속) 제시된 방향대로 구현해라.
```

## 사용 예시
```
imgsender에서 서버 연결을 오랫동안 하지 못하면 다음 에러가 반복 발생한다.

Error: Empty frame from side
Error: Empty frame from center

- 원인을 파악하라.
- 바람직한 수정방향을 제시하라.

(후속) 제시된 방향대로 구현해라.
```

## 변수 설명
- `{{컴포넌트}}`: 문제가 발생하는 모듈/클래스/파일명
- `{{증상}}`: 관찰되는 문제 현상
- `{{상세 로그/에러 메시지}}`: 실제 에러 로그나 메시지
