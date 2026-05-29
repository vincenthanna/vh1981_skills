# Task Specification Template

> **무엇**: rough request → 구조화된 task spec으로 변환하는 input form. 모든 prompt composition의 입력.
> **용도**: composition을 시작하기 전 task를 A-E 등 필드로 구조화할 때 작성.
> **시리즈 위치**: composer Phase 1에서 호출. router / context-injection / evaluation-rubric / composer와 함께 동작.
>
> **참고 영향**: DSPy의 Signature (task의 input/output 선언), Anthropic Skills의 trigger description.

---

## 0. 사용 시점

다음 중 하나라도 해당하면 spec을 작성한다:
- composition으로 prompt를 만들기 직전
- 같은 task pattern을 6주 이내 반복 예정 (재사용 가능성)
- 산출물이 외부 보고 / 감사 / 클라이언트 대상
- `[IRREVERSIBLE]` 또는 `[COSTLY-TO-REVERSE]` 권고가 예상됨

다음이면 spec 생략 — direct prompting:
- 1회성 ad-hoc 질문 ("이거 한 줄 요약해줘")
- spec 작성 비용 > task 자체 비용
- task가 너무 단순해서 components 활성화가 불필요

---

## 1. 필수 필드 (A-E, 이 5개 없이는 routing 불가)

```markdown
# Task Spec: <task-id-kebab-case>

## A. Purpose (한 문장)
<이 task를 통해 결정/생성하고 싶은 단일 산출물은 무엇인가>
※ "그리고", "및" 두 번 이상 나오면 compound goal — 분리 검토.

## B. Output Type (단일 선택)
- [ ] Decision (선택지 중 채택)
- [ ] Analysis (사실 수집 + 평가, 결정은 다른 step)
- [ ] Generation (새 문서/코드 작성)
- [ ] Transformation (입력 → 출력 변환)
- [ ] Review (기존 산출물 검토)
- [ ] Mixed → ⚠️ task 분할 권고

## C. Scale
- topic / unit 개수: <N>
- 예상 산출물 길이: <라인/페이지/토큰>
- 단계 수: <1 LLM call / 다단계>

## D. Constraints
- 시간 예산: <분/시간>
- 토큰 예산 (가능 시): <대략 number>
- 형식 제약: <markdown / JSON / PR description / 한국어 / ...>
- 도메인 제약: <보안 / 규제 / 내부 공개 범위 / 라이선스>

## E. Success Criteria (측정 가능하게)
- 무엇을 보면 "좋은 결과"라고 판단하는가 (체크리스트 가능)
- 어떤 실패 모드가 cost 큰가
```

---

## 2. 권장 필드 (F-J, 있으면 routing 품질 향상)

```markdown
## F. Audience
<누가 결과를 읽고 행동하는가 — 본인 / 팀 / 외부 / 클라이언트>

## G. Reversibility (산출물이 행동을 유발하는 경우)
- [REVERSIBLE] / [COSTLY-TO-REVERSE] / [IRREVERSIBLE]
- rollback 한계: <한 줄>

## H. Prior Context
- 관련 이전 분석 / PR / 회의록 경로 list
- 이번 task에 영향 주는 결정 사항 list

## I. Environment
- 작업 환경: Claude Code / claude.ai / API / Cowork
- 사용 가능 tools: <Read / Grep / WebFetch / Bash / ...>
- 외부 자료 접근 가능 여부

## J. Confidence Required
- [Low] 빠른 정답 / 사용자가 검토 후 확정
- [Medium] 결정 직전 검토
- [High] 즉시 실행 가능 수준
```

---

## 3. 선택 필드 (K-L, 특수 케이스만)

```markdown
## K. Multi-LLM 필요 신호 (multi-agent-template §6.8.1 trigger)
- [ ] irreversible 권고 후보 1건 이상
- [ ] 외부 보고 / 감사 대상
- [ ] 동일 domain 6개월 내 반복 분석 (memory bias 의심)
- [ ] 1차 분석에서 evidence 충돌 관측

하나라도 체크 → multi-LLM 활성화 검토.

## L. Domain Lens 우선순위
agent-role-dictionary §5의 어떤 분야 lens가 critical한가:
- 1순위: <backend-engineer / frontend-engineer / mobile-engineer /
  devops-sre / embedded-engineer / data-engineer / ml-engineer /
  ml-researcher / security-researcher / systems-researcher / hci-researcher>
- 2순위: <...>
- 3순위: <...>
```

---

## 4. Spec 작성 example

```markdown
# Task Spec: dsai-onprem-customer-deploy-server-survey

## A. Purpose
DeepingSource 신규 customer의 on-prem 환경 후보 N개 중 적합한 서버 등록 방식을 결정.

## B. Output Type
[x] Decision (Teleport / VPN / SSH bastion 중 1개 채택)

## C. Scale
- topic 개수: 3개 (각 방식)
- 예상 산출물: 2-3페이지 한국어 결정서

## D. Constraints
- 시간: 하루 이내
- 형식: 한국어 markdown + 결정서 PDF 변환 가능 형태
- 도메인: 보안 critical, 외부 노출 최소화

## E. Success Criteria
- [ ] 각 방식의 위협 모델이 명시되어 있다
- [ ] 운영 부담 (on-call, key rotation) 비교 가능
- [ ] 채택 시 1주 내 PoC 가능한 actionability

## F. Audience
팀 내부 (봉경, 호용) + 인프라 결정자

## G. Reversibility
[COSTLY-TO-REVERSE] — customer side 변경 부담 큼

## L. Domain Lens
1순위: security-researcher, 2순위: devops-sre, 3순위: backend-engineer
```

---

## 5. Self-check (spec 완성 직후 의무)

- [ ] A-E 5개 필수 필드 모두 채워졌는가
- [ ] Purpose가 한 문장 + 단일 goal (compound 분리)
- [ ] Output Type이 단일 선택인가 (Mixed는 sub-task 분리 신호)
- [ ] Success Criteria가 **측정 가능**한가 ("좋다" 같은 모호한 표현 금지)
- [ ] G. Reversibility 명시됨 (action 권고 산출물일 때)

self-check 실패 = spec 재작성. routing에 부적합한 spec은 **garbage routing의 직접 원인**.

---

## 6. Anti-patterns

- ❌ **Purpose가 compound** ("X를 결정 *그리고* Y를 분석하라") → 두 spec으로 분리
- ❌ **Success Criteria가 vague** ("훌륭한 결과") → 체크리스트 형태로 sharpen
- ❌ **Output Type 미선택** → 어떤 component를 활성화할지 router가 판단 불가
- ❌ **D. Constraints 누락** → 토큰 blowup 위험 (router의 bypass 분기 작동 안 함)
- ❌ **L. Domain Lens 추측만으로 spec에 명시** → 잘못된 lens는 잘못된 critic을 부른다. 모르면 비워두고 router가 inference하게 하라.

---

## 7. 저장 위치 권장

```
.specs/<task-id>.md            # 이 spec
.specs/<task-id>.log           # composer의 routing log + post-eval 점수 누적
```

run-id를 가진 분석(`multi-agent-template`)을 트리거하는 spec이면, 추가로:
```
.analysis/<run-id>/00_plan.md  # spec의 핵심을 plan에 echo
```
