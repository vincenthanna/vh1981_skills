---
title: PTS correction probe 검증용 check_probe 구현 요청
repo: plusinsight
tags:
  - d-platform
  - pts-correction
  - probe
  - verification
  - deepstream
created_at: '2026-02-13T11:55:04.653Z'
source: claude-code-skill
hostname: mtmc71_yeonhui
---
d-platform/pipeline/components/probes/pts_correction.py 에서 frame_meta.ntp_timestamp 에 제대로 값이 들어가는지 검증하고 싶다.

pts_correction.py probe 함수에서 frame_meta의 source_id 와 frame_num 을 키로 해서 해당 frame_meta의 ntp_timestamp 값을 저장해두고
dsrefiner 직전에 임시로 probe(check_probe) 붙여서 동일 frame_meta가 기대하는 ntp_timestamp 를 가지고 있는지 확인하는 것이다.
여기서 frame_meta 식별하는 키는 source_id 와 frame_num 을 사용한다.

pts_correction.py probe 에서 state_manager 에 값을 저장하고, check_probe 에서 frame_meta에 해당하는 ntp_timestamp 가 있는지 확인하면 된다.
lru를 써서 이미 넘어간 frame_meta의 정보가 계속 남아있지 않도록 한다.

check_probe 에서 문제가 생기면 logger.error 로 알려주기만 하면 된다.
