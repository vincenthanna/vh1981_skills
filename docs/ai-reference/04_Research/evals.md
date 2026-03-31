---

모델이 작성한 평가 데이터셋
이 저장소에는 "Discovering Language Model Behaviors with Model-Written Evaluations" 논문에서 사용된, 언어 모델이 작성한 데이터셋이 포함되어 있습니다.
이 데이터셋은 다음과 같은 분들에게 유용할 것입니다:

모델이 생성한 데이터의 품질과 특성을 이해하고자 하는 분들
우리가 연구에서 조사한 행동(예: 모델 페르소나, 아첨성, 고급 AI 위험, 성별 편향)에 대해 다른 모델을 평가하기 위해 데이터셋을 사용하고자 하는 분들

이 평가들은 대화형 에이전트(예: 사용자 발화에 명시적으로 응답하도록 파인튜닝된 모델, 또는 대화형 에이전트처럼 동작하도록 프롬프트된 사전학습 언어 모델)에게 질문하도록 생성되었습니다. 그러나 다른 유형의 모델을 테스트하기 위해 데이터를 수정하는 것도 가능합니다.
아래에서 각 데이터셋 컬렉션을 설명합니다:

persona/: 정치적·종교적 견해, 성격, 도덕적 신념, 잠재적으로 위험한 목표(예: 자기 보존 또는 권력 추구) 추구 의지 등 행동의 다양한 측면에 대해 모델을 테스트하는 데이터셋.
sycophancy/: 다양한 질문(철학, NLP 연구, 정치)에 대해 모델이 사용자의 의견을 그대로 반복하는지 테스트하는 데이터셋.
advanced-ai-risk/: 고급 AI 시스템의 치명적 위험과 관련된 다양한 행동에 대해 모델을 테스트하는 데이터셋. 이 데이터셋은 퓨샷(few-shot) 방식으로 생성되었습니다. 참조 및 비교를 위해 Surge AI가 수집한 인간 작성 데이터셋도 포함되어 있습니다.
winogender/: Winogender Dataset(Rudinger et al., 2018)의 더 큰 모델 생성 버전입니다. 데이터셋 생성에 사용한 직업 명칭(미국 노동통계국의 직업 성별 통계 포함)도 함께 제공합니다.

데이터셋, 생성 방법, 인간 검증 지표, 기타 분석에 대한 자세한 내용은 논문을 참고하세요.
면책 조항: 논문에서 논의된 바와 같이, 일부 데이터에는 사회적 편견과 고정관념이 포함된 내용이 있습니다. 데이터에는 유해하거나 불쾌한 콘텐츠가 포함될 수도 있습니다. 데이터에 표현된 견해는 Anthropic 또는 직원의 견해를 반영하지 않습니다.
연락처
질문은 ethan at anthropic dot com으로 이메일을 보내주세요.
Bibtex 인용
우리의 연구나 데이터를 인용하고 싶으시면, 다음 bibtex 인용을 사용하세요:
@misc{perez2022discovering,
  doi = {10.48550/ARXIV.2212.09251},
  url = {https://arxiv.org/abs/2212.09251},
  author = {Perez, Ethan and Ringer, Sam and Lukošiūtė, Kamilė and Nguyen, Karina and Chen, Edwin and Heiner, Scott and Pettit, Craig and Olsson, Catherine and Kundu, Sandipan and Kadavath, Saurav and Jones, Andy and Chen, Anna and Mann, Ben and Israel, Brian and Seethor, Bryan and McKinnon, Cameron and Olah, Christopher and Yan, Da and Amodei, Daniela and Amodei, Dario and Drain, Dawn and Li, Dustin and Tran-Johnson, Eli and Khundadze, Guro and Kernion, Jackson and Landis, James and Kerr, Jamie and Mueller, Jared and Hyun, Jeeyoon and Landau, Joshua and Ndousse, Kamal and Goldberg, Landon and Lovitt, Liane and Lucas, Martin and Sellitto, Michael and Zhang, Miranda and Kingsland, Neerav and Elhage, Nelson and Joseph, Nicholas and Mercado, Noemí and DasSarma, Nova and Rausch, Oliver and Larson, Robin and McCandlish, Sam and Johnston, Scott and Kravec, Shauna and {El Showk}, Sheer and Lanham, Tamera and Telleen-Lawton, Timothy and Brown, Tom and Henighan, Tom and Hume, Tristan and Bai, Yuntao and Hatfield-Dodds, Zac and Clark, Jack and Bowman, Samuel R. and Askell, Amanda and Grosse, Roger and Hernandez, Danny and Ganguli, Deep and Hubinger, Evan and Schiefer, Nicholas and Kaplan, Jared},
  keywords = {Computation and Language (cs.CL), Artificial Intelligence (cs.AI), Machine Learning (cs.LG), FOS: Computer and information sciences, FOS: Computer and information sciences},
  title = {Discovering Language Model Behaviors with Model-Written Evaluations},
  publisher = {arXiv},
  year = {2022},
  copyright = {arXiv.org perpetual, non-exclusive license}
}
