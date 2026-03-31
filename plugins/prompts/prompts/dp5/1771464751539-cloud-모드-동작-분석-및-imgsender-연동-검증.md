---
title: Cloud 모드 동작 분석 및 imgsender 연동 검증
repo: dp5
tags:
  - cloud-mode
  - imgsender
  - integration-test
  - verification
  - deepstream
created_at: '2026-02-19T01:32:31.539Z'
source: claude-code-skill
hostname: mtmc71_yeonhui
---
1. d-platform 소스코드와 ./imgsender, docs/cloud_mode_spec.md, docs/image_api_design.md 문서 내용을 분석해서 cloud 모드 동작에 대해 이해하고 동작 설명을 간략하게 해라
2. 현재 imgsender 는 띄워놓은 상태이다. 이 상태에서 'python3 app.py' 실행해서 제대로 동작하는지 검증하라. - 현재 config.yaml 에 cloud 모드로 동작하도록 설정해 두었다.
    - 제대로 imgsender로부터 이미지와 그 이미지에 포함된 메타데이터를 수신하고 있는지 확인한다.
        - 수신한 이미지 10 장에 대해 이미지 수신 여부와 수신된 메타데이터를 출력해라.
    - 수신한 이미지가 정상적으로 저장되는지 확인하라.
