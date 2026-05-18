---

Python용 Claude SDK

Python용 Claude SDK는 Python 애플리케이션에서 Claude API에 접근할 수 있도록 한다.
문서
전체 문서는 platform.claude.com/docs/en/api/sdks/python 에서 확인할 수 있다.
설치
pip install anthropic
시작하기
import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),  # This is the default and can be omitted
)

message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-opus-4-6",
)
print(message.content)
요구사항
Python 3.9+
기여하기
CONTRIBUTING.md 를 참조하라.
라이선스
이 프로젝트는 MIT License로 라이선스된다. 자세한 내용은 LICENSE 파일을 참조하라.
