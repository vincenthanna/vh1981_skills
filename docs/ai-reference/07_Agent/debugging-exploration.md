---
name: debugging-exploration
source: plusinsight/.claude/agents/
type: claude-code-agent-group
agents: debugger, deep-explore
---

# 디버깅 & 탐색

2개의 디버깅/코드 탐색 전문 서브에이전트.
근본 원인 분석과 시맨틱 코드 검색을 담당한다.

---

## debugger

> 에러, 테스트 실패, 예상치 못한 동작의 근본 원인 분석 전문가.

### 디버깅 프로세스

```
1. 에러 메시지 및 스택 트레이스 캡처
2. 재현 단계 식별
3. 실패 위치 격리
4. 최소 수정 구현
5. 솔루션 검증
```

### 핵심 기법
- 에러 메시지 및 로그 분석
- 최근 코드 변경 검토
- 가설 수립 및 테스트
- 전략적 디버그 로깅 추가
- 변수 상태 검사
- 예방 권고사항 제시

### 스킬 연동
- `/qa` 스킬: GitHub Actions 실패 시 진단/수정에 사용
- `/develop` 스킬: 개발 중 에러 발생 시 호출

---

## deep-explore

> mgrep 시맨틱 검색 기반 코드베이스 심층 탐색 전문가.

### 핵심 도구

```bash
# 의미 기반 코드 검색 (텍스트 매칭이 아닌 의도 기반)
mgrep "authentication flow"
mgrep "error handling patterns"
mgrep "database connection setup"
```

### 핵심 역량
- **시맨틱 검색**: Mixedbread 임베딩 기반, 의미/의도로 코드 검색
- **아키텍처 발견**: 컴포넌트 관계, 데이터 흐름 매핑
- **패턴 식별**: 코드베이스 전체에서 반복 패턴 발견
- **코드 추적**: 함수 호출 체인, 데이터 변환 경로 추적
- **영향 분석**: 변경사항의 잠재적 영향 범위 평가

### 의존성
- `mgrep` (`npm install -g @mixedbread/mgrep`)
- 미설치 시 일반 `Explore` 에이전트로 폴백

### 스킬 연동
- `/develop` 스킬 Step 2: mgrep 가용 시 코드 탐색의 1순위 에이전트
