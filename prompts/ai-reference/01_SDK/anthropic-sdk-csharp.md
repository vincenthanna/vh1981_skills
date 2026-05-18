---

Anthropic C# API 라이브러리

📦 패키지 버전 관리 업데이트
버전 10+ 부터, `Anthropic` 패키지는 공식 Anthropic C# SDK이다.
패키지 버전 3.X 이하는 이전에 tryAGI 커뮤니티가 제작한 SDK용으로 사용되었으며, `tryAGI.Anthropic` 으로 이전되었다. 프로젝트에서 이전 클라이언트를 계속 사용해야 한다면, 패키지 참조를 `tryAGI.Anthropic` 으로 업데이트하라.
Claude 생태계와 C# 커뮤니티를 위해 일해온 `tryAGI.Anthropic` 의 메인테이너들에게 감사한다.

Anthropic C# SDK는 C#으로 작성된 애플리케이션에서 Anthropic REST API에 편리하게 접근할 수 있도록 한다.
REST API 문서는 docs.anthropic.com 에서 확인할 수 있다.
설치
NuGet에서 패키지를 설치한다:
dotnet add package Anthropic
요구사항
이 라이브러리는 .NET Standard 2.0 이상을 요구한다.
사용법
완전하고 실행 가능한 예제는 `examples` 디렉터리를 참조하라.
using System;
using Anthropic;
using Anthropic.Models.Messages;

AnthropicClient client = new();

MessageCreateParams parameters = new()
{
    MaxTokens = 1024,
    Messages =
    [
        new()
        {
            Role = Role.User,
            Content = "Hello, Claude",
        },
    ],
    Model = Model.ClaudeSonnet4_5_20250929,
};

var message = await client.Messages.Create(parameters);

Console.WriteLine(message);
클라이언트 설정
환경 변수를 사용해 클라이언트를 설정한다:
using Anthropic;

// Configured using the ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN and ANTHROPIC_BASE_URL environment variables
AnthropicClient client = new();
또는 직접 설정한다:
using Anthropic;

AnthropicClient client = new() { ApiKey = "my-anthropic-api-key" };
두 방식을 조합하여 사용할 수도 있다.
사용 가능한 옵션은 다음 표를 참조하라:

Property
Environment variable
Required
Default value

ApiKey
ANTHROPIC_API_KEY
false
-

AuthToken
ANTHROPIC_AUTH_TOKEN
false
-

BaseUrl
ANTHROPIC_BASE_URL
true
"https://api.anthropic.com"

설정 변경
동일한 연결 및 스레드 풀을 재사용하면서 일시적으로 수정된 클라이언트 설정을 사용하려면, 클라이언트나 서비스에 대해 `WithOptions` 를 호출한다:
using System;

var message = await client
    .WithOptions(options =>
        options with
        {
            BaseUrl = "https://example.com",
            Timeout = TimeSpan.FromSeconds(42),
        }
    )
    .Messages.Create(parameters);

Console.WriteLine(message);
`with` 표현식을 사용하면 수정된 옵션을 쉽게 구성할 수 있다.
`WithOptions` 메서드는 원본 클라이언트나 서비스에 영향을 주지 않는다.
요청과 응답
Anthropic API에 요청을 보내려면, 일부 `Params` 클래스의 인스턴스를 구성하여 해당 클라이언트 메서드에 전달한다. 응답이 수신되면 C# 클래스의 인스턴스로 역직렬화된다.
예를 들어, `client.Messages.Create` 는 `MessageCreateParams` 인스턴스와 함께 호출되어야 하며, `Task<Message>` 인스턴스를 반환한다.
중요: 장시간 실행되는 요청에는 **반드시** 스트리밍을 사용할 것을 강력히 권장한다.

스트리밍을 사용하지 않고 큰 `MaxTokens` 값을 설정하는 것은 권장하지 않는다. 일부 네트워크는 일정 시간 후에 유휴 연결을 끊을 수 있어, Anthropic으로부터 응답을 받지 못한 채 요청이 실패하거나 타임아웃될 수 있다. 우리는 이런 네트워크의 영향을 줄이기 위해 주기적으로 API를 핑하여 연결을 유지한다.
스트리밍이 아닌 요청이 10분 이상 걸릴 것으로 예상되는 경우 SDK는 오류를 던진다. 스트리밍 메서드를 사용하거나 클라이언트 또는 요청 수준에서 타임아웃을 재정의하면 이 오류가 비활성화된다.
스트리밍
SDK는 응답 "청크" 스트림을 반환하는 메서드를 정의한다. 각 청크는 전체 응답을 기다리지 않고 도착하는 즉시 개별적으로 처리할 수 있다. 스트리밍 메서드는 일반적으로 SSE 또는 JSONL 응답에 해당한다.
이러한 메서드 중 일부는 스트리밍 및 비스트리밍 변형이 있을 수 있지만, 스트리밍 메서드는 비스트리밍 변형이 없더라도 항상 이름에 `Streaming` 접미사가 붙는다.
이러한 스트리밍 메서드는 `IAsyncEnumerable` 을 반환한다:
using System;
using Anthropic.Models.Messages;

MessageCreateParams parameters = new()
{
    MaxTokens = 1024,
    Messages =
    [
        new()
        {
            Role = Role.User,
            Content = "Hello, Claude",
        },
    ],
    Model = Model.ClaudeSonnet4_5_20250929,
};

await foreach (var message in client.Messages.CreateStreaming(parameters))
{
    Console.WriteLine(message);
}
Aggregators
`Messages` 및 `BetaMessages` 스트리밍 엔드포인트 모두 비스트리밍 대응 메서드와 동일한 객체를 생성할 수 있는 내장 aggregator를 가지고 있다.
`CreateStreaming` 메서드가 반환하는 `IAsyncEnumerable` 에 대한 `.Aggregate()` 확장을 통해 전체 결과 객체만 가져오거나, LINQ 트리에 외부 aggregator를 삽입할 수 있다:
IAsyncEnumerable<RawMessageStreamEvent> responseUpdates = client.Messages.CreateStreaming(
    parameters
);

// This produces a single object based on the streaming output.
var message = await responseUpdates.Aggregate().ConfigureAwait(false);

// You can also add an aggregator as part of your LINQ chain to get realtime streaming and aggregation

var aggregator = new MessageContentAggregator();
await foreach (RawMessageStreamEvent rawEvent in responseUpdates.CollectAsync(aggregator))
{
    // Do something with the stream events
    if (rawEvent.TryPickContentBlockDelta(out var delta))
    {
        if (delta.Delta.TryPickThinking(out var thinkingDelta))
        {
            Console.Write(thinkingDelta.Thinking);
        }
        else if (delta.Delta.TryPickText(out var textDelta))
        {
            Console.Write(textDelta.Text);
        }
    }
}

// And then get the full aggregated message.
var fullMessage = await aggregator.Message();
IChatClient
SDK는 `Microsoft.Extensions.AI.Abstractions` 라이브러리의 `IChatClient` 인터페이스 구현을 제공한다.
이를 통해 `AnthropicClient` (및 `Anthropic.Services.IBetaService`) 를 이러한 핵심 추상화와 통합되는 다른 라이브러리와 함께 사용할 수 있다. 예를 들어, MCP C# SDK (`ModelContextProtocol`) 라이브러리의 도구를 `IChatClient` 를 통해 노출된 `AnthropicClient` 와 직접 사용할 수 있다.
using Anthropic;
using Microsoft.Extensions.AI;
using ModelContextProtocol.Client;

// Configured using the ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN and ANTHROPIC_BASE_URL environment variables
IChatClient chatClient = client.AsIChatClient("claude-haiku-4-5")
    .AsBuilder()
    .UseFunctionInvocation()
    .Build();

// Using McpClient from the MCP C# SDK
McpClient learningServer = await McpClient.CreateAsync(
    new HttpClientTransport(new() { Endpoint = new("https://learn.microsoft.com/api/mcp") }));

ChatOptions options = new() { Tools = [.. await learningServer.ListToolsAsync()] };

Console.WriteLine(await chatClient.GetResponseAsync("Tell me about IChatClient", options));
바이너리 응답
SDK는 바이너리 응답을 반환하는 메서드를 정의하며, 이는 JSON이 아닌 데이터처럼 굳이 파싱할 필요가 없는 API 응답에 사용된다.
이러한 메서드는 `HttpResponse` 를 반환한다:
using System;
using Anthropic.Models.Beta.Files;

FileDownloadParams parameters = new() { FileID = "file_id" };

var response = await client.Beta.Files.Download(parameters);

Console.WriteLine(response);
응답 콘텐츠를 파일이나 `Stream` 에 저장하려면 `CopyToAsync` 메서드를 사용한다:
using System.IO;

using var response = await client.Beta.Files.Download(parameters);
using var contentStream = await response.ReadAsStream();
using var fileStream = File.Open(path, FileMode.OpenOrCreate);
await contentStream.CopyToAsync(fileStream); // Or any other Stream
원시 응답
SDK는 응답을 C# 클래스의 인스턴스로 역직렬화하는 메서드를 정의한다. 그러나 이러한 메서드는 응답 헤더, 상태 코드 또는 원시 응답 본문에 대한 접근을 제공하지 않는다.
이 데이터에 접근하려면, 클라이언트나 서비스의 HTTP 메서드 호출 앞에 `WithRawResponse` 를 붙인다:
var response = await client.WithRawResponse.Messages.Create(parameters);
var statusCode = response.StatusCode;
var headers = response.Headers;
원시 `HttpResponseMessage` 는 `RawMessage` 속성을 통해서도 접근할 수 있다.
비스트리밍 응답의 경우, 필요하다면 응답을 C# 클래스의 인스턴스로 역직렬화할 수 있다:
using System;
using Anthropic.Models.Messages;

var response = await client.WithRawResponse.Messages.Create(parameters);
Message deserialized = await response.Deserialize();
Console.WriteLine(deserialized);
스트리밍 응답의 경우, 필요하다면 응답을 `IAsyncEnumerable` 로 역직렬화할 수 있다:
using System;

var response = await client.WithRawResponse.Messages.CreateStreaming(parameters);
await foreach (var item in response.Enumerate())
{
    Console.WriteLine(item);
}
오류 처리
SDK는 사용자 정의 unchecked 예외 타입을 던진다:

AnthropicApiException: API 오류의 기본 클래스. 각 HTTP 상태 코드에 대해 던져지는 예외 서브클래스는 다음 표를 참조하라:

Status
Exception

400
AnthropicBadRequestException

401
AnthropicUnauthorizedException

403
AnthropicForbiddenException

404
AnthropicNotFoundException

422
AnthropicUnprocessableEntityException

429
AnthropicRateLimitException

5xx
Anthropic5xxException

others
AnthropicUnexpectedStatusCodeException

추가로, 모든 4xx 오류는 `Anthropic4xxException` 을 상속한다.

AnthropicSseException: 성공적인 초기 HTTP 응답 이후 SSE 스트리밍 중 발생한 오류에 대해 던져진다.

AnthropicIOException: I/O 네트워킹 오류.

AnthropicInvalidDataException: 성공적으로 파싱된 데이터를 해석하지 못함. 예를 들어, 필수로 가정된 속성에 접근하려 했지만 API가 응답에서 예기치 않게 그것을 생략한 경우.

AnthropicException: 모든 예외의 기본 클래스.

페이지네이션
SDK는 결과의 페이지네이션된 목록을 반환하는 메서드를 정의한다. 결과를 한 페이지씩 또는 모든 페이지에 걸쳐 항목별로 접근할 수 있는 편리한 방법을 제공한다.
자동 페이지네이션
모든 페이지의 모든 결과를 순회하려면, 필요에 따라 자동으로 더 많은 페이지를 가져오는 `Paginate` 메서드를 사용한다. 이 메서드는 `IAsyncEnumerable` 을 반환한다:
using System;

var page = await client.Beta.Messages.Batches.List(parameters);
await foreach (var item in page.Paginate())
{
    Console.WriteLine(item);
}
수동 페이지네이션
개별 페이지 항목에 접근하고 다음 페이지를 수동으로 요청하려면, `Items` 속성과 `HasNext`, `Next` 메서드를 사용한다:
using System;

var page = await client.Beta.Messages.Batches.List();
while (true)
{
    foreach (var item in page.Items)
    {
        Console.WriteLine(item);
    }
    if (!page.HasNext())
    {
        break;
    }
    page = await page.Next();
}
네트워크 옵션
재시도
SDK는 기본적으로 요청 사이에 짧은 지수 백오프를 두고 자동으로 2회 재시도한다.
다음 오류 타입만 재시도된다:

연결 오류 (예: 네트워크 연결 문제로 인한)
408 Request Timeout
409 Conflict
429 Rate Limit
5xx Internal

API가 SDK에게 재시도하거나 재시도하지 말도록 명시적으로 지시할 수도 있다.
사용자 정의 재시도 횟수를 설정하려면, `MaxRetries` 메서드를 사용해 클라이언트를 설정한다:
using Anthropic;

AnthropicClient client = new() { MaxRetries = 3 };
또는 `WithOptions` 를 사용해 단일 메서드 호출을 설정한다:
using System;

var message = await client
    .WithOptions(options =>
        options with { MaxRetries = 3 }
    )
    .Messages.Create(parameters);

Console.WriteLine(message);
타임아웃
요청은 기본적으로 10분 후 타임아웃된다.
사용자 정의 타임아웃을 설정하려면, `Timeout` 옵션을 사용해 클라이언트를 설정한다:
using System;
using Anthropic;

AnthropicClient client = new() { Timeout = TimeSpan.FromSeconds(42) };
또는 `WithOptions` 를 사용해 단일 메서드 호출을 설정한다:
using System;

var message = await client
    .WithOptions(options =>
        options with { Timeout = TimeSpan.FromSeconds(42) }
    )
    .Messages.Create(parameters);

Console.WriteLine(message);
문서화되지 않은 API 기능
SDK는 문서화된 API의 편리한 사용을 위해 타입이 지정되어 있다. 그러나 문서화되지 않았거나 아직 지원되지 않는 API 부분에서의 작업도 지원한다.
응답 검증
드물게 API가 예상 타입과 일치하지 않는 응답을 반환할 수 있다. 예를 들어, SDK가 속성이 문자열을 포함할 것으로 예상했으나 API가 다른 것을 반환할 수 있다.
기본적으로 SDK는 이 경우 예외를 던지지 않는다. 해당 속성에 직접 접근하는 경우에만 `AnthropicInvalidDataException` 을 던진다.
응답이 처음부터 완전히 잘 타입화되었는지 확인하고 싶다면, `Validate` 를 호출하거나:
var message = client.Messages.Create(parameters);
message.Validate();
또는 `ResponseValidation` 옵션을 사용해 클라이언트를 설정한다:
using Anthropic;

AnthropicClient client = new() { ResponseValidation = true };
또는 `WithOptions` 를 사용해 단일 메서드 호출을 설정한다:
using System;

var message = await client
    .WithOptions(options =>
        options with { ResponseValidation = true }
    )
    .Messages.Create(parameters);

Console.WriteLine(message);
시맨틱 버저닝
이 패키지는 일반적으로 SemVer 규칙을 따르지만, 특정 하위 호환되지 않는 변경 사항은 마이너 버전으로 릴리스될 수 있다:

기술적으로는 공개되어 있지만 외부 사용을 의도하거나 문서화하지 않은 라이브러리 내부 변경. (이러한 내부에 의존하고 있다면 GitHub issue를 열어 알려달라.)
실제로 대다수 사용자에게 영향을 주지 않을 것으로 예상되는 변경.

우리는 하위 호환성을 진지하게 다루며, 원활한 업그레이드 경험을 신뢰할 수 있도록 노력한다.
피드백을 환영한다. 질문, 버그 또는 제안 사항이 있다면 issue를 열어달라.
