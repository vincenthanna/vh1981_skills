---

Claude Code 헬스케어 마켓플레이스
임상 시험, 사전 승인 검토, FHIR API 개발 등 헬스케어 워크플로우를 위한 Skills입니다.
빠른 시작
# Add the marketplace
/plugin marketplace add anthropics/healthcare

# Install skills
/plugin install fhir-developer@healthcare
/plugin install prior-auth-review@healthcare
/plugin install clinical-trial-protocol@healthcare
사용 가능한 Skills
FHIR Developer
Plugin ID: fhir-developer@healthcare
리소스 구조, 코딩 시스템(LOINC, SNOMED CT, RxNorm), 검증 패턴을 포함한 HL7 FHIR R4에 대한 전문 지식으로 헬스케어 시스템을 더 빠르게 연결합니다.
요구 사항: 없음

Prior Authorization Review (데모)
Plugin ID: prior-auth-review@healthcare
사전 승인 요청 문서를 분석하고, 초기 확인(NPI, ICD-10, CMS Coverage, CPT)을 수행하며, 의료 필요성에 대한 근거를 요약하는 데모 Skill입니다. 자체 용도에 맞게 커스터마이즈할 수 있습니다.
요구 사항: 없음

Clinical Trial Protocol Generator
Plugin ID: clinical-trial-protocol@healthcare
웨이포인트 기반 아키텍처를 사용하여 의료 기기 또는 의약품에 대한 FDA/NIH 준수 임상 시험 프로토콜을 생성합니다.
요구 사항: scipy와 numpy가 설치된 Python
원격 MCP 서버

MCP 이름
설명
URL

CMS Coverage
CMS Coverage 데이터베이스 접근
https://mcp.deepsense.ai/cms_coverage/mcp

NPI Registry
미국 NPI(National Provider Identifier) 레지스트리 접근
https://mcp.deepsense.ai/npi_registry/mcp

PubMed
PubMed에서 생의학 문헌 검색
https://pubmed.mcp.claude.com/mcp

MCP 플러그인 설치:
claude mcp add-from-marketplace anthropics/healthcare/cms-coverage
claude mcp add-from-marketplace anthropics/healthcare/npi-registry
claude mcp add-from-marketplace anthropics/healthcare/pubmed
라이선스
Skills는 Anthropic의 서비스 약관에 따라 제공됩니다.
