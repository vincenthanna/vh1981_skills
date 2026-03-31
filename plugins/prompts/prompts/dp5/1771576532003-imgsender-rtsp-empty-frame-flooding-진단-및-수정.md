---
title: imgsender RTSP empty frame flooding 진단 및 수정
repo: dp5
tags:
  - imgsender
  - rtsp
  - bug-diagnosis
  - producer-consumer
  - reconnection
created_at: '2026-02-20T08:35:32.003Z'
source: claude-code-skill
hostname: mtmc71_yeonhui
---
imgsender 에서 서버 연결을 오랫동안 하지 못하는 상황이 오랜 시간 동안 지속되면 다음의 에러가 빠르게 계속해서 발생한다.
Error: Empty frame from side
Error: Empty frame from window
Error: Empty frame from clothes2

- 원인을 파악하라.
- 바람직한 수정방향을 제시하라.

(이후 추가 지시)
- 1번부터 구현해라
- 나머지 2, 3, 4번도 구현해라
- imgsender 에서 프레임 송신 시 출력되는 log에 site_id 도 출력되도록 수정하라.
