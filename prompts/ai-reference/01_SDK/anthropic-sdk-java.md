---

Java용 Claude SDK

Java용 Claude SDK는 Java 애플리케이션에서 Claude API에 접근할 수 있도록 한다.
문서
전체 문서는 platform.claude.com/docs/en/api/sdks/java 에서 확인할 수 있다.
설치

Gradle
implementation("com.anthropic:anthropic-java:2.16.0")
Maven
<dependency>
  <groupId>com.anthropic</groupId>
  <artifactId>anthropic-java</artifactId>
  <version>2.16.0</version>
</dependency>

시작하기
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.Message;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.Model;

// Configures using the `ANTHROPIC_API_KEY` environment variable
AnthropicClient client = AnthropicOkHttpClient.fromEnv();

MessageCreateParams params = MessageCreateParams.builder()
    .maxTokens(1024L)
    .addUserMessage("Hello, Claude")
    .model(Model.CLAUDE_OPUS_4_6)
    .build();
Message message = client.messages().create(params);
요구사항
Java 8+
기여하기
CONTRIBUTING.md 를 참조하라.
라이선스
이 프로젝트는 MIT License로 라이선스된다. 자세한 내용은 LICENSE 파일을 참조하라.
