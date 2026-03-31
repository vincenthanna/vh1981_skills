---

Anthropic TypeScript Tokenizer

A TypeScript/JavaScript tokenizer for counting tokens in text sent to Anthropic's models.

> **Note**: This tokenizer is only accurate for pre-Claude 3 models. For Claude 3+ models, it serves as a rough approximation only. Anthropic recommends using the `usage` field in API response bodies for accurate token counts with newer models.

## Installation

```bash
npm install --save @anthropic-ai/tokenizer
# or
yarn add @anthropic-ai/tokenizer
```

## Usage

```typescript
import { countTokens } from '@anthropic-ai/tokenizer';

const tokenCount = countTokens('Hello, world!');
console.log(tokenCount); // number of tokens
```

## Requirements

- Node.js 12+
- Deno v1.28.0+ (experimental support)

## Status

Beta — accurate for pre-Claude 3 models only.

## License

MIT

## Links

- GitHub: https://github.com/anthropics/anthropic-tokenizer-typescript
