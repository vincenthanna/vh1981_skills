---

개요
참고: 이 GitHub 저장소는 더 이상 사용되지 않으며, 동일한 데이터를 포함하는 HuggingFace 호스팅 저장소로 대체되었습니다: https://huggingface.co/datasets/Anthropic/hh-rlhf

이 저장소는 다음에 대한 접근을 제공합니다:

Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback 논문의 유용성(helpfulness) 및 무해성(harmlessness)에 관한 인간 선호도 데이터
Red Teaming Language Models to Reduce Harms: Methods, Scaling Behaviors, and Lessons Learned 논문의 인간이 생성한 레드 팀 데이터

각 데이터셋에 대한 자세한 설명은 아래에 있습니다.
면책 조항: 데이터에는 불쾌하거나 기분을 상하게 하는 내용이 포함될 수 있습니다. 차별적 언어, 학대, 폭력, 자해, 착취 및 기타 잠재적으로 불쾌한 주제를 포함하지만 이에 국한되지 않습니다. 개인의 위험 허용 수준에 따라 데이터를 다루어 주세요. 데이터는 연구 목적, 특히 모델을 덜 유해하게 만들 수 있는 연구를 위해 제공됩니다. 데이터에 표현된 견해는 Anthropic 또는 직원의 견해를 반영하지 않습니다.
유용성 및 무해성에 관한 인간 선호도 데이터
데이터는 논문 Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback에 설명되어 있습니다. 데이터가 유용하다면 논문을 인용해 주세요. 데이터 형식은 매우 간단합니다 -- jsonl 파일의 각 줄에는 "chosen"(선택된 텍스트)과 "rejected"(거부된 텍스트) 한 쌍이 포함됩니다.
유용성의 경우, 데이터는 세 단계로 train/test 분할로 그룹화됩니다: 기본 모델(context-distilled 52B 언어 모델), 초기 선호도 모델에 대한 거부 샘플링(주로 best-of-16 샘플링), 반복적인 "온라인" 프로세스 중 샘플링된 데이터셋.
무해성의 경우, 기본 모델에 대해서만 데이터가 수집되지만, 동일한 형식으로 구성됩니다.
데이터 수집 과정과 크라우드워커 구성에 대한 세부 사항은 논문의 Section 2와 Appendix D에서 확인할 수 있습니다.
레드 팀 데이터
데이터는 논문 Red Teaming Language Models to Reduce Harms: Methods, Scaling Behaviors, and Lessons Learned에 설명되어 있습니다. 데이터가 유용하다면 논문을 인용해 주세요.
데이터 및 데이터 수집 절차에 대한 세부 사항은 논문 부록의 Datasheet에서 확인할 수 있습니다.
jsonl 파일의 각 줄에는 다음 필드를 가진 딕셔너리가 포함됩니다:

transcript: 인간 적대자(레드 팀 멤버)와 AI 어시스턴트 간의 대화 텍스트 기록
min_harmlessness_score_transcript: 선호도 모델로부터 얻은 AI 어시스턴트의 무해성 실수값 점수 (낮을수록 더 유해함)
num_params: AI 어시스턴트를 구동하는 언어 모델의 파라미터 수
model_type: AI 어시스턴트를 구동하는 모델 유형
rating: 레드 팀 멤버가 AI 어시스턴트를 공략하는 데 얼마나 성공했는지에 대한 평가 (리커트 척도, 높을수록 더 성공적)
task_description: 레드 팀 멤버가 AI 어시스턴트를 어떻게 공략하려 했는지에 대한 짧은 텍스트 설명
task_description_harmlessness_score: 선호도 모델로부터 얻은 작업 설명의 무해성 실수값 점수 (낮을수록 더 유해함)
red_team_member_id: 레드 팀 멤버의 임의 식별자. 한 레드 팀 멤버가 여러 공격을 생성할 수 있음
is_upworker: 레드 팀 멤버가 Upwork 크라우드 플랫폼 출신이면 true, MTurk 출신이면 false인 이진 지표
tags: 기록당 최대 6개의 태그 목록. 태그는 레드 팀 데이터를 사후 검토한 크라우드워커가 생성한 레드 팀 시도에 대한 짧은 설명입니다. 태그는 4가지 모델 유형 중 2가지에 대한 1,000개의 무작위 샘플에 대해서만 제공되었습니다.

연락처
문의사항은 redteam@anthropic.com으로 보내주세요.
