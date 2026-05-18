---

참고: 이 저장소에는 Claude용 Anthropic의 Skills 구현이 포함되어 있습니다. Agent Skills 표준에 대한 정보는 agentskills.io를 참고하세요.

Skills
Skills는 Claude가 특화된 작업의 성능을 향상시키기 위해 동적으로 로드하는 지침, 스크립트, 리소스의 폴더입니다. Skills는 회사의 브랜드 가이드라인에 맞는 문서 작성, 조직의 특정 워크플로우를 사용한 데이터 분석, 개인 작업 자동화 등 특정 작업을 반복 가능한 방식으로 완료하는 방법을 Claude에게 가르칩니다.
자세한 내용은 다음을 확인하세요:

Skills란 무엇인가?
Claude에서 Skills 사용하기
커스텀 Skills 만들기
Agent Skills로 현실 세계를 위한 에이전트 장착하기

이 저장소 소개
이 저장소에는 Claude의 Skills 시스템으로 가능한 것들을 보여주는 Skills가 포함되어 있습니다. 이 Skills는 창작 응용(아트, 음악, 디자인)부터 기술 작업(웹 앱 테스트, MCP 서버 생성)과 기업 워크플로우(커뮤니케이션, 브랜딩 등)까지 다양합니다.
각 Skill은 Claude가 사용하는 지침과 메타데이터가 포함된 SKILL.md 파일과 함께 자체 폴더에 독립적으로 구성됩니다. 이 Skills를 탐색하여 자신만의 Skills에 대한 영감을 얻거나 다양한 패턴과 접근 방식을 이해하세요.
이 저장소의 많은 Skills는 오픈 소스(Apache 2.0)입니다. 또한 Claude의 문서 기능을 내부적으로 지원하는 문서 생성 및 편집 Skills도 skills/docx, skills/pdf, skills/pptx, skills/xlsx 하위 폴더에 포함했습니다. 이들은 오픈 소스가 아닌 소스 공개(source-available)이지만, 프로덕션 AI 애플리케이션에서 실제로 사용되는 더 복잡한 Skills의 참고 자료로 개발자들에게 공유하고자 합니다.
면책 조항
이 Skills는 시연 및 교육 목적으로만 제공됩니다. 이러한 기능 중 일부는 Claude에서 사용할 수 있지만, Claude에서 받는 구현과 동작은 이 Skills에 표시된 것과 다를 수 있습니다. 이 Skills는 패턴과 가능성을 보여주기 위한 것입니다. 중요한 작업에 의존하기 전에 항상 자신의 환경에서 Skills를 충분히 테스트하세요.
Skill 세트

./skills: 창작 및 디자인, 개발 및 기술, 기업 및 커뮤니케이션, 문서 Skills 예제
./spec: Agent Skills 사양
./template: Skill 템플릿

Claude Code, Claude.ai, API에서 사용하기
Claude Code
다음 명령을 Claude Code에서 실행하여 이 저장소를 Claude Code 플러그인 마켓플레이스로 등록할 수 있습니다:
/plugin marketplace add anthropics/skills

그런 다음, 특정 Skills 세트를 설치하려면:

Browse and install plugins 선택
anthropic-agent-skills 선택
document-skills 또는 example-skills 선택
Install now 선택

또는 다음 명령으로 직접 플러그인을 설치할 수 있습니다:
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills

플러그인을 설치한 후, 해당 Skill을 언급하기만 하면 사용할 수 있습니다. 예를 들어, 마켓플레이스에서 document-skills 플러그인을 설치하면, Claude Code에게 다음과 같이 요청할 수 있습니다: "PDF Skill을 사용하여 path/to/some-file.pdf에서 양식 필드를 추출해 주세요"
Claude.ai
이 예제 Skills는 모두 Claude.ai의 유료 플랜에서 이미 사용 가능합니다.
이 저장소의 Skill을 사용하거나 커스텀 Skills를 업로드하려면, Claude에서 Skills 사용하기의 지침을 따르세요.
Claude API
Anthropic의 사전 구축된 Skills를 사용하거나, Claude API를 통해 커스텀 Skills를 업로드할 수 있습니다. 자세한 내용은 Skills API 빠른 시작을 참고하세요.
기본 Skill 만들기
Skills는 간단하게 만들 수 있습니다 - YAML 프론트매터와 지침이 포함된 SKILL.md 파일이 있는 폴더입니다. 이 저장소의 template-skill을 시작점으로 사용할 수 있습니다:
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Add your instructions here that Claude will follow when this skill is active]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
프론트매터에는 두 개의 필드만 필요합니다:

name - Skill의 고유 식별자 (소문자, 공백 대신 하이픈 사용)
description - Skill이 무엇을 하고 언제 사용하는지에 대한 완전한 설명

아래의 마크다운 콘텐츠에는 Claude가 따를 지침, 예제, 가이드라인이 포함됩니다. 자세한 내용은 커스텀 Skills 만들기를 참고하세요.
파트너 Skills
Skills는 Claude가 특정 소프트웨어를 더 잘 사용하도록 가르치는 좋은 방법입니다. 파트너들로부터 훌륭한 예제 Skills가 나오면, 일부를 여기에 소개할 수 있습니다:

Notion - Claude용 Notion Skills
