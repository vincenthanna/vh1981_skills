---
title: PTS correction CSV 통합 테스트 작성 및 JIRA 이슈 정리
repo: plusinsight
tags:
  - testing
  - pytest
  - pts-correction
  - jira
  - issue-definition
created_at: '2026-02-13T06:32:34.163Z'
source: claude-code-skill
hostname: mtmc71_yeonhui
---
1. d-platform/tests/sample/timestamp_test_csv.zip 파일을 unzip 하고, 그 안의 csv 파일들을 읽어서 테스트하는 pytest case 추가해.

검사 조건:
- timestamp 역전/중복 여부 (basic check)
- CORRECTED 상태 100프레임 이상 연속 지속 여부
- 단조증가 보장 (warmup/re-anchor 구간 제외)
- interval deviation 개선 확인 (10% 허용)

2. 지금까지 했던 내용들을 정리해서 issue 정의를 만들어라. 아직 수정 전이라는 상황을 가정하고, 세부적인 수정 내용은 빼고, 현재 문제점과 수정 방향을 중점으로 다듬어라. 특정 파일/클래스명을 언급하지 말아라.
