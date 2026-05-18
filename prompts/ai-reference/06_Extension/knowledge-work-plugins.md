---

Knowledge Work Plugins
Claude를 사용자의 역할, 팀, 회사에 맞춘 전문가로 변신시키는 plugin이다. Claude Cowork용으로 만들어졌으며 Claude Code와도 호환된다.
Why Plugins
Cowork에서는 목표만 설정하면 Claude가 완성된 전문가 수준의 결과물을 제공한다. Plugin은 한 걸음 더 나아가게 해준다: 사용자가 일을 어떻게 처리하길 원하는지, 어떤 도구와 데이터에서 가져올지, 핵심 workflow를 어떻게 처리할지, 어떤 slash command를 노출할지를 Claude에게 알려주어, 팀이 더 우수하고 일관된 결과를 얻도록 한다.
각 plugin은 특정 업무 기능을 위한 skill, connector, slash command, sub-agent를 묶어 제공한다. 기본 상태로도 해당 역할의 누구든 도와줄 수 있는 강력한 출발점을 Claude에게 제공한다. 진정한 위력은 회사에 맞게 — 회사의 도구, 용어, 프로세스로 — 커스터마이징할 때 나오며, 그 결과 Claude가 마치 팀을 위해 만들어진 것처럼 작동한다.
Plugin Marketplace
우리 자신의 업무에서 영감을 받아 만든 11개의 plugin을 오픈소스로 공개한다:

Plugin
How it helps
Connectors

productivity
태스크, 캘린더, 일일 workflow, 개인 컨텍스트를 관리하여 같은 말을 반복하는 시간을 줄여준다.
Slack, Notion, Asana, Linear, Jira, Monday, ClickUp, Microsoft 365

sales
잠재 고객을 조사하고, 통화를 준비하며, 파이프라인을 검토하고, 아웃리치를 초안 작성하며, 경쟁 배틀카드를 만든다.
Slack, HubSpot, Close, Clay, ZoomInfo, Notion, Jira, Fireflies, Microsoft 365

customer-support
티켓을 분류하고, 응답을 초안 작성하며, 에스컬레이션을 패키징하고, 고객 컨텍스트를 조사하며, 해결된 이슈를 지식 베이스 글로 변환한다.
Slack, Intercom, HubSpot, Guru, Jira, Notion, Microsoft 365

product-management
스펙을 작성하고, 로드맵을 계획하며, 사용자 리서치를 종합하고, 이해관계자를 업데이트하며, 경쟁 환경을 추적한다.
Slack, Linear, Asana, Monday, ClickUp, Jira, Notion, Figma, Amplitude, Pendo, Intercom, Fireflies

marketing
콘텐츠를 초안 작성하고, 캠페인을 계획하며, 브랜드 톤을 강제하고, 경쟁사 브리핑을 작성하며, 채널 전반의 성과를 보고한다.
Slack, Canva, Figma, HubSpot, Amplitude, Notion, Ahrefs, SimilarWeb, Klaviyo

legal
계약을 검토하고, NDA를 분류하며, 컴플라이언스를 탐색하고, 리스크를 평가하며, 미팅을 준비하고, 템플릿 기반 응답을 초안 작성한다.
Slack, Box, Egnyte, Jira, Microsoft 365

finance
분개를 준비하고, 계정을 reconcile하며, 재무제표를 생성하고, 변동을 분석하며, 결산을 관리하고, 감사를 지원한다.
Snowflake, Databricks, BigQuery, Slack, Microsoft 365

data
데이터셋을 쿼리, 시각화, 해석한다 — SQL을 작성하고, 통계 분석을 실행하며, 대시보드를 구축하고, 공유 전에 작업을 검증한다.
Snowflake, Databricks, BigQuery, Hex, Amplitude, Jira

enterprise-search
이메일, 채팅, 문서, 위키 어디서든 무엇이든 찾는다 — 회사의 모든 도구에 걸친 단일 쿼리.
Slack, Notion, Guru, Jira, Asana, Microsoft 365

bio-research
전임상 연구 도구와 데이터베이스(문헌 검색, 유전체 분석, 타깃 우선순위 결정)에 연결하여 초기 단계 생명과학 R&D를 가속한다.
PubMed, BioRender, bioRxiv, ClinicalTrials.gov, ChEMBL, Synapse, Wiley, Owkin, Open Targets, Benchling

cowork-plugin-management
조직의 특정 도구와 workflow에 맞춘 새 plugin을 만들거나 기존 plugin을 커스터마이징한다.
—

Cowork에서 직접 설치하거나, GitHub에서 전체 컬렉션을 둘러보거나, 직접 만들어라.
Getting Started
Cowork
claude.com/plugins에서 plugin을 설치하라.
Claude Code
# Add the marketplace first
claude plugin marketplace add anthropics/knowledge-work-plugins

# Then install a specific plugin
claude plugin install sales@knowledge-work-plugins
설치되면 plugin이 자동으로 활성화된다. Skill은 관련 시점에 발동하며, slash command는 세션에서 바로 사용할 수 있다 (예: /sales:call-prep, /data:write-query).
How Plugins Work
모든 plugin은 동일한 구조를 따른다:
plugin-name/
├── .claude-plugin/plugin.json   # Manifest
├── .mcp.json                    # Tool connections
├── commands/                    # Slash commands you invoke explicitly
└── skills/                      # Domain knowledge Claude draws on automatically

Skill은 Claude가 유용한 도움을 주기 위해 필요한 도메인 전문 지식, 모범 사례, 단계별 workflow를 인코딩한다. Claude는 관련 시점에 자동으로 이를 끌어와 사용한다.
Command는 사용자가 명시적으로 트리거하는 동작이다 (예: /finance:reconciliation, /product-management:write-spec).
Connector는 MCP 서버를 통해 — CRM, 프로젝트 트래커, 데이터 웨어하우스, 디자인 도구 등 — 사용자의 역할이 의존하는 외부 도구에 Claude를 연결한다.

모든 구성 요소는 파일 기반이다 — markdown과 JSON, 코드 없음, 인프라 없음, 빌드 단계 없음.
Making Them Yours
이 plugin들은 일반적인 출발점이다. 회사가 실제로 일하는 방식에 맞춰 커스터마이징하면 훨씬 유용해진다:

Swap connectors — .mcp.json을 편집해 특정 도구 스택을 가리키도록 한다.
Add company context — 회사의 용어, 조직 구조, 프로세스를 skill 파일에 넣어 Claude가 회사의 환경을 이해하도록 한다.
Adjust workflows — 교과서가 말하는 방식이 아닌, 팀이 실제로 일하는 방식에 맞춰 skill 지시문을 수정한다.
Build new plugins — cowork-plugin-management plugin을 사용하거나 위 구조를 따라 아직 다루지 않은 역할과 workflow에 대한 plugin을 만든다.

팀이 plugin을 만들고 공유할수록 Claude는 부서 간 전문가가 된다. 정의한 컨텍스트는 모든 관련 상호작용에 반영되므로, 리더와 관리자는 프로세스를 강제하는 데 시간을 덜 쓰고 개선하는 데 더 많은 시간을 쓸 수 있다.
Contributing
Plugin은 단지 markdown 파일이다. repo를 fork하고, 변경 사항을 만들고, PR을 제출하라.
