---

Claude SDK for PHP

The Claude SDK for PHP provides convenient access to the Anthropic REST API from any PHP 8.1.0+ application. The SDK uses named parameters and provides value objects with builder patterns for a clean, idiomatic PHP experience.

Note: The PHP SDK is currently in beta. APIs may change between versions.

Documentation
Full documentation is available at platform.claude.com/docs/en/api/sdks/php.

Installation
composer require "anthropic-ai/sdk"

Requirements
PHP 8.1.0+

Getting Started
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

Streaming
The SDK supports streaming responses using Server-Sent Events (SSE):
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

Error Handling
When the API returns a non-success status code or a connection fails, a subclass of Anthropic\Core\Exceptions\APIException is thrown:
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

Error types by HTTP status:

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

Retries
Certain errors are automatically retried 2 times by default with a short exponential backoff. Connection errors, 408, 409, 429, and >= 500 status codes are all retried by default.

You can configure retry behavior:
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

Pagination
List methods provide auto-paginating iterators:
<?php

use Anthropic\Client;

$client = new Client(
  apiKey: getenv('ANTHROPIC_API_KEY') ?: 'my-anthropic-api-key'
);

$page = $client->beta->messages->batches->list(limit: 20);

foreach ($page->pagingEachItem() as $item) {
  var_dump($item->id);
}

Value Objects
The SDK provides value objects with both static constructors and builders:
// Static constructor with named parameters (recommended)
Base64ImageSource::with(data: "U3RhaW5sZXNzIHJvY2tz", ...)

// Builder pattern
(new Base64ImageSource)->withData("U3RhaW5sZXNzIHJvY2tz")

Advanced Usage
You can send undocumented parameters and access undocumented endpoints:
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

Contributing
See CONTRIBUTING.md.
License
This project is licensed under the MIT License. See the LICENSE file for details.
