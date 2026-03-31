---
title: dsmtmctracker detection object_meta 보존 분석 및 설정 추가
repo: dp5
tags:
  - deepstream
  - tracker
  - object_meta
  - bbox
  - file_output
  - dsmtmctracker
created_at: '2026-02-19T12:48:46.274Z'
source: claude-code-skill
hostname: mtmc71_yeonhui
---
dsmtmctracker에서 tracker 에서 나온 track 을 object_meta로 만들고 기존 detection object_meta는 삭제하는데, detection object_meta를 삭제하지 않으려면 어떻게 해야 할까? (기존 기능이 있는가?) 코드를 분석해서 알려달라

---

그냥 d-platform/pipeline/components/config.py 에 TrackerConfig 에 preserve_detector_obj_meta 항목을 추가하고, 이게 true이면 tracker에서 지우지 않도록 clear_detector_obj_meta=false 넣도록 수정해라.

---

pipeline/components/probes/file_output.py 에서 bbox 그릴 때 object_id == -1 이면 그냥 붉은색 bbox 만 그리도록 수정해. 선 굵기도 다르게 해. object_id == -1 이면 기존 굵기, 그렇지 않으면 조금 더 굵게 그려라.

---

현재 track_id == UNTRACKED_OBJECT_ID 일 때 bbox 그리고 있는데, conf 를 %.02f 포맷으로 bbox 위에 출력.
