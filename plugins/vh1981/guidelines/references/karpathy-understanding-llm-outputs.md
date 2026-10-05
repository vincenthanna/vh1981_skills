# Karpathy, "LLM 출력을 이해하는 법" 번역과 관련 자료

이 문서는 Andrej Karpathy가 2026-10-02에 X에 올린 글의 번역과, 그 글과 이어진 자료의 요약이다.
글의 요지는 LLM이 일을 더 많이 대신할수록 사람의 일은 결과를 이해하고 감독하는 쪽으로 옮겨 가며, 그 이해를 돕는 출력 형식이 글, 도식, 웹 페이지, 설명 영상 순으로 강력하다는 것이다.
관련 자료에서 가장 중요한 사실은, 이 글이 권한 통제 언어(ASD-STE100)를 엄격하게 적용하면 사실이 크게 사라지고 느슨하게 적용하면 그 손실이 작다는 실험 결과다.
이 문서를 근거로 만든 작성 원칙은 `../output-principles.md` 에 있다.

## 원문 정보

```
URL     https://x.com/karpathy/status/2105819303471976479
작성    Andrej Karpathy (@karpathy), 2026-10-02 00:37 UTC
형식    긴 단일 게시물. 스레드나 X Article이 아니고, 인용이나 답글도 아니다. 외부 링크는 없고 이미지가 하나 붙어 있다
반응    조회 약 720만, 좋아요 약 5.3만, 북마크 약 7.8만 (수집 시점)
```

## 번역

> 앞으로 우리는 언어 모델이 내놓은 결과물을 이해하려고 훨씬 더 많은 시간을 쓰게 될 것이다. 몇 가지 생각과 요령을 적는다.
>
> **글.** 내가 효과를 본 방법이 있다. LLM에게 무언가를 ASD-STE100으로 설명해 달라고 해 보라. ASD-STE100은 원래 항공기 정비 문서를 위해 만들어진 통제 언어 규격이다. LLM은 이 언어를 잘 알고, 이 언어에는 깔끔한 문체에 대한 강한 제약이 따라와서, 나는 그 결과가 훨씬 읽기 쉽다고 느낄 때가 많다. 규격이 꽤 엄격해서 가끔은 조금 누그러뜨려 "ASD-STE100의 80% 정도로" 써 달라고 하기도 했다. 하지만 이보다 더 좋은 것이 있다.
>
> **도식과 이미지.** 글 대신 LLM에게 도식을 만들어 달라고 하라. 도식은 받아들이고, 해석하고, 이해하기가 훨씬 쉬울 수 있다. 하지만 이보다 더 좋은 것이 있다.
>
> **웹 페이지.** 출력을 "HTML로" 달라고 하면 아름답고 상호작용하는 웹 페이지를 얻는다. LLM은 프론트엔드를 정말 잘 만들게 되었고, 아름다운 경험과 애니메이션 같은 것을 만들어 낼 수 있다. 하지만 이보다 더 좋은 것이 있다.
>
> **설명 영상.** 내가 가장 기대하는 출력 형식은 어떤 주제든 그 주제만을 위해 완전히 맞춤으로 만든 설명 영상이다. "X에 대해 3b1b 스타일의 설명 영상을 만들어 줘. 음성 내레이션은 내 ElevenLabs API 키를 써"처럼 실험해 보라. (뒤쪽은 API 키가 필요하다. 아니면 LLM에게 로컬 컴퓨터로 돌릴 수 있는 괜찮은 무료 대안을 찾아 달라고 할 수 있다.) 이것이 실제로 되기 시작했다.
>
> **요약하면:**
> - LLM이 좋아질수록 잡일은 점점 더 많이 LLM이 스스로 하게 되고, 우리 일의 훨씬 많은 부분이 추상화의 위층, 즉 감독과 이해로 올라간다.
> - 다행히 여기서도 LLM이 도울 수 있다. 지능과 코드가 점점 흔해지기 때문에, 예전 같으면 만들 이유가 없었을 크고, 맞춤형이고, 쓰고 버려도 되는 소프트웨어 산출물(웹 앱, 설명 영상 등)을 요청할 수 있다. 여기서 한계를 밀어붙여 보라. 놀라게 될 것이다.

번역 메모는 세 가지다.

- "3b1b"는 수학 설명 영상 채널 3Blue1Brown이다. 애니메이션으로 개념을 단계별로 보여 주는 방식을 가리킨다.
- "discardable"은 "쓰고 버려도 되는"으로 옮겼다. 한 번 이해하는 데 쓰고 유지보수하지 않아도 되는 산출물이라는 뜻이다.
- 원문의 "LLMs well-versed in this language"는 "are"가 빠진 원문 그대로의 표현이며, 뜻은 "LLM은 이 언어를 잘 안다"이다.

## 첨부 이미지

글에는 "Simplified Technical English: overview"라는 한 장짜리 설계도 형식의 정리표가 붙어 있다. LLM에게 도식을 만들게 한 예시로 보인다. 담긴 내용은 아래와 같다.

| 칸 | 내용 |
|---|---|
| 문서 구조 | 1부 작성 규칙(단어, 명사 묶음, 동사, 문장, 절차, 설명문, 안전 지시, 문장부호와 단어 수, 작성 관행), 2부 사전(승인 단어 약 900개, 단어마다 품사 하나와 뜻 하나) |
| 문장 예시 | "It is imperative that the operator ensures the hydraulic reservoir is replenished prior to commencing operation." 을 "Make sure that the hydraulic reservoir is full before you start the operation." 으로 고친다 |
| 동사 형태 | 명령형, 단순 현재, 단순 과거, 단순 미래, to부정사, 형용사로 쓰는 과거분사는 승인. 진행형, 완료형, 절차 문장의 수동태는 비승인 |
| 수치 제한 | 절차 문장 20단어, 설명 문장 25단어, 문단 6문장, 명사 묶음 3단어, 문장당 지시 하나 |
| 작성 관행 | 같은 대상에는 항상 같은 단어를 쓴다. "the", "a", "this" 같은 말을 빼지 않는다. 절차에는 능동태를 쓴다. 복잡한 내용은 세로 목록으로 쓴다. 문단 하나에 주제 하나 |

이 이미지에는 오류가 있다. 사실 확인 글(아래 자료 4)에 따르면 사전 칸의 세 줄이 실제 규격과 다르다. APPROXIMATELY는 승인 단어이고, TEST는 명사로만 승인되며, "in order to" 항목은 Issue 8과 9 사전에 없다. LLM이 만든 도식도 사실 확인이 필요하다는 사례다.

## 관련 자료

### 1~2. 흐름의 시작: Andrew Carr의 두 게시물 (2026-07-27, 07-29)

Carr는 Claude가 "plain English로 말해 달라"는 부탁에도 은유와 자체 용어로 가득한 답을 내는 사례를 인용하며, 해결책으로 "ASD-STE100 Simplified Technical English로만 보고하라"고 쓰게 하라고 했다.
이틀 뒤에는 Claude와 Codex가 프로젝트 전용 어휘를 스스로 만들어 내는 지경이 되었고, 그것이 심해지면 이 프롬프트를 쓴다고 덧붙였다. 커뮤니티가 만든 skill과 checker 저장소 다섯 개도 소개했다.

```
https://x.com/andrew_n_carr/status/2081534245370314816
https://x.com/andrew_n_carr/status/2082453463712018658
```

### 3. Simplified Technical English 개요 (Wikipedia)

ASD-STE100은 비영어권 정비사도 쉽게 이해하도록 항공기 정비 문서의 영어를 표준화한 통제 언어다. 규칙은 53개이고, 승인 단어 사전은 약 900개다. 2025년 Issue 9에서 국제 표준이 되었고, 현재 사용자의 64%는 항공·방산 밖에 있다.
비판도 함께 실려 있다. STE로 바르게 쓰려면 영어 실력과 주제 지식이 모두 필요하고, 검사기를 맹신하면 엉터리 글이 나온다. 항공 밖의 조직은 대부분 STE 대신 plain language를 쓴다.

```
https://en.wikipedia.org/wiki/Simplified_Technical_English
```

### 4. 사실 확인 글 (max.nardit.com)

첨부 이미지의 사전 오류 세 건을 짚고, 수치 제한(절차 20단어, 설명 25단어)은 맞다고 확인한다. 도식이 글보다 이해에 유리하다는 주장은 Larkin과 Simon(1987)의 "Why a Diagram is (Sometimes) Worth Ten Thousand Words"로, 설명 영상의 효과는 TheoremExplainAgent(ACL 2025)로 뒷받침한다.
TheoremExplainAgent에서는 영상 설명이 글 설명에 숨어 있던 추론 결함을 드러냈다. 일부 모델은 STE 요청을 그냥 무시한다는 답글도 소개한다.

```
https://max.nardit.com/articles/karpathy-understanding-llm-outputs
```

### 5~6. Lucian Ghinda의 실험과 권고

Claude와 Codex에게 실제 Ruby 코드 4개(95~130줄)를 세 조건으로 두 번씩 설명하게 하고, 예제마다 정해 둔 사실 6개가 설명에 남는지 셌다. 이 실험이 이 문서에서 가장 실무적인 근거다.

| 조건 | 평균 문장 길이(단어) | 잃은 사실 |
|---|---|---|
| Claude, 스타일 지시 없음 | 17.8 | 기준 |
| Claude, 느슨한 "Simple Technical English" | 9.0 | 4/47 (8.5%) |
| Claude, 엄격한 ASD-STE100 | 10.2 | 22/47 (46.8%) |
| Codex, 느슨한 "Simple Technical English" | 12.5(지시 없음) | 13/30 (43.3%) |

"explicit", "deterministic", "propagates" 같은 흐릿한 단어는 스타일 지시로 26회에서 1회로 줄었다. 그러나 엄격한 규격은 도메인 용어를 표현하지 못해 사실을 잃었다. Ghinda의 결론은 Claude에는 느슨한 지시가 낫고, 규격을 도입하기 전에 자기 분야로 직접 시험해 보라는 것이다.
그가 권하는 지시문은 다음과 같다. "Use Simple Technical English: short sentences, one idea each, reusing domain terms from the codebase instead of inventing abstractions."

```
https://allaboutcoding.ghinda.com/explain-to-me-in-simple-technical-english/
https://notes.ghinda.com/post/don-t-automatically-add-asd-ste100-to-your-agents-instructions
```

### 7. K. Golubic의 정리

STE의 원칙은 "단어 하나에 뜻 하나, 품사 하나"이고, "명확하게"는 의견이지만 STE 규칙은 셀 수 있다는 점이 강점이다. 다만 LLM은 공식 사전을 갖고 있지 않으므로, LLM이 내는 것은 STE가 아니라 "STE 풍의 영어"다.

```
https://kgolubic.com/posts/asd-ste100-and-llms/
```

### 8. 커뮤니티 구현

`JAICHANGPARK/ASD-STE100` 은 "80% 실용 모드"를 정의한다. 단어 단속과 조동사 치환은 풀고, API나 Docker 같은 현대 기술 명사를 허용한다. 문장 길이 목표 15~22단어(상한 25), 능동태, 문장당 생각 하나는 지킨다. 사실 보존, 코드 블록 불변, 도메인 용어 유지를 가드레일로 둔다.

```
https://github.com/JAICHANGPARK/ASD-STE100
```

## 수집 한계

- 공식 사이트 `asd-ste100.org` 는 접근이 막혀(HTTP 403) 규격 원문을 확인하지 못했다. 규칙 목록은 위 2차 자료에서 왔다.
- Karpathy 본인의 후속 답글은 답글 목록을 불러올 수 없어 확인하지 못했다.
- 자료 3~8의 인용은 요약형 수집 도구를 거쳤으므로 글자 단위로 대조하지 않았다(미검증). 원문 번역은 fxtwitter API로 받은 전문을 기준으로 했다.
