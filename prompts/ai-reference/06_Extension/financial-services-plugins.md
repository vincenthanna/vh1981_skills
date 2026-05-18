---

Claude for Financial Services Plugins
Claude를 금융 서비스 — 투자 은행, 주식 리서치, 사모 펀드, 자산 관리 — 전문가로 변신시키는 plugin이다. Claude Cowork용으로 만들어졌으며 Claude Code와도 호환된다.
Why Plugins
Cowork에서는 목표만 설정하면 Claude가 완성된 전문가 수준의 결과물을 제공한다. Plugin은 한 걸음 더 나아가게 해준다: 회사가 분석하는 방식, 어떤 데이터 소스에서 가져올지, 핵심 workflow를 어떻게 처리할지, 어떤 slash command를 노출할지를 Claude에게 알려주어, 팀이 더 우수하고 일관된 결과를 얻도록 한다.
각 plugin은 특정 금융 서비스 workflow를 위한 skill, connector, slash command, sub-agent를 묶어 제공한다. 기본 상태로도 해당 역할의 누구든 도와줄 수 있는 강력한 출발점을 Claude에게 제공한다. 진정한 위력은 회사에 맞게 — 회사의 모델, 템플릿, 프로세스로 — 커스터마이징할 때 나오며, 그 결과 Claude가 마치 팀을 위해 만들어진 것처럼 작동한다.
What is Claude for Financial Services?
Claude for Financial Services는 금융 분석을 위한 전문 capability를 갖춘 Claude for Enterprise 기반의 종합 솔루션이다. 금융 전문가가 매일 사용하는 데이터 소스와 도구에 Claude를 연결하여, 여러 브라우저 탭을 오갈 필요를 없애고 출처 검증을 개선해 수작업 데이터 수집에서 비롯되는 오류 위험을 줄인다.
End-to-End Workflows
이 plugin들은 단순한 포인트 도구 모음이 아니라 — 리서치, 분석, 모델링, 출력 생성 전반에 걸친 완전한 workflow를 가능하게 한다:

Research to Report: MCP 공급자로부터 실시간 데이터를 가져오고, 실적 결과를 분석하며, 출간 가능한 수준의 주식 리서치 리포트를 생성한다 — 단일 세션 내에서 모두 수행
Spreadsheet Analysis: 유사 기업 분석(comps), DCF 모델, LBO 모델을 라이브 수식, 민감도 표, 업계 표준 서식이 포함된 완전한 Excel 워크북으로 구축
Financial Modeling: SEC 공시자료로부터 3-statement 모델을 채우고, 가정을 동종 업계 데이터와 교차 확인하며, 시나리오 스트레스 테스트를 수행한다 — blue/black/green 색상 코딩 규칙 내장
Deal Materials: CIM, teaser, process letter를 초안 작성한 뒤 회사 브랜드 PowerPoint 템플릿으로 피치덱 슬라이드와 strip profile을 생성
Portfolio to Presentation: 기회를 스크리닝하고, 실사 체크리스트를 실행하며, IC memo를 작성하고, 포트폴리오 KPI를 추적한다 — 데이터에서 결과물까지 매끄럽게 이동

각 workflow는 상류의 데이터 소스(MCP 경유)를 하류의 출력(Excel, PowerPoint, Word)에 연결하므로, 컨텍스트 전환 없이 질문에서 완성된 결과물까지 이동할 수 있다.
Plugin Marketplace
financial analysis부터 시작하라 — 공유 모델링 도구와 모든 MCP 데이터 connector를 제공하는 핵심 plugin이다. 그 위에 워크플로에 맞게 Claude의 capability를 강화하는 기능별 plugin을 추가하라.

Plugin
Type
How it helps
Connectors

financial analysis
Core (install first)
comps, DCF 모델, LBO 모델, 3-statement 재무제표를 구축한다. 프레젠테이션을 QC하고 재사용 가능한 PPT 템플릿을 만든다. 공유 기반과 모든 데이터 connector를 제공한다.
Daloopa, Morningstar, S&P Global, FactSet, Moody's, MT Newswires, Aiera, LSEG, PitchBook, Chronograph, Egnyte

investment banking
Add-on
CIM, teaser, process letter를 작성한다. 매수자 리스트를 구축하고, 인수합병 모델을 실행하며, strip profile을 생성하고, 라이브 딜을 마일스톤별로 추적한다.
—

equity research
Add-on
실적 업데이트와 initiating coverage 리포트를 작성한다. 투자 논리를 유지하고, 촉매를 추적하며, 모닝 노트를 초안 작성하고, 새로운 아이디어를 스크리닝한다.
—

private equity
Add-on
딜을 소싱하고 스크리닝하며, 실사 체크리스트를 실행하고, 단위 경제성과 수익률을 분석하며, IC memo를 작성하고, 포트폴리오 회사 KPI를 모니터링한다.
—

wealth management
Add-on
고객 미팅을 준비하고, 재무 계획을 수립하며, 포트폴리오를 리밸런싱하고, 고객 리포트를 생성하며, tax-loss harvesting 기회를 식별한다.
—

41 skills, 38 commands, 11 MCP integrations
Cowork에서 직접 설치하거나, GitHub에서 전체 컬렉션을 둘러보거나, 직접 만들어라.
Partner-Built Plugins
이 plugin들은 데이터 파트너가 직접 만들고 유지보수하며, 그들의 금융 데이터와 분석을 Claude workflow에 곧바로 가져온다.

Plugin
Partner
How it helps

LSEG
LSEG
LSEG 금융 데이터와 분석을 사용해 채권 가격 산정, 수익률 곡선 분석, FX carry trade 평가, 옵션 가치 평가, 매크로 대시보드 구축을 수행한다. 채권, FX, 주식, 매크로를 다루는 8개 command.

S&P Global
S&P Global
S&P Capital IQ 데이터를 활용한 기업 tearsheet, 실적 프리뷰, funding digest를 생성한다. 여러 대상(equity research, IB/M&A, corp dev, sales)을 지원한다.

Getting Started
Cowork
claude.com/plugins에서 plugin을 설치하라.
Claude Code
# Add the marketplace
claude plugin marketplace add anthropics/financial-services-plugins

# Install the core plugin first (required)
claude plugin install financial-analysis@financial-services-plugins

# Then add function-specific plugins as needed
claude plugin install investment-banking@financial-services-plugins
claude plugin install equity-research@financial-services-plugins
claude plugin install private-equity@financial-services-plugins
claude plugin install wealth-management@financial-services-plugins
설치되면 plugin이 자동으로 활성화된다. Skill은 관련 시점에 발동하며, slash command는 세션에서 바로 사용할 수 있다:
/comps [company]                # Comparable company analysis
/dcf [company]                  # DCF valuation model
/earnings [company] [quarter]   # Post-earnings update report
/one-pager [company]            # One-page company profile
/ic-memo [project name]         # Investment committee memo
/source [criteria]              # Deal sourcing
/client-review [client]         # Client meeting prep
How Plugins Work
모든 plugin은 동일한 구조를 따른다:
plugin-name/
├── .claude-plugin/plugin.json   # Manifest
├── .mcp.json                    # Tool connections
├── commands/                    # Slash commands you invoke explicitly
└── skills/                      # Domain knowledge Claude draws on automatically

Skill은 Claude가 전문가 수준의 금융 결과물을 제공하기 위해 필요한 도메인 전문 지식, 모범 사례, 단계별 workflow를 인코딩한다. Claude는 관련 시점에 자동으로 이를 끌어와 사용한다.
Command는 사용자가 명시적으로 트리거하는 동작이다 (예: /comps, /earnings, /ic-memo).
Connector는 MCP 서버를 통해 — 금융 데이터 단말기, 리서치 플랫폼, 문서 관리 등 — 워크플로가 의존하는 외부 데이터 소스에 Claude를 연결한다.

모든 구성 요소는 파일 기반이다 — markdown과 JSON, 코드 없음, 인프라 없음, 빌드 단계 없음.
MCP Integrations
모든 connector는 financial analysis 핵심 plugin에 중앙화되어 있으며 모든 add-on plugin에서 공유된다.

Provider
URL

Daloopa
https://mcp.daloopa.com/server/mcp

Morningstar
https://mcp.morningstar.com/mcp

S&P Global
https://kfinance.kensho.com/integrations/mcp

FactSet
https://mcp.factset.com/mcp

Moody's
https://api.moodys.com/genai-ready-data/m1/mcp

MT Newswires
https://vast-mcp.blueskyapi.com/mtnewswires

Aiera
https://mcp-pub.aiera.com

LSEG
https://api.analytics.lseg.com/lfa/mcp

PitchBook
https://premium.mcp.pitchbook.com/mcp

Chronograph
https://ai.chronograph.pe/mcp

Egnyte
https://mcp-server.egnyte.com/mcp

MCP 접근은 해당 공급자의 구독 또는 API 키가 필요할 수 있다.

Making Them Yours
이 plugin들은 출발점이다. 회사가 실제로 일하는 방식에 맞춰 커스터마이징하면 훨씬 유용해진다:

Swap connectors — .mcp.json을 편집해 특정 데이터 공급자와 내부 도구를 가리키도록 한다.
Add firm context — 회사의 용어, 딜 프로세스, 서식 표준을 skill 파일에 넣어 Claude가 회사의 환경을 이해하도록 한다.
Bring your templates — /ppt-template을 사용해 Claude에게 회사의 브랜드 PowerPoint 레이아웃을 가르쳐, 모든 덱이 스타일 가이드와 일치하도록 한다.
Adjust workflows — 교과서가 말하는 방식이 아닌, 팀이 실제로 분석하는 방식에 맞춰 skill 지시문을 수정한다.
Build new plugins — 위 구조를 따라 아직 다루지 않은 workflow에 대한 plugin을 만든다.

팀이 plugin을 만들고 공유할수록 Claude는 부서 간 전문가가 된다. 정의한 컨텍스트는 모든 관련 상호작용에 반영되므로, 리더는 프로세스를 강제하는 데 시간을 덜 쓰고 개선하는 데 더 많은 시간을 쓸 수 있다.
Contributing
Plugin은 단지 markdown 파일이다. repo를 fork하고, 변경 사항을 만들고, PR을 제출하라. 새 skill이나 plugin의 경우 다음을 포함하라:

명확한 트리거 조건과 workflow 단계가 있는 SKILL.md
사용자가 호출 가능하다면 commands/의 대응 command
새 capability를 추가한다면 업데이트된 plugin manifest

License
Apache License 2.0
Disclaimer
이 plugin들은 금융 workflow를 돕지만 금융 또는 투자 자문을 제공하지 않는다. 결론은 항상 자격 있는 금융 전문가와 검증하라. AI가 생성한 분석은 금융 또는 투자 결정에 의존하기 전에 반드시 금융 전문가의 검토를 거쳐야 한다.
