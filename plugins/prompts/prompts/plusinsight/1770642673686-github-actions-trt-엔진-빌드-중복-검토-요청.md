---
title: GitHub Actions TRT 엔진 빌드 중복 검토 요청
repo: plusinsight
tags:
  - github-actions
  - code-review
  - trt-engine
  - d-platform
created_at: '2026-02-09T13:11:13.686Z'
source: claude-code-skill
hostname: mtmc71_yeonhui
---
.github/workflows/build_monorepo_components.yml 에서 "Build TRT Engines (ada)" 에서 onnx 하나를 여러번씩 빌드하는 것 같아 보인다. 관련된 코드를 확인해보고 혹시 문제점이 있는지 확인해달라.(검토만, 코드 수정 x)
현재 돌고 있는 github action 이다. https://github.com/DeepingSource/plusinsight/actions/runs/21813527386/job/62931210863?pr=382
