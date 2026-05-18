---

Claude Code Action
GitHub PR와 issue에서 사용할 수 있는 범용 Claude Code action으로, 질문에 답하고 코드 변경을 구현할 수 있다. 이 action은 workflow 컨텍스트에 따라 활성화 시점을 지능적으로 감지한다—@claude 멘션 응답, issue 할당, 또는 명시적 prompt를 사용한 자동화 작업 실행 등에 대응한다. Anthropic 직접 API, Amazon Bedrock, Google Vertex AI, Microsoft Foundry를 포함한 다양한 인증 방식을 지원한다.
Features

🎯 지능형 모드 감지: workflow 컨텍스트에 따라 적절한 실행 모드를 자동 선택한다—별도 설정 불필요
🤖 인터랙티브 코드 어시스턴트: Claude가 코드, 아키텍처, 프로그래밍에 관한 질문에 답할 수 있다
🔍 코드 리뷰: PR 변경 사항을 분석하고 개선점을 제안한다
✨ 코드 구현: 간단한 수정, 리팩토링, 그리고 신규 기능까지 구현할 수 있다
💬 PR/Issue 통합: GitHub 코멘트 및 PR 리뷰와 매끄럽게 연동된다
🛠️ 유연한 도구 접근: GitHub API와 파일 작업에 접근할 수 있다 (추가 도구는 설정을 통해 활성화 가능)
📋 진행 상황 추적: Claude가 작업을 완료함에 따라 동적으로 갱신되는 체크박스 형식의 시각적 진행 표시
📊 구조화된 출력: 복잡한 자동화를 위해 검증된 JSON 결과를 자동으로 GitHub Action 출력으로 변환한다
🏃 자체 인프라에서 실행: action은 전적으로 사용자의 GitHub runner에서 실행된다 (Anthropic API 호출은 선택한 provider로 전송됨)
⚙️ 간소화된 설정: 통합된 prompt와 claude_args 입력으로 Claude Code SDK와 정렬된 깔끔하고 강력한 설정을 제공한다

📦 v0.x에서 업그레이드 중인가?
v1.0으로 workflow를 갱신하는 단계별 안내는 Migration Guide를 참조한다. 새 버전은 대부분의 기존 설정과 호환성을 유지하면서 설정을 간소화한다.
Quickstart
이 action을 설정하는 가장 쉬운 방법은 터미널에서 Claude Code를 사용하는 것이다. claude를 열고 /install-github-app을 실행하기만 하면 된다.
이 명령은 GitHub 앱과 필수 secret 설정 과정을 안내한다.
참고:

GitHub 앱을 설치하고 secret을 추가하려면 반드시 저장소 admin이어야 한다
이 quickstart 방법은 Anthropic API 직접 사용자에게만 제공된다. AWS Bedrock, Google Vertex AI, Microsoft Foundry 설정은 docs/cloud-providers.md를 참조한다.

📚 Solutions & Use Cases
특정 자동화 패턴을 찾고 있는가? 완전한 작동 예시를 포함한 Solutions Guide를 확인한다:

🔍 자동 PR 코드 리뷰 - 전체 리뷰 자동화
📂 경로별 리뷰 - 핵심 파일 변경 시 트리거
👥 외부 기여자 리뷰 - 신규 기여자에 대한 특별 처리
📝 커스텀 리뷰 체크리스트 - 팀 표준 강제 적용
🔄 예약된 유지보수 - 자동화된 저장소 상태 점검
🏷️ Issue 분류 및 라벨링 - 자동 카테고리화
📖 문서 동기화 - 코드 변경에 맞춰 문서 유지
🔒 보안 중심 리뷰 - OWASP에 정렬된 보안 분석
📊 DIY 진행 추적 - 자동화 모드에서 추적 코멘트 생성

각 솔루션에는 완전한 작동 예시, 설정 세부 사항, 예상 결과가 포함되어 있다.
Documentation

Solutions Guide - 🎯 바로 사용 가능한 자동화 패턴
Migration Guide - ⭐ v0.x에서 v1.0으로 업그레이드
Setup Guide - 수동 설정, 커스텀 GitHub 앱, 보안 모범 사례
Usage Guide - 기본 사용법, workflow 설정, 입력 파라미터
Custom Automations - 자동화된 workflow 및 커스텀 prompt 예시
Configuration - MCP 서버, 권한, 환경 변수, 고급 설정
Experimental Features - 실행 모드 및 네트워크 제한
Cloud Providers - AWS Bedrock, Google Vertex AI, Microsoft Foundry 설정
Capabilities & Limitations - Claude가 할 수 있는 것과 할 수 없는 것
Security - 접근 제어, 권한, commit 서명
FAQ - 자주 묻는 질문 및 문제 해결

📚 FAQ
문제가 있거나 질문이 있는가? 자주 묻는 문제에 대한 해결책과 Claude의 기능 및 한계에 대한 상세한 설명은 Frequently Asked Questions를 확인한다.
License
이 프로젝트는 MIT License로 라이선스가 부여된다—자세한 내용은 LICENSE 파일을 참조한다.
