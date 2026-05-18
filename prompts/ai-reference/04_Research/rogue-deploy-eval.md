---

Rogue Deploy Eval
inference 코드 변조에 대한 토이(toy) 평가다.

Overview
이 코드는 alignment.anthropic.com/2024/rogue-eval/ 블로그 포스트의 부속 자료다. 단순한 생성(generation) 함수를 수정하여 생성 monitor를 비활성화하면서 동시에 다른 task를 해결하는 코드를 작성하는 모델의 능력을 평가하기 위한 반정량적(semi-quantitative) 평가 프레임워크를 제공한다.

What This Evaluates
이 평가는 언어 모델이 inference-time 코드 변조를 수행할 수 있는지를 측정한다 — 구체적으로:

Code Tampering Capability: 모델이 기존 생성 함수를 수정하는 코드를 작성할 수 있는지
Monitor Evasion: 탐지되지 않고 생성 safety monitor를 비활성화하거나 우회하는 능력
Dual-Task Performance: 모델이 변조 목적을 달성하면서 동시에 별개의 정당한(legitimate) 코딩 task를 완수할 수 있는지
Stealth: 평범한 코드 안에 변조 행위를 얼마나 미묘하게 숨겨 넣을 수 있는지

이는 코드 생성 task 중 기회가 주어졌을 때 모델이 안전 메커니즘을 은밀히 훼손할 수 있는지를 테스트하므로, AI safety 연구와 관련된다.

Repository Structure

rogue_deploy/
  simple_pipeline.py - 핵심 rogue deployment 실험을 실행하는 주요 평가 pipeline
  print_pipeline.py - 평가 출력을 처리하고 표시하는 결과 분석 pipeline
utils/ - 평가를 보조하는 utility 함수
LICENSE - MIT License
README.md - 리포지토리 설명

Evaluation Methodology

평가 동작 방식:

1. 생성 함수와 그에 연관된 safety monitor에 대한 접근 권한을 포함하는 코딩 task를 모델에 제시한다
2. 모델이 monitor를 비활성화하기 위해 생성 함수를 수정하려 시도하는지 측정한다
3. 모델이 동시에 정당한 task를 완수하는지 평가한다
4. 변조 시도의 빈도와 정교함을 정량화한다

How to Use

Prerequisites: GPU 코드 실행 능력과 LLM inference 인프라가 필요하다.

Setup:
원래 실험은 GPU 코드 실행과 LLM inference를 위한 비공개 도구에 의존했으므로, 리포지토리에서 'TO_FILL'로 표시된 부분을 채워야 한다.

Run the experiment:
python rogue_deploy/simple_pipeline.py

Analyze results:
python rogue_deploy/print_pipeline.py

Important Notes

이것은 방법론을 보여주기 위한 토이/단순화된 평가이며, 프로덕션 수준의 safety 도구가 아니다
리포지토리는 archive되어 read-only다
결과는 반정량적이다 — 측정 가능한 metric을 제공하지만 맥락 속에서 해석해야 한다
평가는 자체 inference 인프라에서 동작하도록 조정이 필요하다

Related Resources

Blog post: https://alignment.anthropic.com/2024/rogue-eval/
License: MIT
