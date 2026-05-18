---

PHP용 Claude SDK

PHP용 Claude SDK는 PHP 8.1.0+ 애플리케이션에서 Anthropic REST API에 편리하게 접근할 수 있도록 한다. SDK는 명명된 매개변수를 사용하고 builder 패턴을 가진 value object를 제공하여 깔끔하고 관용적인 PHP 경험을 제공한다.

참고: PHP SDK는 현재 베타이다. API는 버전 간에 변경될 수 있다.

문서
전체 문서는 platform.claude.com/docs/en/api/sdks/php 에서 확인할 수 있다.

설치
composer require "anthropic-ai/sdk"

요구사항
PHP 8.1.0+

시작하기
<?php

use Anthropic\Client;

$client = new Client(
  apiKey: getenv('ANTHROPIC_API_KEY') ?: 'my-anthropic-api-key'
);

$message = $client->messages->create(
  maxTokens: 1024,
  messages: [['role' => 'user', 'content' => 'Hello, Claude']],
  model: 'claude-opus-4-6',
);

var_dump($message->content);

스트리밍
SDK는 Server-Sent Events (SSE)를 사용한 스트리밍 응답을 지원한다:
<?php

use Anthropic\Client;

$client = new Client(
  apiKey: getenv('ANTHROPIC_API_KEY') ?: 'my-anthropic-api-key'
);

$stream = $client->messages->createStream(
  maxTokens: 1024,
  messages: [['role' => 'user', 'content' => 'Hello, Claude']],
  model: 'claude-opus-4-6',
);

foreach ($stream as $message) {
  var_dump($message);
}

오류 처리
API가 비성공 상태 코드를 반환하거나 연결이 실패하면, `Anthropic\Core\Exceptions\APIException` 의 서브클래스가 던져진다:
<?php

use Anthropic\Client;
use Anthropic\Core\Exceptions\APIConnectionException;
use Anthropic\Core\Exceptions\APIStatusException;
use Anthropic\Core\Exceptions\RateLimitException;

$client = new Client();

try {
  $message = $client->messages->create(
    maxTokens: 1024,
    messages: [['role' => 'user', 'content' => 'Hello, Claude']],
    model: 'claude-opus-4-6',
  );
} catch (APIConnectionException $e) {
  echo "The server could not be reached", PHP_EOL;
  var_dump($e->getPrevious());
} catch (RateLimitException $_) {
  echo "A 429 status code was received; we should back off a bit.", PHP_EOL;
} catch (APIStatusException $e) {
  echo "Another non-200-range status code was received", PHP_EOL;
  echo $e->getMessage();
}

HTTP 상태별 오류 타입:

HTTP 400 - BadRequestException
HTTP 401 - AuthenticationException
HTTP 403 - PermissionDeniedException
HTTP 404 - NotFoundException
HTTP 409 - ConflictException
HTTP 422 - UnprocessableEntityException
HTTP 429 - RateLimitException
HTTP >= 500 - InternalServerException
Timeout - APITimeoutException
Network error - APIConnectionException

재시도
특정 오류는 기본적으로 짧은 지수 백오프와 함께 자동으로 2회 재시도된다. 연결 오류, 408, 409, 429, 및 >= 500 상태 코드는 모두 기본적으로 재시도된다.

재시도 동작을 설정할 수 있다:
<?php

use Anthropic\Client;
use Anthropic\RequestOptions;

// Configure the default for all requests:
$client = new Client(requestOptions: RequestOptions::with(maxRetries: 0));

// Or, configure per-request:
$result = $client->messages->create(
  maxTokens: 1024,
  messages: [['role' => 'user', 'content' => 'Hello, Claude']],
  model: 'claude-opus-4-6',
  requestOptions: RequestOptions::with(maxRetries: 5),
);

페이지네이션
list 메서드는 자동 페이지네이션 이터레이터를 제공한다:
<?php

use Anthropic\Client;

$client = new Client(
  apiKey: getenv('ANTHROPIC_API_KEY') ?: 'my-anthropic-api-key'
);

$page = $client->beta->messages->batches->list(limit: 20);

foreach ($page->pagingEachItem() as $item) {
  var_dump($item->id);
}

Value Object
SDK는 정적 생성자와 builder를 모두 가진 value object를 제공한다:
// Static constructor with named parameters (recommended)
Base64ImageSource::with(data: "U3RhaW5sZXNzIHJvY2tz", ...)

// Builder pattern
(new Base64ImageSource)->withData("U3RhaW5sZXNzIHJvY2tz")

고급 사용법
문서화되지 않은 매개변수를 보내고 문서화되지 않은 엔드포인트에 접근할 수 있다:
$message = $client->messages->create(
  maxTokens: 1024,
  messages: [['role' => 'user', 'content' => 'Hello, Claude']],
  model: 'claude-opus-4-6',
  requestOptions: RequestOptions::with(
    extraQueryParams: ['my_query_parameter' => 'value'],
    extraBodyParams: ['my_body_parameter' => 'value'],
    extraHeaders: ['my-header' => 'value'],
  ),
);

기여하기
CONTRIBUTING.md 를 참조하라.
라이선스
이 프로젝트는 MIT License로 라이선스된다. 자세한 내용은 LICENSE 파일을 참조하라.
