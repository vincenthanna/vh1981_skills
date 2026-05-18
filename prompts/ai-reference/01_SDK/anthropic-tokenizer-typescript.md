---

Anthropic TypeScript Tokenizer

Anthropic 모델에 보내는 텍스트의 토큰을 계산하기 위한 TypeScript/JavaScript tokenizer.

> **참고**: 이 tokenizer는 Claude 3 이전 모델에서만 정확하다. Claude 3+ 모델의 경우, 대략적인 근사치로만 동작한다. Anthropic은 최신 모델에서 정확한 토큰 수를 얻기 위해 API 응답 본문의 `usage` 필드를 사용할 것을 권장한다.

## 설치

```bash
npm install --save @anthropic-ai/tokenizer
# or
yarn add @anthropic-ai/tokenizer
```

## 사용법

```typescript
import { countTokens } from '@anthropic-ai/tokenizer';

const tokenCount = countTokens('Hello, world!');
console.log(tokenCount); // number of tokens
```

## 요구사항

- Node.js 12+
- Deno v1.28.0+ (실험적 지원)

## 상태

베타 — Claude 3 이전 모델에서만 정확함.

## 라이선스

MIT

## 링크

- GitHub: https://github.com/anthropics/anthropic-tokenizer-typescript
