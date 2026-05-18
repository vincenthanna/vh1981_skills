---

Agent SDK Workshop
Claude Agent SDK로 production agent를 만들기 위한 실습 워크숍 자료.
코드 작성은 필요하지 않다. 스위치를 켜고 끄거나 컴포넌트 목록에서 선택하고 prompt를 작성한다. 나머지는 SDK가 처리한다.

Quick start
# 1. Clone and enter
git clone <repo-url> agent-sdk-workshop
cd agent-sdk-workshop

# 2. Install (Python 3.10+)
pip install -r requirements.txt

# 3. Set your API key
cp .env.example .env
# → edit .env and paste your key after ANTHROPIC_API_KEY=

# 4. Verify everything works
./workshop check
#   (on Windows: python workshop check)

# 5. Run the first exercise
./workshop demo

Structure
01-guided-demo/    One agent, four stages. Flip switches in config.py, re-run, watch it improve.
02-breakouts/      Pick a use case. Assemble an agent from pre-built tools and sub-agents.
extend/            Finished early? Recipes for adding your own tools, sub-agents, and breakouts.
docs/              Cheat sheet, FAQ, troubleshooting.

The ./workshop command
모든 기능에 대한 단일 진입점:

Command
Does

./workshop check
시작 전에 환경을 확인한다 (Python 버전, API key, SDK)

./workshop demo
가이드 데모 agent를 실행한다

./workshop demo --show-prompt
SDK가 모델에 보내는 전체 context를 확인한다

./workshop breakout
사용 가능한 breakout 목록을 표시한다

./workshop breakout <name>
특정 breakout을 실행한다

./workshop reset
모든 메모리 파일을 삭제한다 (초기 상태로 시작)

Windows에서는 앞에 python을 붙인다: python workshop check.

Part 1 — Guided demo
하나의 agent. 하나의 작업. 네 번의 실행. 매 실행 사이에 config.py에서 스위치 하나를 켜고, 같은 작업에서 agent가 점점 더 잘 동작하는 모습을 관찰한다.

Stage
Toggle
SDK primitive
What unlocks

0
(all off)
system_prompt
단순 채팅 — tool도 state도 없음

1
ENABLE_TOOLS
@tool + mcp_servers
agent가 정보를 조회할 수 있음

2
ENABLE_SUBAGENTS
AgentDefinition + Task tool
agent가 전문가에게 위임함

3
ENABLE_MEMORY
hooks + a persistence tool
agent가 재시작 후에도 기억함

→ stage별 진행 가이드는 01-guided-demo/GUIDE.md를 연다.

Part 2 — Breakouts
유스케이스를 선택한다. agent를 조립한다. 사전 제작된 tool 라이브러리(6개 카테고리, 19개 tool)와 6개의 sub-agent를 사용할 수 있다. 각 breakout의 config.py에서 어떤 것을 활성화할지 선택하고 system prompt를 작성한다.

Breakout
Scenario

00-warmup
데모와 동일한 브리핑 작업을 breakout 방식으로 조립

chief-of-staff
이사회 회의 준비, email 초안, 임원 브리핑

customer-support
KB 기반 응답으로 티켓 분류

sre-agent
인시던트 조사 — 배포, 메트릭, 런북을 상호 연관 분석

account-intelligence
갱신 전 계정 리뷰 — 숨은 이탈 리스크를 드러냄

freeform
빈 캔버스 — 자신만의 유스케이스가 있을 때

→ 선택하려면 02-breakouts/README.md를 연다.

Requirements

Python 3.10+ (SDK는 최신 타입 문법을 사용한다)
Anthropic API key
이것이 전부다. 모든 tool은 로컬 mock 데이터로 동작한다 — 외부 서비스도, 추가 자격증명도 필요 없다.

If something breaks

./workshop check를 실행한다 — 대부분의 셋업 문제를 잡아낸다
docs/TROUBLESHOOTING.md를 확인한다
docs/FAQ.md를 확인한다

Going further

extend/ — 자신만의 tool, sub-agent, breakout을 추가하는 레시피
docs/CHEATSHEET.md — 모든 SDK 패턴을 한 페이지에
Claude Agent SDK — SDK 자체, 더 많은 예제 포함
claude-cookbooks / claude_agent_sdk — 더 깊이 있는 레퍼런스 agent들
