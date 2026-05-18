## 코드 구조 시각화 prompt

<br>

<br>

# C++ / GStreamer 애플리케이션 구조 시각화

당신은 이 코드베이스를 처음 본 엔지니어에게 30분 안에 전체 구조를 이해시켜야 한다. "파일이 많다"가 아니라 "어떻게 동작하는가"가 보이는 다이어그램을 만들어라.

## 분석 절차

1. 빌드 진입점(`main`, `CMakeLists.txt` 또는 `Makefile`)부터 추적해 실제로 빌드되는 소스 집합을 확정하라.
2. dead code / 미사용 모듈은 회색 처리 또는 제외하고 표시하라.
3. 아래 5개 view를 모두 산출하라. 하나라도 생략하지 말 것.

## 산출물 (모두 mermaid로 출력)

### View 1. 모듈 의존성 그래프

- 노드: 헤더+소스 단위(또는 namespace/디렉토리). 함수 단위 X.
- 엣지: `#include` 또는 호출 방향. 양방향 의존이 있으면 빨간색.
- 외부 라이브러리(GStreamer, OpenCV, CUDA 등)는 별도 그룹으로 묶어 시각적으로 구분.

### View 2. 클래스 다이어그램 (`classDiagram`)

- 주요 클래스의 멤버·메서드와 관계(상속·composition·association)를 표기.
- 단순 POD/struct는 생략하거나 한 박스에 합칠 것.
- 누가 누구의 lifetime을 소유하는지 composition(◆)과 aggregation(◇)으로 구분.

### View 3. GStreamer 파이프라인 그래프 (`graph LR`)

- 코드가 만드는 실제 element 그래프를 그려라.
- 노드 라벨: `<element-name> (<factory>)` 예: `enc (nvv4l2h264enc)`
- 엣지: pad 연결 (`src → sink`). caps 협상이 명시된 곳은 caps도 표기.
- tee / queue / dynamic pad(`pad-added`)로 분기되는 부분은 점선으로.
- 참고: 실제 런타임 그래프는 `GST_DEBUG_DUMP_DOT_DIR=/tmp gst-launch ...` + `dot -Tpng` 으로 검증 가능 — 정적 분석 결과와 차이가 나면 명시하라.

### View 4. 스레드 / 콜백 모델 (`sequenceDiagram` 또는 `flowchart`)

- 어떤 스레드가 존재하는가 (main, GMainLoop, GStreamer streaming thread, appsink callback thread, 자체 워커 등).
- 각 콜백·signal handler가 **어느 스레드에서 호출되는가** 명시.
- shared state가 있다면 어느 스레드가 read/write 하는지 표시.

### View 5. 상태 / 생명주기 (`stateDiagram-v2`)

- `NULL → READY → PAUSED → PLAYING` 전이를 트리거하는 코드 위치.
- EOS, ERROR, 외부 stop 신호 처리 흐름.
- 리소스(파일, GPU 컨텍스트, 네트워크 핸들)의 획득·반납 시점.

## 출력 형식 : 아래의 템플릿 문서를 참고하여 구성된 문서, 그리고 그것을 markdown 파일로 저장한다.

```
## Overview
<코드베이스가 무엇을 하는 앱인지 3문장>

## View 1. Module Dependency
```mermaid
...
```

## View 2. Class Diagram
```mermaid
...
```

## View 3. GStreamer Pipeline
```mermaid
...
```

## View 4. Threading Model
```mermaid
...
```

## View 5. Lifecycle
```mermaid
...
```

## 관찰 사항
- 구조상 눈에 띄는 점, 이상한 점, 정적 분석으로 확정 못 한 부분 등을 bullet로.

```

## 제약

- 추측은 금지. 코드에 근거가 없으면 다이어그램 노드에 `?` 표기하고 "관찰 사항"에 명시하라.
- "전부 다" 그리지 말고 의미 단위로 묶어라. 노드 100개짜리 그래프는 시각화가 아니다.
- 각 다이어그램은 한 화면에 들어와야 한다 (너무 크면 sub-view로 분할).