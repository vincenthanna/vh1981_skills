---

Claude SDK for Python

The Claude SDK for Python provides access to the Claude API from Python applications.
Documentation
Full documentation is available at platform.claude.com/docs/en/api/sdks/python.
Installation
pip install anthropic
Getting started
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
Requirements
Python 3.9+
Contributing
See CONTRIBUTING.md.
License
This project is licensed under the MIT License. See the LICENSE file for details.
