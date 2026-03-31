---
title: 검증 + 테스트 작성 템플릿
repo: curated
tags:
  - template
  - verification
  - testing
  - reusable
curated_from:
  - plusinsight/pts-correction-csv-통합-테스트-작성-및-jira-이슈-정리
  - plusinsight/csv-기반-pytest-통합-테스트-추가-zip-자동-해제
quality_score: 4.0
created_at: '2026-02-26T00:00:00.000Z'
source: curate-prompts
---
## 목적
데이터 파일 기반의 통합 테스트 케이스 작성

## 템플릿
```
{{테스트데이터 경로}}를 읽어서 테스트하는 pytest case 추가해.

검사 조건:
- {{조건1}}
- {{조건2}}
- {{조건3}}
- {{조건4}}
```

## 사용 예시
```
tests/sample/timestamp_test_csv.zip 파일을 unzip하고,
그 안의 csv 파일들을 읽어서 테스트하는 pytest case 추가해.

검사 조건:
- timestamp 역전/중복 여부 (basic check)
- 에러 상태 100프레임 이상 연속 지속 여부
- 단조증가 보장 (warmup 구간 제외)
- interval deviation 개선 확인 (10% 허용)
```

## 변수 설명
- `{{테스트데이터 경로}}`: 테스트에 사용할 데이터 파일 경로
- `{{조건N}}`: 검사할 조건들 (구체적인 기준값 포함)
