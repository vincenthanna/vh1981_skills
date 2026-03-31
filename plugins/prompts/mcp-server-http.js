#!/usr/bin/env node

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');

// 웹 서버 API를 통해 데이터 저장/조회
const API_BASE = process.env.PROMPT_API_URL || 'http://localhost:3000/api';

async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    return await response.json();
  } catch (error) {
    return { error: error.message };
  }
}

// MCP 서버 생성
const server = new Server(
  {
    name: 'prompts-storage',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 도구 목록 등록
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'save_prompt',
        description: '프롬프트를 저장소에 저장합니다',
        inputSchema: {
          type: 'object',
          properties: {
            title: {
              type: 'string',
              description: '프롬프트 제목',
            },
            repo: {
              type: 'string',
              description: '프로젝트 repo 이름 (없으면 general)',
              default: 'general',
            },
            tags: {
              type: 'array',
              items: { type: 'string' },
              description: '태그 목록',
            },
            content: {
              type: 'string',
              description: '프롬프트 내용',
            },
          },
          required: ['title', 'content'],
        },
      },
      {
        name: 'list_prompts',
        description: '모든 프롬프트 목록을 조회합니다',
        inputSchema: {
          type: 'object',
          properties: {
            repo: {
              type: 'string',
              description: '특정 repo만 필터링 (선택)',
            },
            tag: {
              type: 'string',
              description: '특정 태그만 필터링 (선택)',
            },
          },
        },
      },
      {
        name: 'get_prompt',
        description: '특정 프롬프트를 조회합니다',
        inputSchema: {
          type: 'object',
          properties: {
            id: {
              type: 'string',
              description: '프롬프트 ID',
            },
          },
          required: ['id'],
        },
      },
      {
        name: 'search_prompts',
        description: '프롬프트를 검색합니다',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: '검색어 (제목, 내용, 태그에서 검색)',
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'get_repos',
        description: '모든 repo 목록을 조회합니다',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'get_tags',
        description: '모든 태그 목록을 조회합니다',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
    ],
  };
});

// 도구 실행 처리
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'save_prompt': {
        const result = await apiCall('/prompts', {
          method: 'POST',
          body: JSON.stringify(args)
        });
        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        };
      }

      case 'list_prompts': {
        const params = new URLSearchParams();
        if (args?.repo) params.append('repo', args.repo);
        if (args?.tag) params.append('tag', args.tag);
        const result = await apiCall(`/prompts?${params}`);
        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        };
      }

      case 'get_prompt': {
        const result = await apiCall(`/prompts/${args.id}`);
        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        };
      }

      case 'search_prompts': {
        const result = await apiCall(`/prompts?search=${encodeURIComponent(args.query)}`);
        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        };
      }

      case 'get_repos': {
        const result = await apiCall('/repos');
        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        };
      }

      case 'get_tags': {
        const result = await apiCall('/tags');
        return {
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{ type: 'text', text: JSON.stringify({ error: error.message }, null, 2) }],
      isError: true,
    };
  }
});

// 서버 시작
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`Prompts Storage MCP Server (HTTP mode) running on stdio`);
  console.error(`API endpoint: ${API_BASE}`);
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
