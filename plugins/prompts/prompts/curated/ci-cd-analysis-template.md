---
title: CI/CD 실패 분석 템플릿
repo: curated
tags:
  - template
  - analysis
  - ci-cd
  - debugging
  - reusable
curated_from:
  - plusinsight/github-actions-실패-원인-분석-요청
quality_score: 4.5
created_at: '2026-02-26T00:00:00.000Z'
source: curate-prompts
---
## 목적
CI/CD 파이프라인 실패 시 원인만 먼저 파악 (수정은 별도)

## 템플릿
```
이 repo에서 올라간 PR이 트리거한 {{CI시스템}} action이 실패하는데 원인을 확인해줘:
{{실패한 job 링크}}

수정은 하지 말고 일단 원인만 확인해줘.
```

## 사용 예시
```
이 repo에서 올라간 PR이 트리거한 GitHub Actions이 실패하는데 원인을 확인해줘:
https://github.com/org/repo/actions/runs/12345/job/67890?pr=123

수정은 하지 말고 일단 원인만 확인해줘.
```

## 변수 설명
- `{{CI시스템}}`: GitHub Actions, Jenkins, CircleCI 등
- `{{실패한 job 링크}}`: 실패한 CI job의 URL
