---

Anthropic Ruby API 라이브러리
Anthropic Ruby 라이브러리는 Ruby 3.2.0+ 애플리케이션에서 Anthropic REST API에 편리하게 접근할 수 있도록 한다. Yard, RBS, RBI 형식의 포괄적인 타입과 docstring을 함께 제공한다 — Sorbet과 함께 사용하는 방법은 아래를 참조하라. 표준 라이브러리의 `net/http` 가 HTTP 전송으로 사용되며, `connection_pool` gem을 통한 연결 풀링이 적용된다.
문서
이 gem의 릴리스 문서는 RubyDoc에서 확인할 수 있다.
REST API 문서는 docs.anthropic.com 에서 확인할 수 있다.
설치
이 gem을 사용하려면, Bundler를 통해 애플리케이션의 Gemfile에 다음을 추가하여 설치한다:

gem "anthropic", "~> 1.23.0"

피드백
추천 사항, 버그, 혼란스러운 점 또는 다른 무엇이든 있다면 github issue를 생성하라. 부끄러워하지 말라 — 우리는 여러분의 어떤 의견이나 생각도 매우 열려 있다!
좀 더 본격적인 이슈는 issue를 만들어달라. 더 작은 이슈나 의식의 흐름은 여기 고정된 issue를 사용할 수 있다.
사용법
require "bundler/setup"
require "anthropic"

anthropic = Anthropic::Client.new(
  api_key: ENV["ANTHROPIC_API_KEY"] # This is the default and can be omitted
)

message = anthropic.messages.create(
  max_tokens: 1024,
  messages: [{role: "user", content: "Hello, Claude"}],
  model: "claude-sonnet-4-5-20250929"
)

puts(message.content)
스트리밍
Server-Sent Events (SSE)를 사용한 스트리밍 응답을 지원한다.
stream = anthropic.messages.stream(
  max_tokens: 1024,
  messages: [{role: "user", content: "Hello, Claude"}],
  model: "claude-sonnet-4-5-20250929"
)

stream.each do |message|
  puts(message.type)
end
스트리밍 헬퍼
이 라이브러리는 메시지 스트리밍을 위한 여러 편의 기능을 제공한다. 예를 들어:
stream = anthropic.messages.stream(
  max_tokens: 1024,
  messages: [{role: :user, content: "Say hello there!"}],
  model: :"claude-sonnet-4-5-20250929"
)

stream.text.each do |text|
  print(text)
end
`anthropic.messages.stream(...)` 을 사용한 스트리밍은 누적과 SDK 특정 이벤트를 포함한 다양한 헬퍼를 노출한다.
입력 스키마 및 도구 호출
도구를 위한 구조화된 데이터 클래스를 정의하고 Claude가 자동으로 실행할 수 있도록 하는 헬퍼 메커니즘이 있다.
더 자세한 사용 정보는 `helpers.md` 를 참조하라.
class CalculatorInput < Anthropic::BaseModel
  required :lhs, Float
  required :rhs, Float
  required :operator, Anthropic::InputSchema::EnumOf[:+, :-, :*, :/]
end

class Calculator < Anthropic::BaseTool
  input_schema CalculatorInput

  def call(expr)
    expr.lhs.public_send(expr.operator, expr.rhs)
  end
end

# Automatically handles tool execution loop
client.beta.messages.tool_runner(
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 1024,
  messages: [{role: "user", content: "What's 15 * 7?"}],
  tools: [Calculator.new]
).each_message { puts _1.content }
구조화된 출력
`output_config` 매개변수를 사용하여 Claude의 응답이 특정 JSON 스키마를 따르도록 제약한다:
class FamousNumber < Anthropic::BaseModel
  required :value, Float
  optional :reason, String, doc: "why is this number mathematically significant?"
end

class Output < Anthropic::BaseModel
  required :numbers, Anthropic::ArrayOf[FamousNumber], min_length: 3, max_length: 5
end

message = anthropic.messages.create(
  model: "claude-sonnet-4-5-20250929",
  max_tokens: 1024,
  messages: [{role: "user", content: "give me some famous numbers"}],
  output_config: {format: Output}
)

# Access the parsed response
message.parsed_output
# => #<Output numbers=[#<FamousNumber value=3.14159... reason="Pi is...">...]>
스트리밍과 더 많은 예제는 `helpers.md` 를 참조하라.
페이지네이션
Anthropic API의 list 메서드는 페이지네이션된다.
이 라이브러리는 각 list 응답과 함께 자동 페이지네이션 이터레이터를 제공하므로, 후속 페이지를 수동으로 요청할 필요가 없다:
page = anthropic.messages.batches.list(limit: 20)

# Fetch single item from page.
batch = page.data[0]
puts(batch.id)

# Automatically fetches more pages as needed.
page.auto_paging_each do |batch|
  puts(batch.id)
end
또는, 페이지를 다루는 더 세밀한 제어를 위해 `#next_page?` 및 `#next_page` 메서드를 사용할 수 있다.
if page.next_page?
  new_page = page.next_page
  puts(new_page.data[0].id)
end
파일 업로드
파일 업로드에 해당하는 요청 매개변수는 원시 콘텐츠, `Pathname` 인스턴스, `StringIO` 등으로 전달할 수 있다.
require "pathname"

# Use `Pathname` to send the filename and/or avoid paging a large file into memory:
file_metadata = anthropic.beta.files.upload(file: Pathname("/path/to/file"))

# Alternatively, pass file contents or a `StringIO` directly:
file_metadata = anthropic.beta.files.upload(file: File.read("/path/to/file"))

# Or, to control the filename and/or content type:
file = Anthropic::FilePart.new(File.read("/path/to/file"), filename: "/path/to/file", content_type: "…")
file_metadata = anthropic.beta.files.upload(file: file)

puts(file_metadata.id)
원시 IO 디스크립터를 전달할 수도 있지만, 라이브러리가 디스크립터가 파일인지 파이프(되감기 불가)인지 확신할 수 없기 때문에 재시도가 비활성화된다.
오류 처리
라이브러리가 API에 연결할 수 없거나 API가 비성공 상태 코드 (즉, 4xx 또는 5xx 응답)를 반환하면, `Anthropic::Errors::APIError` 의 서브클래스가 던져진다:
begin
  message = anthropic.messages.create(
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}],
    model: "claude-sonnet-4-5-20250929"
  )
rescue Anthropic::Errors::APIConnectionError => e
  puts("The server could not be reached")
  puts(e.cause)  # an underlying Exception, likely raised within `net/http`
rescue Anthropic::Errors::RateLimitError => e
  puts("A 429 status code was received; we should back off a bit.")
rescue Anthropic::Errors::APIStatusError => e
  puts("Another non-200-range status code was received")
  puts(e.status)
end
오류 코드는 다음과 같다:

Cause
Error Type

HTTP 400
BadRequestError

HTTP 401
AuthenticationError

HTTP 403
PermissionDeniedError

HTTP 404
NotFoundError

HTTP 409
ConflictError

HTTP 422
UnprocessableEntityError

HTTP 429
RateLimitError

HTTP >= 500
InternalServerError

Other HTTP error
APIStatusError

Timeout
APITimeoutError

Network error
APIConnectionError

재시도
특정 오류는 기본적으로 짧은 지수 백오프와 함께 자동으로 2회 재시도된다.
연결 오류 (예: 네트워크 연결 문제로 인한), 408 Request Timeout, 409 Conflict, 429 Rate Limit, >=500 Internal 오류, 그리고 타임아웃은 모두 기본적으로 재시도된다.
이를 설정하거나 비활성화하려면 `max_retries` 옵션을 사용할 수 있다:
# Configure the default for all requests:
anthropic = Anthropic::Client.new(
  max_retries: 0 # default is 2
)

# Or, configure per-request:
anthropic.messages.create(
  max_tokens: 1024,
  messages: [{role: "user", content: "Hello, Claude"}],
  model: "claude-sonnet-4-5-20250929",
  request_options: {max_retries: 5}
)
타임아웃
기본적으로 요청은 600초 후에 타임아웃된다. 이를 설정하거나 비활성화하려면 `timeout` 옵션을 사용할 수 있다:
# Configure the default for all requests:
anthropic = Anthropic::Client.new(
  timeout: nil # default is 600
)

# Or, configure per-request:
anthropic.messages.create(
  max_tokens: 1024,
  messages: [{role: "user", content: "Hello, Claude"}],
  model: "claude-sonnet-4-5-20250929",
  request_options: {timeout: 5}
)
타임아웃 시, `Anthropic::Errors::APITimeoutError` 가 발생한다.
타임아웃된 요청은 기본적으로 재시도된다는 점에 유의하라.
AWS Bedrock
이 라이브러리는 `aws-sdk-bedrockruntime` gem과 함께 설치하면 Anthropic Bedrock API도 지원한다.
별도의 `Anthropic::BedrockClient` 클래스를 인스턴스화한 후, 자격 증명 설정을 위해 AWS의 표준 가이드를 사용할 수 있다 (`aws-sdk-ruby` gem README 또는 AWS 문서 참조). 기본 `Anthropic::Client` 클래스와 동일한 API를 가진다.
Bedrock 모델에 필요한 모델 ID는 다르며, 사용하려는 모델에 따라 Anthropic 모델에 대한 AWS의 모델 ID — AWS의 Bedrock 모델 카탈로그에서 찾을 수 있음 — 또는 추론 프로필 id (예: Claude 3.5 Haiku의 경우 `us.anthropic.claude-3-5-haiku-20241022-v1:0`)를 사용해야 한다.
require "bundler/setup"
require "anthropic"

anthropic = Anthropic::BedrockClient.new

message = anthropic.messages.create(
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content: "Hello, Claude"
    }
  ],
  model: "anthropic.claude-sonnet-4-5-20250929-v2:0"
)

puts(message)
더 많은 예제는 `examples/bedrock` 을 참조하라.
Google Vertex
이 라이브러리는 `googleauth` gem과 함께 설치하면 Anthropic Vertex API도 지원한다.
별도의 `Anthropic::VertexClient` 클래스를 import하고 인스턴스화한 후, Application Default Credentials 설정을 위해 Google 가이드를 사용할 수 있다. 기본 `Anthropic::Client` 클래스와 동일한 API를 가진다.
require "bundler/setup"
require "anthropic"

anthropic = Anthropic::VertexClient.new(region: "us-east5", project_id: "my-project-id")

message = anthropic.messages.create(
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content: "Hello, Claude"
    }
  ],
  model: "claude-sonnet-4@20250514"
)

puts(message)
더 많은 예제는 `examples/vertex` 를 참조하라.
고급 개념
BaseModel
모든 매개변수 및 응답 객체는 `Anthropic::Internal::Type::BaseModel` 을 상속하며, 다음을 포함한 여러 편의 기능을 제공한다:

알 수 없는 필드를 포함한 모든 필드는 `obj[:prop]` 구문으로 접근 가능하며, `obj => {prop: prop}` 또는 패턴 매칭 구문으로 구조 분해할 수 있다.

동등성을 위한 구조적 동치성; 두 API 호출이 동일한 값을 반환하면, `==` 로 응답을 비교할 때 `true` 를 반환한다.

인스턴스와 클래스 자체 모두 pretty-print할 수 있다.

`#to_h`, `#deep_to_h`, `#to_json`, `#to_yaml` 같은 헬퍼.

사용자 정의 또는 문서화되지 않은 요청 만들기
문서화되지 않은 속성
모든 엔드포인트에 문서화되지 않은 매개변수를 보내고, 문서화되지 않은 응답 속성을 읽을 수 있다. 다음과 같이:
경고
동일한 이름의 `extra_` 매개변수는 문서화된 매개변수를 재정의한다. 보안상의 이유로, 이러한 메서드는 신뢰할 수 있는 입력 데이터에만 사용되도록 보장하라.

message =
  anthropic.messages.create(
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}],
    model: "claude-sonnet-4-5-20250929",
    request_options: {
      extra_query: {my_query_parameter: value},
      extra_body: {my_body_parameter: value},
      extra_headers: {"my-header": value}
    }
  )

puts(message[:my_undocumented_property])
문서화되지 않은 요청 매개변수
명시적으로 추가 매개변수를 보내려면, 요청 시 `request_options:` 매개변수 아래의 `extra_query`, `extra_body`, `extra_headers` 로 보낼 수 있다. 위 예제에서 보여준 것과 같다.
문서화되지 않은 엔드포인트
인증, 재시도 등의 이점을 유지하면서 문서화되지 않은 엔드포인트에 요청하려면, `client.request` 를 사용해 요청할 수 있다. 다음과 같이:
response = client.request(
  method: :post,
  path: '/undocumented/endpoint',
  query: {"dog": "woof"},
  headers: {"useful-header": "interesting-value"},
  body: {"hello": "world"}
)
동시성 및 연결 풀링
`Anthropic::Client` 인스턴스는 스레드 안전하지만, 진행 중인 HTTP 요청이 없을 때만 fork-safe하다.
`Anthropic::Client` 의 각 인스턴스는 기본 크기가 99인 자체 HTTP 연결 풀을 가진다. 따라서 대부분의 설정에서 애플리케이션당 한 번만 클라이언트를 인스턴스화할 것을 권장한다.
풀에서 사용 가능한 모든 연결이 체크아웃되면, 요청은 새 연결이 사용 가능해질 때까지 기다리며, 대기 시간은 요청 타임아웃에 포함된다.
달리 명시되지 않는 한, SDK의 다른 클래스는 기본 데이터 구조를 보호하는 잠금이 없다.
Sorbet
이 라이브러리는 포괄적인 RBI 정의를 제공하며, `sorbet-runtime` 에 의존하지 않는다.
다음과 같이 타입 안전한 요청 매개변수를 제공할 수 있다:
anthropic.messages.create(
  max_tokens: 1024,
  messages: [Anthropic::MessageParam.new(role: "user", content: "Hello, Claude")],
  model: "claude-sonnet-4-5-20250929"
)
또는, 동등하게:
# Hashes work, but are not typesafe:
anthropic.messages.create(
  max_tokens: 1024,
  messages: [{role: "user", content: "Hello, Claude"}],
  model: "claude-sonnet-4-5-20250929"
)

# You can also splat a full Params class:
params = Anthropic::MessageCreateParams.new(
  max_tokens: 1024,
  messages: [Anthropic::MessageParam.new(role: "user", content: "Hello, Claude")],
  model: "claude-sonnet-4-5-20250929"
)
anthropic.messages.create(**params)
Enums
이 라이브러리는 `sorbet-runtime` 에 의존하지 않기 때문에, `T::Enum` 인스턴스를 제공할 수 없다. 대신, 런타임에서 항상 원시값인 "tagged symbol"을 제공한다:
# :auto
puts(Anthropic::MessageCreateParams::ServiceTier::AUTO)

# Revealed type: `T.all(Anthropic::MessageCreateParams::ServiceTier, Symbol)`
T.reveal_type(Anthropic::MessageCreateParams::ServiceTier::AUTO)
Enum 매개변수는 "완화된(relaxed)" 타입을 가지므로, enum 상수 또는 그 리터럴 값을 전달할 수 있다:
# Using the enum constants preserves the tagged type information:
anthropic.messages.create(
  service_tier: Anthropic::MessageCreateParams::ServiceTier::AUTO,
  # …
)

# Literal values are also permissible:
anthropic.messages.create(
  service_tier: :auto,
  # …
)
버저닝
이 패키지는 SemVer 규칙을 따른다. 라이브러리가 초기 개발 중이고 메이저 버전이 0이므로, API는 언제든지 변경될 수 있다.
이 패키지는 (런타임이 아닌) `*.rbi` 및 `*.rbs` 타입 정의의 개선을 비호환 변경으로 간주하지 않는다.
요구사항
Ruby 3.2.0 이상.
기여하기
contributing 문서를 참조하라.
감사의 말
피드백을 제공하고, `anthropic` Ruby Gem 이름을 기증하고, 첫 번째 Anthropic Ruby SDK를 구축하여 길을 닦아준 @alexrudall에게 감사드린다.
