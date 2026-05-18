아래 과정을 통해 이번 PR의 동작을 검증한다.

<br>

## Jobs

* * *

<br>

run\_name : “pr\_on\_site\_test”

<br>

PR : **“PII-2203** Default PA/ReID inference to every frame**”**

<br>

#### **목적**

- PR 이전/이후의 동작을 비교하여 문제없이 동작하는지를 확인한다.

<br>

중요 : 컨테이너 컨트롤 관련 방법은 아래 “원격 테스트 rule” 내용 참고

<br>

상수 선언 :

- **실행시간** : 5분
- **Target 장비** : DS48

<br>

#### 작업순서

- 나열한 조건들 각각에 대해 다음 과정들을 순서대로 수행한다. 작업은 순차적으로 해야 하고, 조건별로 따로따로 돌려야지 병렬로 돌려서는 안된다.
    - 조건들 리스트
        - **Before PR**
            - target 장비 : <<<Target 장비>>>
            - 원격 sync 모드 명시 규칙 : ref-only
                - **Ref:** 2e05c1338eb27eb75bad28fa3064067027e5cddb
            - 다음 이름의 view는 15fps, 그 외 카메라는 3fps 로 설정한다.
                - **192.168.0.103, 192.168.0.106, 192.168.0.107, 192.168.0.111**
            - pa\_reid 모델 사용 : `pa_reid_resnet50_swin_160x320_onnx`
            - pipeline.pedestrian\_attribute 의 interval은 0으로 설정
        - **After PR**
            - target 장비 : <<<Target 장비>>>
            - 원격 sync 모드 명시 규칙 : ref-only
                - **Ref:** 671a0e1e2b44843f15456317b4848bbf653b13c2
            - 다음 이름의 view는 15fps, 그 외 카메라는 3fps 로 설정한다.
                - **192.168.0.103, 192.168.0.106, 192.168.0.107, 192.168.0.111**
            - pa\_reid 모델 사용 : `pa_reid_resnet50_swin_160x320_onnx`
            - pipeline.pedestrian\_attribute 의 interval은 0으로 설정

    - 주의사항
        - 테스트 전에 user\_config.yaml 파일을 꼭 확인해서 제대로 설정이 되었는지 한번 더 체크한다.

<br>

  **과정:**

1. 소스 초기화하기 - 아래 단계로 실행하면 소스 동영상이 다시 처음부터 송출된다. -> 각각의 조건마다 항상 처음부터 수행해야 한다.
    1. 다음 명령으로 접속 : ssh [yeonhui@192.168.49.53](mailto:yeonhui@192.168.49.53)
    2. 디렉토리 이동     : cd /home/yeonhui/recorder7
    3. 명령 실행        : ./play.sh
    4. ssh 연결 끊기.
2. 1번 동작 이후 60초 정도 대기한다.
3. fps 변경(rule의 방법대로) 혹은 조건 적용
4. target 장비로 tsh로 접속한다.
    - 거기 plusinsight-dplatform-1 컨테이너가 있다.
5. `~/plusinsight` 로 이동을 해서 dplatform 도커를 내렸다가 올린다.(cleanup과정)
    ```bash
    docker compose down dplatform;docker compose up -d dplatform
    ```
6. 새로 시작된 plusinsight-dplatform-1 컨테이너의 데이터를 업데이트해야 한다.
    - **“조건들”** 에서 **“원격 sync 모드 명시 규칙”** 내용대로 rule의 “적용방법.컨테이너 업데이트" 항목을 적용한다.
    - 이 단계에서 fps 변경을 실제로 했든, 아니든 baseline 일치 여부와 무관하게 항상 mediaserver/mediamtx를 재시작한다
        - fps 변경이 필요해서 했다면 항상 mediaserver/mediamtx 재시작을 해야한다.
        - fps 읽어서 값을 변경할 필요가 없어도 mediaserver/mediamtx 재시작 해야한다.
            - 값만 바뀌고 실제 적용이 되지 않았을 가능성이 있다.
7. 컨테이너에서 “python3 app.py” 실행한다. - 시작시간 기록(start\_time)
    - 시작 전에 이전에 혹시 돌린 것이 살아있는지 꼭 확인하고, 떠있으면 먼저 죽이고 시작한다.
8. 위에 선언된 “상수 선언.실행 시간" 동안 실행(대기)
    - 실행하면서 기대하는 fps 가 잘 유지가 되는지도 check해 본다.
9. 종료 시간 기록(end\_time)
10. raw 처리를 해야 하므로 1분 30초 정도 추가 대기
11. 실행 시간(start\_time ~ end\_time) 동안 “동선 길이 측정" 수행 (rule 참고)
12. [app.py](https://app.py "https://app.py") 확실히 종료(죽인다.)
13. 마무리
    - 정리(필요시, 할것이 있다면)
    - 데이터 추출

- 각각의 조건에 대해 다 끝나면 보고하고 markdown문서로도 작성한다.

<br>

**평가 기준 <중요!>**

- **기본 평가 기준**
    - fps
        - 원하는 fps가 나왔는가.
        - 실제 모든 처리 완료 후 찍히는 fps :
            - `Fps of view: <<<view_name>>> is <<<fps>>>` 

    - **vision / raw** 
        - 데이터가 꾸준히 생성 되었는가.
        - 갯수들을 세보자
    - **동선 길이 측정**
        - rule의 “동선 길이 측정” 참고해서 평가
        - 평가기준
            - 기존과 별 차이 없거나, 3% 정도의 감소는 acceptable.

    - 로그에 에러 발생하였는지 여부
    - cpu/gpu 점유율
        - gpu 점유율은 nvidia-smi 사용하기
        - 평가 기준
            - [app.py](https://app.py "https://app.py") 구동기간동안 평균 점유율
            - 전체 cpu 점유율
            - gpu 점유율
        - 문제상황
            - 모두 100%로 차면서 처리되는 fps가 줄어들면 문제가 된다.

- **PR 수정 내용에 따른 동작 평가 - <중요!>**
    - PR 수정 내용애 따른 정상적으로 동작하는지 평가하는 항목들을 생성해서 추가한다.
    - 평가 항목 생성 가이드라인 :
        - **“After PR”** 적용한 상태에서 전체적으로 정상동작하는지 확인 및 추가한 기능이 정상적으로 동작하는지를 확인해야 한다.

- 사용자 요청 사항
    - 여기서는 기본으로 모든 frame 에 pa/reid 발생하는지만 check하면 된다. **클러스터링 동작 검증은 제외한다.**

<br>

## 원격 테스트 rule

* * *

<br>

원격 d-platform 도커 컨테이너에 현재 repo에 포함된 python 소스 및 새로 빌드한 플러그인들을 다음 teleport resource에 동기화 식으로 옮겨서 돌려보려고 한다.

연결은 tsh 설정을 해 두었다. teleport 접속하면 된다.

- 이름 : “조건들" 에서 “target 장비” 로 전달된다.
- 로그인 계정 : yeonhui
- 도커 컨테이너 이름 : plusinsight-dplatform-1
- 연결은 모두 tsh 만 사용한다.
    - 파일 복사도 tsh scp 만 사용

<br>

**적용방법**

- 기존 프로세스 정리
    - 컨테이너에서 이미 app.py가 돌고 있으면 포트 충돌(8080) 발생하므로 기존 실행 중인 “python3 [app.py](https://app.py "https://app.py")“ 있으면 먼저 종료
- 컨테이너 업데이트
    - 현재 d-platform 디렉토리에 존재하는 repo에 포함되는 python 코드와 cpp plugin .so 파일을 원격 컨테이너에 설치해야 한다.
        - repo에 포함되지 않은(테스트용으로 만든 코드들, 문서들 등) 파일들은 절대로 옮기지 않는다.
        - 파일이 중복되지 않도록 복사 위치를 확실히 확인한다.
            - ./d-platform 은 컨테이너의 /app/mtmc 와 동일 위치이다. 동일 위치 기준으로 대부분의 파일이 overwrite될 것이다. (새로 추가된 파일 제외)
        - cpp 플러그인 so 파일은 플러그인 Makefile의 install 항목을 보면 설치 위치를 알 수 있다.
        - cpp 플러그인 쪽 변경이 없어도 일단 모든 플러그인 빌드 후 .so 파일을 설치한다. **<중요! 원격 컨테이너가 좀 오래되었을 수도 있기 때문이다.>**
        - yaml 파일 등 설정 관련 파일들은 모두 제외
        - 새로 생성한 파일들도 누락하지 말고 복사해야 한다.
            - 새로 생성한 파일들 중 repo에 포함시킨것들만. commit 에서 누락하는 실수도 발견을 꼭 해야 한다.
        - 복사 후 pyc 캐시 모두 정리
        - 정말 정말 중요 ! : config.yaml 파일도 복사해야 하는데, repo에 존재하는 버전으로 넣어야 한다. 내가 테스트 용으로 고친 내용들은 절대 옮겨서는 안된다.
            - 그냥 config.yaml 파일을 복사해서는 안되고!, commit 된 것 기준으로 가져가야 한다. 절대로 수정된 config.yaml 그대로 가져가서는 안된다!
        - “조건들” 에 명시된 config 설정 요청 값들은 `/app/mtmc/configs/user_config.yaml` 에 설정한다.
            - 모두 설정 후 한번 더 조건들에 명시된 config 설정 요청과 일치하는지 꼭 확인한다.
        - `python3 app.py`  실행하면 출력 중에 config 값들도 출력을 한다. 거기를 보고 요청된 설정 요청이 제대로 설정되었는지 검증한다.

- 수정한 플러그인은 빌드한 후에 나온 so 파일을 컨테이너에 설치
    - 플러그인 Makefile에 설치 위치 있음
    - 모든 플러그인을 항상 컨테이너에 설치하자.
- 원격 컨테이너 /app/mtmc 에서 직접 “python3 app.py” 실행시, 수정 내용에 문제가 없으면 정상적으로 실행되어야 한다.
    - 정상 판단기준
        - 전체 view에 대한 fps가 출력이 되어야 한다.
        - 클러스터링 동작에 특별한 문제가 없어야 한다.
        - 도커 로그에 에러가 출력되어서는 안된다.

- 문제 발생시
    - 상세히 보고한다.
    - 테스트에 의미가 없다고 판단되면(조건이 너무 모호) 중단하고 어떻게 고치면 좋을지 제안도 해라.

<br>

**clickhouse 정보**

- 원격의 clickhouse db 에서 설정변경 가능하다.
    - view fps가 camera 테이블에 meta 칼럼에 setFPS로 들어 있다.

<br>

**fps 변경 과정 - 필요시**

아래의 과정을 순서대로 한다.

    1. clickhouse db의 camera 테이블에 meta 칼럼에 setFPS로 들어 있다. 이 값들을 변경한다.
        - setFPS 의 값을 “3” 이렇게 문자열로 저장해서는 절대로 안된다!
            - 숫자로 저장해야 한다.

    2. 원격서버의 ~/plusinsight 로 이동해서 mediaserver와 mediamtx 재시동
        - docker compose restart mediaserver; docker compose restart mediamtx
        - 변경후 항상 mediaserver 와 mediamtx를 재시작 해야 한다.

<br>

**설정 변경 과정 - 필요시**

**configs/user\_config.yaml에 수정하려는 값들을 설정한다.**

<br>

**동선 길이 측정**

- /home/yeonhui/TRACK\_LENGTH\_ANALYSIS.md 문서에 상세 내용이 들어 있다.
- 추가 요청사항
    - 데이터는 잘 보관한다. 키는 “run\_name” 과 실행시간을 조합해서 관리하자.
        - 새로운 관점으로 다시 비교를 해야 할 수 있으므로 사용한 raw값을 csv 파일로 잘 추출해두자.
        - 네가 필요하다고 판단하여 저장하는 데이터에 시간 동안의 vision/raw 테이블 데이터가 포함되어야 한다.

<br>

<br>

* * *

<br>

* * *

<br>

* * *

<br>
<br>

### \[CRITICAL — 원격 sync 모드 명시 규칙\]

```bash
원격으로 보내는 파일은 다음 4가지 모드 중 하나로 명시한다.
prompt에 "Sync mode:" 줄이 없으면 기본값은 "ref-only / Ref: HEAD" (가장 안전).

──────────────────────────────────────────────────────────────────
모드 1) ref-only        (기본값. production 회귀 검증, 특정 commit/branch/tag 검증)
  - 모든 파일을 지정한 git ref에서만 추출
  - working dir의 어떤 변경도 보내지 않음
  - "Ref:" 줄로 ref를 지정 (없으면 HEAD)
  - 명령:
      git fetch origin <branch>     # ref가 origin/<branch>일 때 선행
      git archive <ref> --format=tar.gz <paths> -o /tmp/sync.tar.gz
  - 빌드 입력도 git archive 펼친 임시 디렉토리에서만 수행
  - sync 직전 'git rev-parse <ref>' + 'git log -1 --oneline <ref>' 출력해 시점 확인 보고

모드 2) ref+override    (ref 기준이지만 일부 파일만 working dir 사용)
  - "Ref:" 줄로 base ref 지정 (없으면 HEAD)
  - "Override files:" 줄로 working dir에서 가져올 파일 경로 명시
  - 명시된 파일만 working dir에서, 나머지는 ref에서
  - 사용 예: 1줄짜리 hot-fix 검증, 미커밋 가설 실험
  - 명령:
      git archive <ref> --format=tar.gz <paths> -o /tmp/base.tar.gz
      # 그 위에 override 파일들만 working dir에서 덮어쓰기
  - sync 직후 override된 파일과 base의 md5 차이를 출력해 사용자 확인 보고

모드 3) working-dir     (현재 dev 상태 그대로 검증)
  - 명시적으로 "Sync mode: working-dir" 라고 적혀있을 때만 허용
  - 모든 working dir 변경(staged, unstaged, tracked-file의 미커밋 수정 포함)이 sync됨
  - 사용 예: 진행 중인 큰 작업의 통합 테스트, 여러 파일 동시 실험
  - sync 직전 git status 출력 + 보낼 파일 diff 요약 보고
  - 사용자 확인 받고 진행

모드 4) custom          (드물게 사용. 파일별 출처가 다 다를 때)
  - prompt에 "Source map:" 표로 파일별 출처(ref/working) 지정
  - 각 항목은 path → ref 또는 path → working-dir
  - 사용 예: "config는 v3.5.9 태그에서, 코드는 HEAD에서, debug_logger는 working dir"

──────────────────────────────────────────────────────────────────

[Pre-sync sanity check — 모든 모드 공통]
실제 sync 명령 실행 전에 한 번:

  ref-only / ref+override:
    git rev-parse <ref> && git log -1 --oneline <ref>   # 시점 확정 보고
    git status --short                                   # working dir 상태 보고
  working-dir:
    git status --short + 보낼 파일 git diff 요약
  custom:
    Source map의 각 ref 시점 보고

LLM은 사용자에게 1줄 요약 보고 후 진행 (예: "ref-only mode at 250ff35b7 (PII-2176 head):
                                              128 .py + 7 .so + config.yaml from this commit,
                                              working-dir 수정 3건은 무시")

[Post-sync verification — 모든 모드 공통]
컨테이너에 docker cp 후:

  docker exec <ct> md5sum <synced files>  vs.  로컬에서 의도한 source의 md5
  불일치 시 즉시 보고하고 다음 단계 진행 금지

[빌드 input은 sync 모드에 따름]
- ref-only / ref+override → 빌드 input도 같은 ref (또는 ref+override 그대로)
- working-dir            → 빌드 input도 working dir
- custom                 → Source map에 따름
- 절대로 sync 모드와 빌드 input이 어긋나면 안됨

```