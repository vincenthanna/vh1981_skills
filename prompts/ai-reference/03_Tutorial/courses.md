---

Anthropic Courses
Anthropic의 교육 과정에 오신 것을 환영한다. 이 repo는 현재 다섯 개의 과정을 포함하며, 모두 실습 연습이 포함된 Jupyter Notebook으로 제공된다. 다음 순서로 과정을 완료할 것을 권장한다:

1. Anthropic API Fundamentals
Claude SDK 사용의 기본을 가르친다.
배우게 될 내용:
- API key 발급 및 환경 셋업
- 모델 파라미터 사용 (temperature, max tokens 등)
- 멀티모달 prompt 작성 (텍스트 및 이미지)
- 실시간 출력을 위한 응답 streaming
- Messages API 구조와 응답 형식 이해
사전 요구사항: 기본적인 Python 지식. AI/ML 경험은 필요하지 않다.
디렉터리: anthropic_api_fundamentals/

2. Prompt Engineering Interactive Tutorial
핵심 prompting 기법에 대한 종합적인 단계별 가이드.
배우게 될 내용:
- Role prompting과 system prompt
- Chain-of-thought 추론
- 예제를 활용한 few-shot prompting
- 복잡한 작업을 위한 prompt chaining
- 구조화된 prompt를 위한 XML 태그
- 환각(hallucination)을 줄이고 정확도를 높이는 기법
사전 요구사항: 과정 1 완료 또는 Claude API에 대한 기본적인 친숙도.
디렉터리: prompt_engineering_interactive_tutorial/
대체 버전: AWS 호스팅 환경용 AWS Workshop 버전 제공.

3. Real World Prompting
복잡한 실제 애플리케이션에 prompting 기법을 통합하는 방법을 배운다.
배우게 될 내용:
- production prompt에서 여러 prompting 기법 결합
- 모호하거나 복잡한 사용자 입력 처리
- 특정 유스케이스(요약, 분석, 생성)를 위한 prompt 구축
- prompt 디버깅과 반복 개선
- production 시스템에서 prompt 설계 모범 사례
사전 요구사항: 과정 1과 2 완료.
디렉터리: real_world_prompting/
대체 버전: Google Vertex 버전 제공.

4. Prompt Evaluations
prompt 품질을 측정하기 위한 production prompt evaluation 작성법을 배운다.
배우게 될 내용:
- prompt 품질 평가 기준 설계
- 자동화된 평가 스크립트 작성
- 정확도, 일관성, 관련성 측정
- 다양한 prompt 전략의 A/B 테스트
- 지속적인 개선을 위한 평가 pipeline 구축
사전 요구사항: 과정 1-3 완료.
디렉터리: prompt_evaluations/

5. Tool Use
Claude를 사용한 workflow에서 tool use를 성공적으로 구현하기 위해 알아야 할 모든 내용을 가르친다.
배우게 될 내용:
- JSON schema로 tool 정의
- tool use 응답과 tool 결과 처리
- 여러 tool을 활용한 agentic workflow 구축
- tool use 시나리오에서 에러 처리
- tool 설계 및 설명 작성의 모범 사례
사전 요구사항: 과정 1 완료 또는 Claude API에 대한 친숙도.
디렉터리: tool_use/

Getting Started

repo를 clone한다:
git clone https://github.com/anthropics/courses.git

의존성을 설치하고 ANTHROPIC_API_KEY 환경 변수를 설정한 후, 각 과정 디렉터리의 Jupyter notebook을 연다.

참고: 이 과정들은 자료를 따라 진행하는 학생들의 API 비용을 낮추기 위해 종종 가장 저렴한 모델(Claude 3 Haiku)을 우선 사용한다. 원한다면 다른 Claude 모델을 자유롭게 사용할 수 있다.

Language: Jupyter Notebook
License: repo의 LICENSE 파일을 참고하라.
