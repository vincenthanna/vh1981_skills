---

Claude SDK for TypeScript
 
이 라이브러리는 TypeScript 또는 JavaScript 환경에서 Claude API에 편리하게 접근할 수 있도록 제공한다.
전체 API 문서는 platform.claude.com/docs 또는 api.md 에서 확인할 수 있다.
Installation
npm install @anthropic-ai/sdk
Usage

import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  apiKey: process.env['ANTHROPIC_API_KEY'], // This is the default and can be omitted
});

const message = await client.messages.create({
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Hello, Claude' }],
  model: 'claude-sonnet-4-5-20250929',
});

console.log(message.content);
Streaming responses
Server Sent Events(SSE)를 사용하는 스트리밍 응답을 지원한다.
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

const stream = await client.messages.create({
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Hello, Claude' }],
  model: 'claude-sonnet-4-5-20250929',
  stream: true,
});
for await (const messageStreamEvent of stream) {
  console.log(messageStreamEvent.type);
}
스트림을 취소해야 한다면 루프에서 break 하거나
stream.controller.abort() 를 호출하면 된다.
Request & Response types
이 라이브러리는 모든 요청 파라미터와 응답 필드에 대한 TypeScript 정의를 포함한다. 다음과 같이 import 하여 사용할 수 있다:

import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  apiKey: process.env['ANTHROPIC_API_KEY'], // This is the default and can be omitted
});

const params: Anthropic.MessageCreateParams = {
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Hello, Claude' }],
  model: 'claude-sonnet-4-5-20250929',
};
const message: Anthropic.Message = await client.messages.create(params);
각 메서드, 요청 파라미터, 응답 필드에 대한 문서는 docstring 으로 제공되며, 대부분의 최신 에디터에서 hover 시 표시된다.
Counting Tokens
주어진 요청의 정확한 사용량은 usage 응답 속성을 통해 확인할 수 있다. 예:
const message = await client.messages.create(...)
console.log(message.usage)
// { input_tokens: 25, output_tokens: 13 }
Streaming Helpers
이 라이브러리는 메시지 스트리밍을 위한 여러 편의 기능을 제공한다. 예시:
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic();

async function main() {
  const stream = anthropic.messages
    .stream({
      model: 'claude-sonnet-4-5-20250929',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: 'Say hello there!',
        },
      ],
    })
    .on('text', (text) => {
      console.log(text);
    });

  const message = await stream.finalMessage();
  console.log(message);
}

main();
client.messages.stream(...) 을 사용한 스트리밍은 이벤트 핸들러 및 누적(accumulation) 기능을 포함한 다양한 헬퍼를 노출한다.
대안으로 client.messages.create({ ..., stream: true }) 를 사용할 수 있는데, 이것은 단지 스트림 이벤트의 async iterable 만 반환하므로 메모리를 더 적게 사용한다(최종 메시지 객체를 만들어주지 않는다).
MCP Helpers
이 SDK는 Model Context Protocol(MCP) 서버와의 통합을 위한 헬퍼를 제공한다. 이 헬퍼들은 MCP 타입을 Anthropic API 타입으로 변환하여 MCP tools, prompts, resources 를 다룰 때의 boilerplate 를 줄여준다.

참고: Claude API 는 또한 Claude 가 원격 MCP 서버에 직접 연결할 수 있게 해주는 mcp_servers 파라미터도 지원한다.

URL 로 접근 가능한 원격 서버를 사용하고 tool 지원만 필요한 경우에는 mcp_servers 를 사용하라.
로컬 MCP 서버, prompts, resources 가 필요하거나 MCP 연결을 더 정교하게 제어해야 하는 경우에는 MCP 헬퍼를 사용하라.

import Anthropic from '@anthropic-ai/sdk';
import {
  mcpTools,
  mcpMessages,
  mcpResourceToContent,
  mcpResourceToFile,
} from '@anthropic-ai/sdk/helpers/beta/mcp';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const anthropic = new Anthropic();

// Connect to an MCP server
const transport = new StdioClientTransport({ command: 'mcp-server', args: [] });
const mcpClient = new Client({ name: 'my-client', version: '1.0.0' });
await mcpClient.connect(transport);

// Use MCP prompts
const { messages } = await mcpClient.getPrompt({ name: 'my-prompt' });
const response = await anthropic.beta.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  messages: mcpMessages(messages),
});

// Use MCP tools with toolRunner
const { tools } = await mcpClient.listTools();
const runner = await anthropic.beta.messages.toolRunner({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Use the available tools' }],
  tools: mcpTools(tools, mcpClient),
});

// Use MCP resources as content
const resource = await mcpClient.readResource({ uri: 'file:///path/to/doc.txt' });
await anthropic.beta.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  messages: [
    {
      role: 'user',
      content: [mcpResourceToContent(resource), { type: 'text', text: 'Summarize this document' }],
    },
  ],
});

// Upload MCP resources as files
const resource = await mcpClient.readResource({ uri: 'file:///path/to/data.json' });
await anthropic.beta.files.upload({ file: mcpResourceToFile(resource) });
MCP Error Handling
변환 함수들은 MCP 값이 Claude API 에서 지원되지 않는 경우(예: 지원되지 않는 content type, 지원되지 않는 MIME type, http/https 가 아닌 resource link) UnsupportedMCPValueError 를 던진다.
Message Batches
이 SDK 는 client.messages.batches 네임스페이스 아래에서 Message Batches API 를 지원한다.
Creating a batch
Message Batches 는 요청 배열을 받으며, 각 객체는 custom_id 식별자와 표준 Messages API 와 정확히 동일한 요청 파라미터를 가진다:
await anthropic.messages.batches.create({
  requests: [
    {
      custom_id: 'my-first-request',
      params: {
        model: 'claude-sonnet-4-5-20250929',
        max_tokens: 1024,
        messages: [{ role: 'user', content: 'Hello, world' }],
      },
    },
    {
      custom_id: 'my-second-request',
      params: {
        model: 'claude-sonnet-4-5-20250929',
        max_tokens: 1024,
        messages: [{ role: 'user', content: 'Hi again, friend' }],
      },
    },
  ],
});
Getting results from a batch
Message Batch 가 처리 완료되면(.processing_status === 'ended' 로 표시됨), .batches.results() 로 결과에 접근할 수 있다
const results = await anthropic.messages.batches.results(batch_id);
for await (const entry of results) {
  if (entry.result.type === 'succeeded') {
    console.log(entry.result.message.content);
  }
}
Tool use
이 SDK 는 tool use(function calling) 를 지원한다. 자세한 내용은 문서에서 확인할 수 있다.
SDK 는 tool 을 쉽게 만들고 실행할 수 있도록 헬퍼를 제공한다. tool 입력을 기술하는 데 Zod 스키마 또는 JSON Schema 를 사용할 수 있다. 그런 다음 client.messages.toolRunner() 메서드를 사용해 해당 tool 들을 실행할 수 있다. 이 메서드는 선택된 모델이 생성한 입력을 적절한 tool 에 전달하고, 그 결과를 다시 모델에 전달하는 과정을 처리한다.
import Anthropic from '@anthropic-ai/sdk';

import { betaZodTool } from '@anthropic-ai/sdk/helpers/beta/zod';
import { z } from 'zod';

const anthropic = new Anthropic();

const weatherTool = betaZodTool({
  name: 'get_weather',
  inputSchema: z.object({
    location: z.string(),
  }),
  description: 'Get the current weather in a given location',
  run: (input) => {
    return `The weather in ${input.location} is foggy and 60°F`;
  },
});

const finalMessage = await anthropic.beta.messages.toolRunner({
  model: 'claude-3-5-sonnet-20241022',
  max_tokens: 1000,
  messages: [{ role: 'user', content: 'What is the weather in San Francisco?' }],
  tools: [weatherTool],
});
tool 에서 발생한 오류를 모델에게 다시 보고하려면 run 함수에서 ToolError 를 던지면 된다. 일반 Error 와 달리 ToolError 는 content block 을 받아서, 오류 응답에 이미지나 다른 구조화된 콘텐츠를 포함시킬 수 있다:
import { ToolError } from '@anthropic-ai/sdk/lib/tools/BetaRunnableTool';

const screenshotTool = betaZodTool({
  name: 'take_screenshot',
  inputSchema: z.object({ url: z.string() }),
  run: async (input) => {
    if (!isValidUrl(input.url)) {
      throw new ToolError(`Invalid URL: ${input.url}`);
    }
    const result = await takeScreenshot(input.url);
    if (result.error) {
      // Include the error screenshot so the model can see what went wrong
      throw new ToolError([
        { type: 'text', text: `Failed to load page: ${result.error}` },
        { type: 'image', source: { type: 'base64', data: result.screenshot, media_type: 'image/png' } },
      ]);
    }
    return { type: 'image', source: { type: 'base64', data: result.screenshot, media_type: 'image/png' } };
  },
});
일반 Error 가 던져진 경우, 메시지는 text content block 으로 변환된다.
AWS Bedrock
Anthropic Bedrock API 지원은 별도의 패키지를 통해 제공한다.
File uploads
파일 업로드에 해당하는 요청 파라미터는 다양한 형식으로 전달할 수 있다:

File (또는 동일한 구조의 객체)
fetch Response (또는 동일한 구조의 객체)
fs.ReadStream
toFile 헬퍼의 반환값

files API 는 content-type 을 추론하지 않으므로 명시적으로 설정하는 것을 권장한다:
import fs from 'fs';
import Anthropic, { toFile } from '@anthropic-ai/sdk';

const client = new Anthropic();

// If you have access to Node `fs` we recommend using `fs.createReadStream()`:
await client.beta.files.upload({
  file: await toFile(fs.createReadStream('/path/to/file'), undefined, { type: 'application/json' }),
  betas: ['files-api-2025-04-14'],
});

// Or if you have the web `File` API you can pass a `File` instance:
await client.beta.files.upload({
  file: new File(['my bytes'], 'file.txt', { type: 'text/plain' }),
  betas: ['files-api-2025-04-14'],
});
// You can also pass a `fetch` `Response`:
await client.beta.files.upload({
  file: await fetch('https://somesite/file'),
  betas: ['files-api-2025-04-14'],
});

// Or a `Buffer` / `Uint8Array`
await client.beta.files.upload({
  file: await toFile(Buffer.from('my bytes'), 'file', { type: 'text/plain' }),
  betas: ['files-api-2025-04-14'],
});
await client.beta.files.upload({
  file: await toFile(new Uint8Array([0, 1, 2]), 'file', { type: 'text/plain' }),
  betas: ['files-api-2025-04-14'],
});
Handling errors
라이브러리가 API 에 연결할 수 없거나,
API 가 비성공 상태 코드(즉, 4xx 또는 5xx 응답)를 반환하면
APIError 의 하위 클래스가 던져진다:

const message = await client.messages
  .create({
    max_tokens: 1024,
    messages: [{ role: 'user', content: 'Hello, Claude' }],
    model: 'claude-sonnet-4-5-20250929',
  })
  .catch(async (err) => {
    if (err instanceof Anthropic.APIError) {
      console.log(err.status); // 400
      console.log(err.name); // BadRequestError
      console.log(err.headers); // {server: 'nginx', ...}
    } else {
      throw err;
    }
  });
오류 코드는 다음과 같다:

Status Code
Error Type

400
BadRequestError

401
AuthenticationError

403
PermissionDeniedError

404
NotFoundError

422
UnprocessableEntityError

429
RateLimitError

>=500
InternalServerError

N/A
APIConnectionError

Request IDs

요청 디버깅에 대한 더 자세한 내용은 이 문서를 참고하라

SDK 의 모든 객체 응답은 request-id 응답 헤더에서 추가된 _request_id 속성을 제공하여, 실패한 요청을 빠르게 로깅하고 Anthropic 에 보고할 수 있게 한다.
const message = await client.messages.create({
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Hello, Claude' }],
  model: 'claude-sonnet-4-5-20250929',
});
console.log(message._request_id); // req_018EeWyXxfu5pfWkrYcMdjWG
Retries
특정 오류는 기본적으로 짧은 exponential backoff 와 함께 2회 자동으로 재시도된다.
연결 오류(예: 네트워크 연결 문제), 408 Request Timeout, 409 Conflict,
429 Rate Limit, 그리고 >=500 Internal errors 는 모두 기본으로 재시도된다.
이를 구성하거나 비활성화하려면 maxRetries 옵션을 사용할 수 있다:

// Configure the default for all requests:
const client = new Anthropic({
  maxRetries: 0, // default is 2
});

// Or, configure per-request:
await client.messages.create({
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Hello, Claude' }],
  model: 'claude-sonnet-4-5-20250929',
}, {
  maxRetries: 5,
});
Timeouts
기본적으로 요청은 10분 후 타임아웃된다. 다만 큰 max_tokens 값을 지정하고
스트리밍을 사용하지 않는 경우, 기본 타임아웃은 다음 공식을 사용해 동적으로 계산된다:
const minimum = 10 * 60;
const calculated = (60 * 60 * maxTokens) / 128_000;
return calculated < minimum ? minimum * 1000 : calculated * 1000;
이 결과 요청 또는 client 수준에서 재정의하지 않는 한, max_tokens 파라미터에 따라 스케일링되어 최대 60분까지의 타임아웃이 발생한다.
이는 timeout 옵션으로 구성할 수 있다:

// Configure the default for all requests:
const client = new Anthropic({
  timeout: 20 * 1000, // 20 seconds (default is 10 minutes)
});

// Override per-request:
await client.messages.create({
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Hello, Claude' }],
  model: 'claude-sonnet-4-5-20250929',
}, {
  timeout: 5 * 1000,
});
타임아웃 발생 시 APIConnectionTimeoutError 가 던져진다.
타임아웃이 발생한 요청은 기본으로 두 번 재시도된다는 점에 유의하라.
Long Requests
Important긴 시간이 걸리는 요청에는 streaming Messages API 사용을 강력히 권장한다.

스트리밍을 사용하지 않으면서 큰 max_tokens 값을 설정하는 것은 권장하지 않는다.
일부 네트워크는 일정 시간 후 idle 연결을 끊을 수 있으며, 이로 인해
요청이 실패하거나 Anthropic 로부터 응답을 받지 못한 채 타임아웃될 수 있다.
이 SDK 는 또한 비스트리밍 요청이 대략 10분 이상 걸릴 것으로 예상되는 경우 오류를 던진다.
stream: true 를 전달하거나 client 또는 요청 수준에서 timeout 옵션을 재정의하면 이 오류가 비활성화된다.
비스트리밍 요청의 예상 요청 지연이 타임아웃보다 길면
클라이언트가 응답을 받지 않고 연결을 종료하고 재시도하게 된다.
fetch 구현이 지원하는 경우, idle 연결 타임아웃의 영향을 줄이기 위해
TCP socket keep-alive 옵션을 설정한다.
이는 사용자 정의 proxy 를 구성해 재정의할 수 있다.
Auto-pagination
Claude API 의 list 메서드들은 페이지네이션된다.
for await … of 구문을 사용해 모든 페이지에 걸쳐 항목들을 순회할 수 있다:
async function fetchAllMessageBatches(params) {
  const allMessageBatches = [];
  // Automatically fetches more pages as needed.
  for await (const messageBatch of client.messages.batches.list({ limit: 20 })) {
    allMessageBatches.push(messageBatch);
  }
  return allMessageBatches;
}
대안으로, 한 번에 단일 페이지를 요청할 수도 있다:
let page = await client.messages.batches.list({ limit: 20 });
for (const messageBatch of page.data) {
  console.log(messageBatch);
}

// Convenience methods are provided for manually paginating:
while (page.hasNextPage()) {
  page = await page.getNextPage();
  // ...
}
Default Headers
anthropic-version 헤더를 자동으로 2023-06-01 로 설정해 전송한다.
필요하다면 요청별로 기본 헤더를 설정해 재정의할 수 있다.
다만 이렇게 하면 SDK 에서 잘못된 타입이나 기타 예기치 않거나 정의되지 않은 동작이 발생할 수 있다는 점에 유의하라.
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

const message = await client.messages.create(
  {
    max_tokens: 1024,
    messages: [{ role: 'user', content: 'Hello, Claude' }],
    model: 'claude-sonnet-4-5-20250929',
  },
  { headers: { 'anthropic-version': 'My-Custom-Value' } },
);
Advanced Usage
Accessing raw Response data (e.g., headers)
fetch() 가 반환하는 "raw" Response 는 모든 메서드가 반환하는 APIPromise 타입의 .asResponse() 메서드를 통해 접근할 수 있다.
이 메서드는 성공 응답의 헤더가 수신되는 즉시 반환하며 응답 본문을 소비하지 않으므로, 사용자 정의 파싱 또는 스트리밍 로직을 자유롭게 작성할 수 있다.
원시 Response 와 파싱된 데이터를 함께 얻으려면 .withResponse() 메서드를 사용할 수도 있다.
.asResponse() 와 달리 이 메서드는 본문을 소비하고, 파싱이 완료되면 반환한다.

const client = new Anthropic();

const response = await client.messages
  .create({
    max_tokens: 1024,
    messages: [{ role: 'user', content: 'Hello, Claude' }],
    model: 'claude-sonnet-4-5-20250929',
  })
  .asResponse();
console.log(response.headers.get('X-My-Header'));
console.log(response.statusText); // access the underlying Response object

const { data: message, response: raw } = await client.messages
  .create({
    max_tokens: 1024,
    messages: [{ role: 'user', content: 'Hello, Claude' }],
    model: 'claude-sonnet-4-5-20250929',
  })
  .withResponse();
console.log(raw.headers.get('X-My-Header'));
console.log(message.content);
Logging
Important모든 로그 메시지는 디버깅 용도로만 의도된 것이다. 로그 메시지의 형식과 내용은
릴리스 사이에 변경될 수 있다.

Log levels
log level 은 두 가지 방식으로 구성할 수 있다:

ANTHROPIC_LOG 환경 변수를 통해
logLevel client 옵션을 사용해(설정된 경우 환경 변수보다 우선)

import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  logLevel: 'debug', // Show all log messages
});
사용 가능한 log level (가장 자세한 것부터 가장 적게 출력되는 순):

'debug' - debug 메시지, info, warnings, errors 모두 표시
'info' - info 메시지, warnings, errors 표시
'warn' - warnings 와 errors 표시 (기본값)
'error' - 오직 errors 만 표시
'off' - 모든 로깅 비활성화

'debug' 레벨에서는 헤더와 본문을 포함한 모든 HTTP 요청 및 응답이 로깅된다.
일부 인증 관련 헤더는 마스킹되지만, 요청 및 응답 본문의 민감한 데이터는
여전히 보일 수 있다.
Custom logger
기본적으로 이 라이브러리는 globalThis.console 에 로깅한다. 사용자 정의 logger 를 제공할 수도 있다.
pino, winston, bunyan, consola, signale, @std/log 를 포함한 대부분의 로깅 라이브러리가 지원된다. 사용 중인 logger 가 작동하지 않으면 이슈를 열어달라.
사용자 정의 logger 를 제공하더라도 logLevel 옵션은 여전히 어떤 메시지가 방출되는지를 제어하며, 설정된 레벨보다 낮은
메시지는 logger 로 전송되지 않는다.
import Anthropic from '@anthropic-ai/sdk';
import pino from 'pino';

const logger = pino();

const client = new Anthropic({
  logger: logger.child({ name: 'Anthropic' }),
  logLevel: 'debug', // Send all messages to pino, allowing it to filter
});
Making custom/undocumented requests
이 라이브러리는 문서화된 API 에 편리하게 접근할 수 있도록 타이핑되어 있다. 문서화되지 않은
endpoint, 파라미터, 응답 속성에 접근해야 하는 경우에도 이 라이브러리를 여전히 사용할 수 있다.
Undocumented endpoints
문서화되지 않은 endpoint 에 요청을 보내려면 client.get, client.post 및 기타 HTTP 동사들을 사용할 수 있다.
이러한 요청을 할 때 retries 와 같은 client 옵션이 적용된다.
await client.post('/some/path', {
  body: { some_prop: 'foo' },
  query: { some_query_arg: 'bar' },
});
Undocumented request params
문서화되지 않은 파라미터로 요청을 하려면 해당 파라미터에 // @ts-expect-error 를 사용할 수 있다. 이 라이브러리는
요청이 타입과 일치하는지 런타임에 검증하지 않으므로, 보내는 모든 추가 값들은 그대로 전송된다.
client.messages.create({
  // ...
  // @ts-expect-error baz is not yet public
  baz: 'undocumented option',
});
GET 동사 요청의 경우 추가 파라미터는 query 에 들어가고, 다른 모든 요청은 추가 파라미터를
body 에 전송한다.
명시적으로 추가 인수를 보내려면 query, body, headers 요청 옵션을 사용하면 된다.
Undocumented response properties
문서화되지 않은 응답 속성에 접근하려면, 응답 객체에 // @ts-expect-error 를 사용해 접근하거나,
응답 객체를 필요한 타입으로 캐스팅할 수 있다. 요청 파라미터와 마찬가지로, API 응답에서
추가 속성을 검증하거나 제거하지 않는다.
Customizing the fetch client
기본적으로 이 라이브러리는 전역 fetch 함수가 정의되어 있다고 가정한다.
다른 fetch 함수를 사용하려면, 전역을 polyfill 하거나:
import fetch from 'my-fetch';

globalThis.fetch = fetch;
client 에 전달할 수 있다:
import Anthropic from '@anthropic-ai/sdk';
import fetch from 'my-fetch';

const client = new Anthropic({ fetch });
Fetch options
fetch 함수를 재정의하지 않고 사용자 정의 fetch 옵션을 설정하려면, client 를 인스턴스화하거나 요청을 할 때 fetchOptions 객체를 제공할 수 있다. (요청별 옵션이 client 옵션을 재정의한다.)
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  fetchOptions: {
    // `RequestInit` options
  },
});
Configuring proxies
proxy 동작을 수정하려면 요청에 런타임별 proxy 옵션을 추가하는 사용자 정의 fetchOptions 를
제공할 수 있다:
 Node [docs]
import Anthropic from '@anthropic-ai/sdk';
import * as undici from 'undici';

const proxyAgent = new undici.ProxyAgent('http://localhost:8888');
const client = new Anthropic({
  fetchOptions: {
    dispatcher: proxyAgent,
  },
});
 Bun [docs]
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  fetchOptions: {
    proxy: 'http://localhost:8888',
  },
});
 Deno [docs]
import Anthropic from 'npm:@anthropic-ai/sdk';

const httpClient = Deno.createHttpClient({ proxy: { url: 'http://localhost:8888' } });
const client = new Anthropic({
  fetchOptions: {
    client: httpClient,
  },
});
Beta Features
beta 기능들은 일반 출시 전 조기 피드백을 받고 새로운 기능을 테스트하기 위해 먼저 도입된다. Claude 의 모든 기능과 tool 의 가용성은 여기에서 확인할 수 있다.
대부분의 beta API 기능은 client 의 beta 속성을 통해 접근할 수 있다. 특정 beta 기능을 활성화하려면, 메시지를 생성할 때 betas 필드에 적절한 beta 헤더를 추가해야 한다.
예를 들어, code execution 을 사용하려면:
import Anthropic from 'npm:@anthropic-ai/sdk';

const client = new Anthropic();
const response = await client.beta.messages.create({
  max_tokens: 1024,
  model: 'claude-sonnet-4-5-20250929',
  messages: [
    {
      role: 'user',
      content: [
        {
          type: 'text',
          text: "What's 4242424242 * 4242424242?.",
        },
      ],
    },
  ],
  tools: [
    {
      name: 'code_execution',
      type: 'code_execution_20250522',
    },
  ],
  betas: ['code-execution-2025-05-22'],
});
Frequently Asked Questions
Semantic versioning
이 패키지는 일반적으로 SemVer 규약을 따르지만, 특정 하위 호환이 깨지는 변경 사항은 minor 버전으로 릴리스될 수 있다:

런타임 동작을 깨지 않고 정적 타입에만 영향을 미치는 변경.
기술적으로는 public 이지만 외부 사용을 위한 의도나 문서가 없는 라이브러리 내부 변경. (만약 그러한 내부에 의존하고 있다면 GitHub 이슈를 열어 알려주기 바란다.)
실무에서 절대 다수의 사용자에게 영향을 주지 않을 것으로 예상되는 변경.

하위 호환성을 진지하게 다루며, 원활한 업그레이드 경험에 의존할 수 있도록 노력한다.
피드백을 환영한다; 질문, 버그, 제안이 있다면 이슈를 열어주기 바란다.
Requirements
TypeScript >= 4.9 가 지원된다.
지원되는 런타임은 다음과 같다:

Node.js 20 LTS 또는 그 이상의 (non-EOL) 버전.
Deno v1.28.0 또는 그 이상.
Bun 1.0 또는 그 이상.
Cloudflare Workers.
Vercel Edge Runtime.
Jest 28 이상 (단, "node" environment 사용; "jsdom" 은 현재 지원되지 않음).
Nitro v2.6 이상.
Web browsers: 비밀 API 자격증명 노출을 피하기 위해 기본으로 비활성화됨 (best practice 는 help center 참고). 브라우저 지원을 활성화하려면 dangerouslyAllowBrowser 를 명시적으로 true 로 설정해야 한다.

  More explanation
  Why is this dangerous?
  dangerouslyAllowBrowser 옵션을 활성화하는 것은 client-side 코드에 비밀 API 자격증명을 노출하므로 위험할 수 있다. Web browsers 는 본질적으로 server 환경보다 안전성이 낮으며,
  브라우저에 접근하는 어떤 사용자든 잠재적으로 이 자격증명을 조사, 추출하고 오용할 수 있다. 이는 자격증명을 사용한 무단 접근으로 이어질 수 있으며, 민감한 데이터 또는 기능을 잠재적으로 손상시킬 수 있다.
  When might this not be dangerous?
  브라우저 지원을 활성화하는 것이 큰 위험을 초래하지 않을 수도 있는 특정 시나리오:
  
    Internal Tools: 애플리케이션이 신뢰할 수 있는 사용자만 있는 통제된 내부 환경에서만 사용된다면, 자격증명 노출 위험은 완화될 수 있다.
    Development or debugging purpose: 자격증명이 단기간만 유효하거나 production 환경에서도 사용되지 않거나 자주 회전된다면, 이 기능을 일시적으로 활성화하는 것은 수용 가능할 수 있다.
  

React Native 는 현재 지원되지 않는다는 점에 유의하라.
다른 런타임 환경에 관심이 있다면 GitHub 에서 이슈를 열거나 upvote 해주기 바란다.
Contributing
contributing 문서를 참고하라.
