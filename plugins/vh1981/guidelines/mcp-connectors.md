# MCP 커넥터 연결 실패 대응

claude.ai 커넥터(`mcp__claude_ai_*`)가 끊겼을 때 다시 연결하는 절차다.
재연결이 404로 실패해도 같은 서비스의 독립 MCP 서버를 OAuth로 인증하면 쓸 수 있다.
"사용할 수 없다"고 끝내거나 같은 재연결을 반복하지 말고, 이 경로를 바로 제안한다.

## 증상

- 도구 호출이 `MCP server "claude.ai Notion" is not connected` 로 실패한다.
- `/mcp` 재연결이나 claude.ai 웹의 connect 버튼이 `HTTP 404 ... not_found_error "Server not found"` 를 돌려준다.

Claude 로그인 계정을 바꾼 직후에 이렇게 된 사례가 있다. 같은 상황에서 Slack은 `/mcp` 재연결만으로 돌아왔고, Notion은 돌아오지 않았다.
새 계정에 커넥터가 등록되지 않아서라는 원인은 추측이며 확인하지 않았다.

## Notion 우회 절차

1. 독립 Notion MCP 서버(`https://mcp.notion.com`)의 인증 도구를 찾는다. 서버 이름은 머신마다 다르다(`notion`, `notion-ds` 등).

   ```
   ToolSearch: "notion authenticate"
   ```

2. `mcp__<서버>__authenticate` 를 인자 없이 호출한다. 인증 URL이 돌아온다.
3. 사용자에게 URL을 주고, 회사 Notion 워크스페이스 계정으로 승인하게 한다.
4. 브라우저가 `http://localhost:<port>/callback?code=...&state=...` 로 이동하면서 연결 오류를 보인다. 원격 세션에서는 정상이다.
   사용자에게 주소창의 전체 URL을 복사해 대화에 붙여 달라고 한다.
5. `mcp__<서버>__complete_authentication` 을 그 URL을 `callback_url` 로 넘겨 호출한다.
6. 도구는 `mcp__<서버>__notion-*` 이름으로 나타난다. `mcp__claude_ai_Notion__*` 와 이름이 다르므로 ToolSearch로 스키마를 불러온다.

   ```
   ToolSearch: "+notion search"
   ToolSearch: "select:mcp__<서버>__notion-fetch"
   ```

   `notion-search` 의 `filters.created_date_range` 는 claude.ai 쪽과 똑같이 동작한다.

## 이것도 실패하면

남은 방법은 두 가지다. 사용자에게 둘 중 하나를 고르게 한다.

- claude.ai 설정의 Connectors에서 현재 계정에 Notion 커넥터를 추가한다.
- 커넥터가 동작하던 계정으로 다시 로그인한다.

Slack처럼 독립 MCP 서버가 따로 설치된 다른 서비스도 같은 순서로 시도할 수 있다. 다만 실제로 확인한 것은 Notion뿐이다(미검증).
