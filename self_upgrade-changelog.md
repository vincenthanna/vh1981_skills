# self_upgrade Changelog

> `self_upgrade.md` 거버넌스 하에서 이뤄진 prompt/skill 변경 이력. **1회 1대상** 원칙으로 항목당 1줄.
>
> 형식: `YYYY-MM-DD | 대상 | 변경 요약 | 출처(tier) | 채점 | 승인자`

| Date | Target | 변경 요약 | 출처 | 채점 | 승인자 |
|---|---|---|---|---|---|
| 2026-05-26 | `components/speckit-spec-generation.md` (신규) | speckit(github/spec-kit) 기반 spec/plan/tasks 산출 component 추가. router §1/§1.1/§2/§7, composer 머리말/§5, CLAUDE.md Invariant ④/컴포넌트 라이브러리, ledger §1/§2/§3 동시 갱신. layer="domain content" 3축 분류 도입. | tier 1: `[VERIFIED:webfetch https://github.com/github/spec-kit @2026-05-26]` | 블라인드 독립 채점(general-purpose agent) PASS-with-fixes → 권고 3건(§4 SSOT 표화, 설치 명령 @vX.Y.Z, cost 현실화) 반영 후 commit | yeonhui.kim |
| 2026-06-07 | `components/code-review-rubric.md` v1.0→1.1 (RUL-001+CSC-001) | §9 Custom rule layer(파일패턴 repo-local 규칙 + 4계층 우선순위 + §4 hard floor 불가침) + §10 대형 changeset 스코핑/번들링(번들 휴리스틱 + cross-cutting pass + 단일-bundle fallback). §0 metadata/§1.1/§2/§5 보강. router §1·§2, composer §5 발췌 가이드 동시 갱신(새 component·새 분기 아님 → 컴포넌트 수 7 유지, CLAUDE.md 무변경). | tier 4: `[VERIFIED:webfetch README-described https://github.com/alibaba/open-code-review @2026-06-07]` (rule.json 미독립 fetch, 일반 번들 알고리즘 INFERRED) | 블라인드 독립 채점(general-purpose agent) DO-NOT-MERGE → 3 blocking(§5 template 확장, evidence tag 격하) + 5 non-blocking 전부 반영 후 commit | yeonhui.kim |
