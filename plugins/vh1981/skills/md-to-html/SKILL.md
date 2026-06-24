---
name: md-to-html
description: 임의의 markdown 문서를 사람이 읽기 좋고 직관적으로 이해할 수 있는 검토 전용 HTML 로 재구성하여 export 한다. 원본 md 를 read-only 로 읽은 뒤, 대충 그린 ASCII/흐름도는 mermaid flowchart 로, UI 스케치는 실제 HTML/CSS mockup 으로 재작도하고, 코드·SQL·threshold·결정·파일경로 같은 기술적 사실과 목차 앵커는 정확히 보존한다. markdown 이 source of truth 이고 HTML 은 한 방향으로 뽑는 throwaway 산출물(역방향 없음)이다. 구현계획·설계·분석 문서 등 어떤 markdown 에도 쓸 수 있다. Use when the user wants to turn any markdown document into a readable, visual HTML review view. Trigger phrases include "md-to-html", "md 를 html 로", "markdown html export", "마크다운 html 변환", "md 문서 시각화", "문서를 보기 좋은 html 로", "export markdown to html", "구현계획 html", "plan html export". Do NOT use for general markdown→html static-site builds, lossless/round-trip conversion, or editing the source markdown.
---

# Markdown → HTML Export

> **목적: 사람이 markdown 문서를 읽기 좋고, 시각적으로·직관적으로 이해하기 위한 HTML 을 만든다.**
> 무손실 복제가 목적이 아니다 — **이해(comprehension)** 가 목적이다.
> markdown 이 source of truth(편집·유지 대상)이고, HTML 은 한 방향으로 뽑아내는
> 검토 전용 throwaway 산출물이다. 역방향(html→md)은 없다. md 를 고치면 다시 export 한다.

---

## 입력 (`$SOURCE_MD`)

- 이 skill 의 인자는 **export 할 markdown 파일 경로**다 (`$SOURCE_MD`).
- 인자가 주어지지 않으면:
  - 이번 세션에서 방금 다룬 md 문서가 명확하면 그것을 대상으로 삼고, 시작 전 한 줄로 확인한다.
  - 후보가 불분명하면 어떤 markdown 을 export 할지 사용자에게 묻는다 (추측해서 진행하지 않는다).
- 출력 HTML 은 별도 지정이 없으면 **원본 md 와 같은 디렉토리에 같은 basename + `.html`** 로 쓴다.
  원본 markdown 은 절대 수정·이동·삭제하지 않는다.

---

## 0. 작업 절차

1. **markdown 문서를 전체(처음~끝) 읽어 내용을 이해한다.**
2. **이해를 돕도록 재구성하여 HTML 로 export 한다** (아래 규칙 포함).

산출물은 검토용 HTML 1개. 원본 markdown 은 read-only — 절대 수정·이동·삭제하지 않는다.

---

## 1. 재구성 원칙 (comprehension-first)

- **1:1 대응을 강제하지 않는다.** verbatim 복제·round-trip·"무손실 검증" 같은 제약은 두지 않는다.
  표현·구조·시각화는 이해를 위해 자유롭게 재구성한다.
- **대충 그린 그림(ASCII/유니코드 박스 아트)은 HTML 에서 아예 새로 그린다.**
  - 흐름·아키텍처·파이프라인 다이어그램 → **mermaid flowchart** 로 재작도.
  - UI 스케치(드롭다운·모달 등) → **실제 HTML/CSS mockup** 으로 재작도.
  - 단순 트리/리스트(디렉토리 구조 등)·표·코드는 "그림"이 아니므로 재작도하지 말고
    정돈된 텍스트/표/코드 블록으로 깔끔히 보여준다.
  - 재작도는 원본 스케치의 *의도*를 사람이 이해하기 쉽게 옮기는 것이다. 원본 ASCII 는
    `<details>` 로 접어 한 번에 펼쳐 볼 수 있게 남겨 비교 가능하게 한다(선택).
- **기술적 사실은 정확히 유지한다.** 코드·SQL·threshold·수치·결정·파일경로 등은
  이해를 돕기 위해 재배치·강조할 수 있어도 **내용을 틀리게 바꾸지 않는다** (틀린 스펙은 이해를 해친다).
- 요약으로 핵심 정보를 누락시키지 않는다 — 재구성은 "더 잘 보이게"이지 "줄이기"가 아니다.

---

## 2. 다이어그램 재작도 (mermaid / HTML mockup)

- export 도구(에이전트)가 **md 를 읽고 직접 재작도**한다. mermaid.js 를 항상 로드해 SVG 로 렌더.
- light/dark 테마와 mermaid 테마를 동기화한다 (테마 토글 시 재렌더).
- 문서가 의미색을 쓰면 반영한다 (예: **prod=amber / sim=cyan**) — 노드/엣지 색에 활용.
- 렌더 실패 시 원본 ASCII 를 그대로 노출해 정보가 사라지지 않게 한다(fallback).
- ⚠ 손그림을 기계적으로 *추측 변환*하지 말고, 내용을 이해한 뒤 **의미가 맞게** 다시 그린다.

---

## 3. Export 방식

- 본문은 **CommonMark/GFM 정식 렌더러**(markdown-it / markdown-it-py)로 정적 HTML pre-render.
  (코드블록 `<` `>` `&` 를 올바르게 escape → SQL·heredoc·타입표기 안 깨짐.)
- ⚠ Python `markdown` 의 `toc` 확장 금지 — slugify 가 한글 앵커를 깨뜨린다 (§5).
- 본문 텍스트 변형 방지: smartquotes / replacements / linkify 비활성 (`-->`, `(a)`, `@id` 보존).
- 코드 하이라이트: highlight.js, **언어 지정 블록에만**.
- md 를 결과물에 임베드하지 않는다 (검토 전용).

---

## 4. 서드파티 라이브러리 (적극 사용)

| 목적 | 라이브러리 |
|---|---|
| markdown 렌더(빌드) | markdown-it / markdown-it-py (+ tasklists) |
| **다이어그램 재작도** | **mermaid** (항상 로드 · 테마 동기) |
| 코드 하이라이트 | highlight.js (github / github-dark) |
| 본문 기본 스타일 | github-markdown-css (light/dark) |
| 한글 본문 폰트 | Pretendard |
| 코드 폰트 | JetBrains Mono |

sidebar TOC / scroll-spy / 테마 토글 / 복사 버튼 / UI mockup 등은 vanilla JS·CSS.

---

## 5. 앵커 / 슬러그 (TOC 내비게이션 보존)

원본 목차는 GitHub 스타일 앵커를 쓴다 (`#3-시스템-아키텍처--data-flow`, `#6-5-제약--우회` 등).
이해를 위한 재구성이라도 **목차 점프는 동작해야** 하므로, heading `id` 를 GitHub slugify 동일
알고리즘으로 생성한다: trim+lowercase → 글자/숫자/공백/하이픈/언더스코어 외 삭제 → 공백→'-'
(다중 하이픈 collapse 금지) → 중복 -1,-2 suffix. 원본 `](#anchor)` 가 전부 매칭되는지 확인.

---

## 6. 시각화 기능

- 다이어그램: mermaid 벡터(테마 동기, 중앙 정렬). UI 스케치: HTML mockup.
- Sticky 좌측 사이드바 TOC (h2~h4) + scroll-spy + smooth scroll, 좁은 화면 접힘.
- 상단: 읽기 진행바 + 제목 + `export of <파일명> · <시각>` + 테마 토글 + 인쇄.
- 코드블록: 언어 라벨 + 복사 버튼. 표: zebra + sticky header + 가로스크롤.
- blockquote 콜아웃: 기본 note / `⚠`·`⏰`·`TTL`·`미실행` 포함 시 warning.
- 의미 강조: 결정표·Phase 로드맵·status(✅/⏳) 등 문서에 있으면 시각 강조.
- 테마 light/dark(css·hljs·mermaid 동기) localStorage 기억, print CSS.

---

## 7. 점검 (export 후)

- [ ] 원본 `.md` 무변경 (read-only)
- [ ] 대충 그린 그림이 mermaid/HTML 로 재작도됨 (남은 ASCII 박스아트는 의도된 텍스트뿐)
- [ ] mermaid 전부 렌더(실패 시 원본 fallback)
- [ ] 원본 목차 앵커 전부 동작 (heading id 매칭)
- [ ] 코드·SQL·수치·결정 등 기술 사실 정확
- [ ] 브라우저에서 TOC·scroll-spy·하이라이트·mermaid·테마 동작

---

## 8. 실행

```
입력: $SOURCE_MD
1. md 전체 read-only 로드 → 내용 이해
2. 이해 목적으로 재구성하여 정적 HTML export (대충 그린 그림은 mermaid/HTML mockup 으로 새로 그림)
3. §7 점검 후 html 경로 보고
```

> 목적은 사람의 이해다. 1:1 복제가 아니라 "읽기 좋고 직관적인" 검토용 뷰를 만든다.
> 원본 markdown 은 그대로 두어 편집·유지 소스로 계속 쓴다.
