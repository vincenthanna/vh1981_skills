프롬프트를 자연어로 검색한다.

## 검색어

$ARGUMENTS

## 작업

1. /Users/yeonhuigim/Documents/Prompts/prompts/CATALOG.md 파일을 읽는다.
2. 검색어의 의미와 관련된 프롬프트를 찾는다. (태그가 아닌 설명 기반 매칭)
3. 관련도 높은 순으로 출력한다.
4. templates > skills > archive 순으로 우선 표시한다.

## 출력 형식

관련 프롬프트를 구분하여 출력:
- **Templates**: 바로 복사해서 사용 가능한 템플릿
- **Skills**: /명령으로 호출 가능한 스킬
- **Archive**: 참고용 원본 프롬프트 (있으면)

각 항목은 파일 경로 + 한 줄 설명.
