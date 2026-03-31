---
title: imgsender 정적 링크 빌드 + HTTP keep-alive + 웹 뷰어 디버깅
repo: dp5
tags:
  - imgsender
  - static-linking
  - http-keepalive
  - mjpeg
  - web-viewer
  - debugging
  - cloud-mode
created_at: '2026-02-24T16:37:17.578Z'
source: claude-code-skill
hostname: mtmc71_yeonhui
---
1. imgsender 에서 make 시 최대한 라이브러리를 정적 링크하도록 Makefile 혹은 필요하다고 판단되는 부분을 수정해라.

2. imgsender rtsp 수신 및 송신 동작이 단일 스레드로 이루어지고 있는지? view 를 여러 그룹으로 나누어 스레드 처리를 해야 할 것 같아 보이는데 어떻게 생각해?
→ (이미 뷰별 멀티스레드 구조였음. HTTP 클라이언트를 매 프레임마다 생성하는 문제 발견)
→ HTTP keep-alive 연결 재사용하도록 수정해줘

3. imgsender 의 전체 처리가 지체되는 경우 (queue 가 full 되거나 full 되서 drop해야 하는 경우) 확실히 경고 메세지가 출력되도록 해달라.

4. 지금 imgsender 에서 9채널 보내도록 했는데, api/v1/viewer 에서 2개 view 영상이 안 보이고 있다. 직접 python3 app.py 돌려서 디버깅 해봐라.
→ (브라우저 HTTP/1.1 동시 연결 제한 6개가 원인. MJPEG long-lived 연결 → snapshot polling 방식으로 변경)

5. 5초 주기로 영상 화면들이 전체 refresh(검은색 깜박) 되고 있는데, 혹시 의도한 동작인가?
→ (fetchStreams가 5초마다 무조건 render() 호출하여 DOM 전체 교체. 뷰 목록 변경 시에만 render하도록 수정)
