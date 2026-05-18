---

Life Sciences Marketplace for Claude Code
이 마켓플레이스는 생명과학 도구를 위한 MCP(Model Context Protocol) 서버와 skill을 제공한다. 이 plugin들을 설치하면 Claude Code 내에서 직접 전문 연구 및 분석 도구에 접근할 수 있다.
What's included:

MCP Servers: PubMed, BioRender, Synapse 등 외부 서비스에 연결
Skills: Claude의 전문성을 확장하는 도메인별 workflow와 분석 capability

Quick Start
# Add the marketplace
/plugin marketplace add anthropics/life-sciences

# Install MCP servers
/plugin install pubmed@life-sciences
/plugin install biorender@life-sciences
/plugin install synapse@life-sciences
/plugin install wiley-scholar-gateway@life-sciences
/plugin install 10x-genomics@life-sciences

# Install skills
/plugin install single-cell-rna-qc@life-sciences
/plugin install instrument-data-to-allotrope@life-sciences
/plugin install nextflow-development@life-sciences
/plugin install scvi-tools@life-sciences
인증이 필요한 서버(PubMed를 제외한 전부)의 경우, 설치 후 자격 증명을 구성하라:

Claude Code에서 /plugin 입력
"Manage plugins" 선택
설치된 서버 찾기
"Configure" 선택
필요한 자격 증명 입력
Claude Code 재시작

Available Plugins
Remote MCP Servers
PubMed
Plugin ID: pubmed@life-sciences
PubMed의 생물의학 문헌과 연구 논문을 검색하고 접근한다.
Requirements: 없음 — 모든 사용자에게 접근 가능
BioRender
Plugin ID: biorender@life-sciences
과학 일러스트와 다이어그램을 생성하고 접근한다.
Requirements: 무료 BioRender 계정 (https://www.biorender.com)
Synapse.org
Plugin ID: synapse@life-sciences
Sage Bionetworks의 협업 연구 데이터 관리 플랫폼.
Requirements: 무료 Synapse 계정 (https://www.synapse.org)
Scholar Gateway (Wiley)
Plugin ID: wiley-scholar-gateway@life-sciences
Wiley의 Scholar Gateway에서 학술 연구와 출판물에 접근한다.
Requirements: 무료 Scholar Gateway 계정
Local MCP Servers (MCPB)
10x Genomics Cloud
Plugin ID: 10x-genomics@life-sciences
10x Genomics Cloud 분석 데이터와 workflow에 접근한다.
Requirements:

10x Genomics Cloud 계정 (https://www.10xgenomics.com/products/cloud-analysis)
Access token (다음에서 생성: https://cloud.10xgenomics.com/account/security)
참고: 계정에 분석 데이터가 있어야 유용함

Skills
Single-Cell RNA-seq Quality Control
Plugin ID: single-cell-rna-qc@life-sciences
scverse 모범 사례를 따르는 single-cell RNA-seq 데이터를 위한 자동화된 품질 관리 workflow. 종합적인 시각화와 함께 MAD 기반 필터링을 수행한다.
Instrument Data to Allotrope
Plugin ID: instrument-data-to-allotrope@life-sciences
표준화된 데이터 교환 및 분석을 위해 기기 데이터를 Allotrope Simple Model(ASM) 형식으로 변환한다.
Nextflow Development
Plugin ID: nextflow-development@life-sciences
로컬 또는 공개 GEO/SRA 시퀀싱 데이터에 대해 nf-core 생물정보학 파이프라인(rnaseq, sarek, atacseq)을 실행한다. 전문 생물정보학 훈련 없이 대규모 오믹스 분석을 실행해야 하는 실험실 과학자를 위해 설계되었다.
Supported pipelines:

rnaseq: 유전자 발현 및 차등 발현 분석
sarek: 생식세포 및 체세포 변이 호출 (WGS/WES)
atacseq: 염색질 접근성 분석

Features:

GEO/SRA로부터 공개 데이터셋 다운로드
데이터 유형 자동 감지 및 적절한 파이프라인 제안
파이프라인 호환 samplesheet 생성
환경 검증 및 문제 해결 가이드

Requirements: 로컬에 Docker와 Nextflow 설치
scvi-tools
Plugin ID: scvi-tools@life-sciences
scvi-tools를 사용한 single-cell 오믹스 분석을 위한 딥러닝 툴킷. scVI, scANVI, totalVI, PeakVI, MultiVI 등에 대한 모델 선택 가이드, 학습 workflow, 통합 파이프라인을 포함한다.
Detailed Installation
1. Add the marketplace (one time)
/plugin marketplace add https://github.com/anthropics/life-sciences.git
2. Install specific plugins
# Remote MCP servers (no configuration needed for PubMed)
/plugin install pubmed@life-sciences
/plugin install biorender@life-sciences
/plugin install synapse@life-sciences
/plugin install wiley-scholar-gateway@life-sciences

# Local MCP servers (require configuration)
/plugin install 10x-genomics@life-sciences

# Skills (no configuration needed)
/plugin install single-cell-rna-qc@life-sciences
/plugin install instrument-data-to-allotrope@life-sciences
/plugin install nextflow-development@life-sciences
/plugin install scvi-tools@life-sciences
3. Configure credentials (if needed)
인증이 필요한 서버의 경우 /plugin 메뉴를 사용하라:

Claude Code에서 /plugin 입력
"Manage plugins" 선택
설치된 서버 찾기
"Configure" 선택 (사용 가능한 경우)
API 자격 증명 입력

또는 안내가 표시될 때 서버의 웹 인터페이스를 통해 인증한다.
4. Restart Claude Code
MCP 서버를 활성화하려면 재시작한다.
Authentication Requirements

인증 없음: PubMed
무료 계정 필요: BioRender, Synapse, Wiley Scholar Gateway
유료/기관 계정: 10x Genomics (유용하려면 계정에 데이터가 있어야 함)

Support
다음 사안에 대해:

Claude Code plugin 시스템: Anthropic Slack의 #claude-cli-feedback에 신고
개별 MCP 서버: 해당 공급자의 지원에 문의

License
개별 MCP 서버는 각 공급자의 라이선스를 따른다. 자세한 내용은 각 공급자의 서비스 약관을 참조하라.
Removed Plugins

Benchling: Benchling이 plugin 시스템에서 지원되지 않는 테넌트별 URL을 사용하기 때문에 제거됨.
