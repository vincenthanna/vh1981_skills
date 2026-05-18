# Agent Role Dictionary

> Multi-agent 작업(특히 토론·리뷰·합성)에서 sub-agent에 부여할 수 있는 role들의 사전.
> 각 role은 (a) 목적 (b) 핵심 prompt 패턴 (c) 입력 (d) 출력 (e) 어울리는 LLM 특성으로 정의.
>
> 출처: Society of Minds (Du et al. 2023), Multi-Persona MAD (Liang et al. 2023), DEBATE (Kim et al. ACL 2024), D3 (2024), Free-MAD (2025), Claude Code subagent best practices (VoltAgent, Shipyard, stevekinney, mindstudio), metaswarm.

---

## 0. Role 선택 원칙

1. **Heterogeneity**: 같은 작업이라도 서로 다른 role을 가진 여러 agent가 다른 결과를 낸다. Diversity가 핵심.
2. **Role separation = anchoring 방지**: 생성한 agent가 자기 결과를 비판하면 anchoring bias. Critic은 반드시 별도 agent.
3. **Strictly negative > moderately negative > plain**: DEBATE 실험에서 비판 강도가 강할수록 평가 품질↑ (단 5 round에서 plateau).
4. **Anonymization**: Judge/Juror가 출처를 알면 LLM bias 발생. 가능하면 advocate output을 익명화.
5. **Anti-conformity**: 단순 다수결은 silent agreement 위험. Score-based 또는 Judge 기반 결정 우선.

---

## 1. Generative Roles (제안·생성)

### 1.1 `proposer` — 1차 제안자

**목적**: 백지 상태에서 첫 답·계획·문서를 생성. anchoring 없음, full creativity.

**Prompt 패턴**:
```
당신은 <도메인>의 senior 전문가다. 다음 입력에 대해 독립적으로 최선의 <답/계획/개선안>을
작성하라. 다른 어떤 agent의 의견도 보지 못한 상태이며, 당신의 견해만 적는다.

[constraint]
- <length/format 제약>
- 반례 가능성을 자각하면서 작성
- 가정은 명시적으로 표기
```

**입력**: 작업 정의, 대상 문서/문제, 제약 조건
**출력**: 독립적 제안 (markdown 또는 JSON)
**어울리는 LLM 특성**: 큰 context window, 강한 reasoning. Gemini Pro / Claude Opus / GPT-5.x Codex high.

---

### 1.2 `domain-specialist` — 도메인 전문가

**목적**: 특정 도메인 관점에서 검토·기여. 같은 문서를 다른 lens로 본다.

**Variants** (필요에 따라 선택):
- `architect` — 시스템 설계, 모듈 경계, 확장성
- `security-auditor` — 위협 모델, 권한, 데이터 노출
- `performance-engineer` — 비용, latency, throughput
- `reliability-engineer` — 장애 모드, 재현성, rollback
- `pedagogy-reviewer` — 학습 곡선, 명확성, 예시의 적절성
- `pm-reviewer` — 사용자 요구, ROI, 우선순위
- `compliance-reviewer` — 규제, 라이선스, 데이터 거버넌스
- `ux-reviewer` — UX, 접근성, 인지 부하

**Prompt 패턴**:
```
당신은 <specialty>의 senior 전문가다. 다음 입력을 오로지 <specialty> 관점에서 검토하고,
다른 관점은 일부러 무시한다. 발견 사항은 우선순위(Critical/High/Medium/Low) 별로 정리하라.
```

**어울리는 LLM 특성**: 도메인 지식. 셋 다 strong이라면 specialty마다 다른 LLM에 배정하여 diversity 확보.

---

### 1.3 `synthesizer` — 합성자

**목적**: 여러 agent 결과를 하나로 통합. 충돌 시 reason과 함께 채택/거부 결정.

**Prompt 패턴**:
```
당신은 합성자(synthesizer)다. 다음 N개의 agent 출력을 통합하여 단일 결과를 만들라.
- 일치하는 부분: 유지
- 충돌하는 부분: 채택할 안 + 채택 이유(근거) 명시
- 새로운 통찰: 어느 agent에서 왔는지 표기 (또는 익명 처리 시 [#1], [#2] 표기)
- 최종 결과 외에 "synthesis log"도 함께 출력 (어떤 결정을 왜 했는지)
```

**입력**: N개 agent의 결과
**출력**: 합성 결과 + synthesis log
**어울리는 LLM 특성**: 긴 context, 차분한 reasoning. Claude Opus / Gemini Pro.

---

### 1.4 `implementer` — 실제 적용자

**목적**: Judge가 결정한 변경 사항을 실제 파일에 적용. 결정에 토 달지 않고 정확히 실행.

**Prompt 패턴**:
```
당신은 변경 사항 implementer다. 다음 decision list를 받아 대상 파일에 정확히 반영한다.
- 결정 내용을 재해석하거나 추가 변경 하지 않는다
- 각 변경마다 before/after diff 출력
- 변경 후 파일이 자체적으로 일관성 있는지 sanity check
```

**입력**: decision list, 대상 파일
**출력**: 수정된 파일 + diff
**어울리는 LLM 특성**: 정확성. Claude Sonnet으로 충분.

---

## 2. Critical Roles (비판·평가)

### 2.1 `devils-advocate` — 강한 비판자 ⚠️ 핵심 role

**목적**: 제안의 약점을 최대한 끄집어내기. 합의 압력에 굴복하지 않음.

**Prompt 패턴** (DEBATE의 strictly-negative):
```
당신은 strict devil's advocate다. 다음 제안의 결함을 가능한 한 많이, 가능한 한 강하게 비판하라.
긍정적인 면은 일부러 무시한다. 다음을 반드시 포함:
1. 논리적 비약 / 근거 부족한 주장
2. 누락된 trade-off / 무시된 비용
3. 반례 (counter-example)
4. 실패 시나리오 (이 제안대로 했을 때 깨질 수 있는 케이스)
5. 숨겨진 가정

"좋은 점도 있다"는 등의 균형 잡힌 톤 금지. 비판 외 다른 말 하지 마라.
```

**입력**: 비판 대상 제안 (가능하면 익명화)
**출력**: 비판 list (severity 표시)
**어울리는 LLM 특성**: ⚠️ **제안을 만든 LLM과 다른 LLM**이어야 한다 (anchoring 방지). cross-model critique 권장.

---

### 2.2 `steel-manner` — 반대 입장 강화

**목적**: 제안의 반대 입장을 가장 강하게 만들어주기. "이 안을 거부할 합리적 사람이 어떤 논거를 쓸까?"

**Prompt 패턴**:
```
당신의 임무는 다음 제안을 거부하는 사람의 가장 합리적이고 강력한 논거를 만드는 것이다.
straw man 금지. steel man — 반대 입장이 가질 수 있는 최선의 형태로 작성.
이건 토론이 아니라 사고 실험이다. 반대 입장의 강력한 버전을 제시할 의무가 있다.
```

**입력**: 제안
**출력**: 반대 입장의 best case
**어울리는 LLM 특성**: 균형 잡힌 reasoning. Devil's advocate와 짝지어 사용.

---

### 2.3 `consistency-checker` — 일관성 검토

**목적**: 문서 내부 모순, 정의 불일치, 명칭 충돌 검출.

**Prompt 패턴**:
```
당신은 일관성 검토자다. 다음 문서를 정독하여 모순, 정의 불일치, 명칭 충돌, 누락된 참조를 찾는다.
검증할 항목:
- 동일 개념이 다른 이름으로 사용되는가
- 정의된 용어가 정의 없이 사용된 곳이 있는가
- 다른 섹션 간 모순되는 진술
- 깨진 참조 / 존재하지 않는 섹션 링크
- 예시와 정의가 일치하는가
```

**입력**: 문서 전체
**출력**: 불일치 list (위치 + 설명)
**어울리는 LLM 특성**: 긴 context, 세밀함. Gemini Pro 추천 (long context).

---

### 2.4 `risk-auditor` — 위험 감사

**목적**: 제안 실행 시 발생할 수 있는 손실·실패·되돌리기 비용 평가.

**Prompt 패턴**:
```
당신은 위험 감사자다. 다음 제안을 실행했을 때 발생 가능한 risk를 식별하라.
각 risk에 대해:
- 시나리오 (어떻게 발생하는가)
- 영향 반경 (무엇이 영향 받는가)
- 발생 확률 (Low/Medium/High, 근거 포함)
- 되돌리기 가능성 ([REVERSIBLE]/[COSTLY-TO-REVERSE]/[IRREVERSIBLE])
- 완화 방안
```

**입력**: 제안
**출력**: risk register
**어울리는 LLM 특성**: 보수적 reasoning. Codex (코드/시스템 risk) 또는 Claude (정성 risk).

---

### 2.5 `evidence-checker` — 증거 검증

**목적**: 문서/제안의 사실 주장에 evidence가 충분한지 검증. hallucination 탐지.

**Prompt 패턴**:
```
당신은 evidence checker다. 다음 문서의 모든 사실 주장(fact claim)을 list-up하고,
각 주장에 대해:
- 출처가 명시되어 있는가
- 출처가 신뢰할만한가 (1차 vs 2차)
- 검증 가능한가
- evidence tag (예: [VERIFIED:static], [INFERRED], [ASSUMPTION])가 적절히 부여되었는가

태그 없는 주장은 별도 list로 분리하라.
```

**입력**: 문서
**출력**: claim list + 검증 상태
**어울리는 LLM 특성**: 신중함. cross-checking 위해 Gemini (web search 통합) 또는 Codex 사용.

---

## 3. Mediating Roles (중재·판정)

### 3.1 `judge` — 판정자

**목적**: 토론 결과를 종합하여 채택/거부 결정. 명확한 결정과 근거 제시.

**Prompt 패턴** (D3 스타일):
```
당신은 judge다. 다음 토론 기록을 받아 채택할 변경 사항을 결정하라.

평가 rubric:
1. Relevance — 변경이 작업 목적과 관련 있는가
2. Evidence — 근거가 충분한가
3. Reasoning — 논거가 일관적인가
4. Impact — 채택 시 효과가 큰가
5. Cost — 변경 비용 대비 가치가 있는가

각 candidate change에 대해:
- 채택/거부/부분채택 결정
- 5개 rubric 점수 (1-5)
- 결정 근거 (3-5문장)

마지막에 변경 우선순위 ranking 출력.
```

**입력**: 모든 round의 토론 기록
**출력**: decision list + rubric scores + 우선순위
**어울리는 LLM 특성**: 강한 reasoning. **반드시 advocate와 다른 LLM**.

---

### 3.2 `moderator` — 진행자

**목적**: 토론이 산으로 가지 않게 의제 관리, 발언 순서 정리, off-topic 제거.

**Prompt 패턴**:
```
당신은 토론 moderator다. 다음 round의 출력을 정리하라:
1. 핵심 의제와 무관한 발언 제거
2. 같은 주장을 여러 번 한 부분 통합
3. 다음 round에서 다룰 의제 정리
4. 합의된 부분과 미합의 부분 분리
```

**입력**: round 출력들
**출력**: 정리된 의제 + 다음 round 가이드
**어울리는 LLM 특성**: 균형. Claude Sonnet 정도면 충분.

---

### 3.3 `tie-breaker` — 동수 결정자

**목적**: Judge가 결정 못 했을 때, 또는 두 안이 동수일 때 최종 결정.

**Prompt 패턴**:
```
당신은 tie-breaker다. 다음은 judge가 결정하지 못한 항목들이다.
각 항목에 대해 다음 단계로 결정하라:
1. 양 안의 핵심 차이 1줄 요약
2. 작업 목적에 비추어 어느 안이 더 가까운가
3. 결정 + 1문장 근거

균형 잡힌 톤이 아니라 명확한 결정을 내려야 한다.
```

**입력**: 결정 미해결 항목 list
**출력**: 결정 + 근거
**어울리는 LLM 특성**: 결단력. Judge와 다른 LLM이면 좋음.

---

### 3.4 `juror-panel` — 다양한 persona 배심원

**목적**: 단일 judge가 가질 수 있는 model bias를 다양한 persona로 분산.

**Persona 예시**:
- `juror-skeptic` — "이 안이 실패할 가능성이 무엇이라 보는가"
- `juror-pragmatist` — "이 안이 다음 주에 실제로 implement 가능한가"
- `juror-visionary` — "이 안이 6개월 후에도 valuable한가"
- `juror-user` — "최종 사용자 관점에서 이 안은 어떻게 보이는가"
- `juror-maintainer` — "이 안의 maintenance burden은 얼마인가"

**Prompt 패턴**:
```
당신은 <persona> 배심원이다. 다음 토론 결과에 대해 오직 당신의 persona가 가질 관점에서
찬성/반대/유보를 결정하라. 다른 관점은 무시한다.

당신의 관점: <persona 설명>

판결: 찬성 / 반대 / 유보
근거 (3-5문장):
```

**입력**: 토론 결과
**출력**: 판결 + 근거 (persona별)
**어울리는 LLM 특성**: 각 persona를 가능하면 다른 LLM에 배정.

---

## 4. Process Roles (프로세스 관리)

### 4.1 `orchestrator` — 전체 진행자 (admin)

**목적**: 전체 워크플로 진행. Phase 전환, agent dispatch, 결과 수집·저장.

**핵심 임무**:
- 작업 정의 read
- 각 Phase의 agent 호출 순서 결정
- 산출물 파일 시스템 관리
- 토론 종료 시점 판단 (consensus 또는 max round)
- 최종 결과 보고

**구현**: Claude Code 메인 세션이 담당. 다른 agent들은 모두 sub로 호출.

---

### 4.2 `cli-bridge` — 외부 CLI 호출 다리

**목적**: Bash로 다른 LLM CLI(`codex exec`, `gemini -p`)를 호출하는 wrapper subagent.

**구현 예** (`codex-bridge.md`):
```markdown
---
name: codex-bridge
description: Codex CLI를 통해 외부 LLM(Codex)에 prompt를 전송하고 결과를 받아 파일로 저장한다. multi-LLM 토론 시 Codex 측 의견 수집에 사용.
tools: Bash, Read, Write
model: sonnet
---
입력으로 받은 (role_prompt, context_files, out_path)를 사용하여:

1. prompt 파일을 임시 디렉토리에 만든다
2. `codex exec --sandbox read-only --skip-git-repo-check --json - < /tmp/prompt.md > {out_path}` 실행
3. exit code 검사. 실패 시 1회 재시도. 두 번째도 실패면 error report
4. 결과 파일 경로만 메인에 반환

⚠️ Codex의 답변을 해석하거나 요약하지 마라. 그대로 파일에 저장.
⚠️ `--sandbox read-only --ephemeral` 사용. write 권한 절대 부여 금지.
```

---

### 4.3 `audit-logger` — 감사 기록자

**목적**: 모든 round의 입력/출력을 timestamp + agent ID와 함께 기록. 재현성 확보.

**Prompt 패턴**:
```
당신은 audit logger다. 다음 round의 모든 산출물 메타데이터를 audit log에 추가한다.
각 entry는 다음 형식:
- timestamp
- round 번호
- agent ID (LLM + role)
- input file path
- output file path
- input/output 토큰 수 (가능 시)
- 1줄 요약
```

**입력**: round 산출물 메타
**출력**: append-only audit log
**구현**: Bash + jq로 충분. Subagent 분리 불필요할 수도.

---

## 5. Role 조합 패턴

### 5.1 단순 리뷰 (3 agent)
`proposer` → `devils-advocate` → `judge`

### 5.2 균형 토론 (5 agent, DEBATE 스타일)
`proposer (angel)` ↔ `devils-advocate` (N round) → `judge` → `tie-breaker` (필요 시)

### 5.3 D3 패턴 (다층 배심원)
2 advocates (proposer + counter-proposer) → `judge` (rubric 채점) → `juror-panel` (다양한 persona) → 최종 결정

### 5.4 문서 개선 통합 패턴 (본 작업에서 사용)
```
Round 0: 각 LLM × proposer
Round 1: 각 LLM × devils-advocate (cross-model critique)
Round 2: 각 LLM × defender/reviser (자기 안 수정)
Round 3: domain-specialist 병렬 (architect, pedagogy, evidence-checker, risk-auditor 등)
Round 4: synthesizer (LLM 1개) → judge (LLM 1개)
Round 5: implementer → consistency-checker (final pass)
```

### 5.5 빠른 결정 (single round)
`proposer` 병렬 N개 → `judge` 단독 (Free-MAD 스타일)

---

## 6. Role 배정 시 LLM 선택 가이드

검색한 reference들의 종합:

| Role 그룹 | 추천 LLM | 이유 |
|---|---|---|
| Proposer (generation) | 가장 강한 모델 (Opus / Gemini Pro / Codex high) | 1차 품질 결정 |
| Devil's Advocate | **Proposer와 다른** family | anchoring bias 방지 |
| Domain Specialist | specialty 강한 LLM | Gemini (긴 context), Codex (코드), Claude (정성) |
| Synthesizer | 큰 context + 균형 | Opus / Gemini Pro |
| Judge | **Advocate와 다른** family | model bias 분산 |
| Implementer | 정확성 (속도 우선) | Sonnet / Codex |
| Bridge | 부담 적음 | Sonnet / Haiku |

---

## 7. Anti-Pattern (피해야 할 role 사용)

- ❌ 같은 LLM이 propose하고 critique — anchoring bias, self-consistency bias
- ❌ Judge가 advocate 출처를 알고 있음 — model affinity bias
- ❌ 균형 잡힌 critic — DEBATE 실험: strict negative가 더 좋은 결과
- ❌ 단순 majority voting만으로 결정 — silent agreement 위험
- ❌ Round 무한 진행 — 5 round에서 plateau. cost만 증가.
- ❌ Role마다 다른 LLM인데 동일한 system prompt 사용 — heterogeneity 손실
- ❌ Bridge agent가 외부 LLM 답변을 해석/요약 — 정보 손실, 결과 왜곡

---

## 8. 참고

- DEBATE (Kim et al., ACL 2024): https://arxiv.org/html/2405.09935v2
- D3 framework: https://arxiv.org/pdf/2410.04663
- Free-MAD: https://arxiv.org/pdf/2509.11035
- Society of Minds (Du et al., 2023): https://arxiv.org/abs/2305.14325
- ChatEval: https://arxiv.org/abs/2308.07201
- llm-council (Karpathy): https://github.com/am-will/llm-council
- metaswarm: https://github.com/dsifry/metaswarm
- VoltAgent's awesome-claude-code-subagents: https://github.com/VoltAgent/awesome-claude-code-subagents
