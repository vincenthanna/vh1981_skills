#!/usr/bin/env node

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');
const fs = require('fs').promises;
const path = require('path');
const matter = require('gray-matter');

const PROMPTS_DIR = path.join(__dirname, 'prompts');

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

// 유틸리티: 모든 프롬프트 스캔
async function scanPrompts() {
  const results = [];

  async function scanDir(dir, repoName) {
    try {
      const files = await fs.readdir(dir, { withFileTypes: true });
      for (const file of files) {
        const fullPath = path.join(dir, file.name);
        if (file.isDirectory()) {
          await scanDir(fullPath, file.name);
        } else if (file.name.endsWith('.md')) {
          try {
            const content = await fs.readFile(fullPath, 'utf-8');
            const { data, content: body } = matter(content);
            const id = path.relative(PROMPTS_DIR, fullPath).replace(/\.md$/, '');
            results.push({
              id,
              title: data.title || 'Untitled',
              repo: data.repo || repoName || 'general',
              tags: data.tags || [],
              created_at: data.created_at || new Date().toISOString(),
              source: data.source || 'unknown',
              content: body
            });
          } catch (err) {
            // 파일 읽기 오류 무시
          }
        }
      }
    } catch (err) {
      // 디렉토리 읽기 오류 무시
    }
  }

  await scanDir(PROMPTS_DIR, 'general');
  return results;
}

// 프롬프트 저장
async function savePrompt(args) {
  const { title, repo, tags, content, source } = args;

  // repo 폴더 생성
  const repoDir = path.join(PROMPTS_DIR, repo || 'general');
  await fs.mkdir(repoDir, { recursive: true });

  // 파일명 생성
  const timestamp = Date.now();
  const slug = (title || 'untitled').toLowerCase().replace(/[^a-z0-9가-힣]+/g, '-').replace(/^-|-$/g, '') || 'untitled';
  const filename = `${timestamp}-${slug}.md`;
  const filePath = path.join(repoDir, filename);

  // frontmatter + content
  const frontmatter = matter.stringify(content || '', {
    title: title || 'Untitled',
    repo: repo || 'general',
    tags: tags || [],
    created_at: new Date().toISOString(),
    source: source || 'mcp-plugin'
  });

  await fs.writeFile(filePath, frontmatter);

  const id = path.join(repo || 'general', filename.replace('.md', ''));

  return {
    success: true,
    id,
    title,
    repo: repo || 'general',
    tags: tags || [],
    content: `프롬프트가 저장되었습니다.\n\nID: ${id}\n제목: ${title}\nRepo: ${repo || 'general'}`
  };
}

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
              description: '프롬프트 ID (예: general/1234567890-my-prompt)',
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
        const result = await savePrompt(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'list_prompts': {
        const prompts = await scanPrompts();
        let filtered = prompts;

        if (args?.repo) {
          filtered = filtered.filter(p => p.repo === args.repo);
        }
        if (args?.tag) {
          filtered = filtered.filter(p => p.tags.includes(args.tag));
        }

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(filtered, null, 2),
            },
          ],
        };
      }

      case 'get_prompt': {
        const filePath = path.join(PROMPTS_DIR, args.id + '.md');
        const content = await fs.readFile(filePath, 'utf-8');
        const { data, content: body } = matter(content);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                id: args.id,
                title: data.title,
                repo: data.repo,
                tags: data.tags,
                created_at: data.created_at,
                content: body
              }, null, 2),
            },
          ],
        };
      }

      case 'search_prompts': {
        const prompts = await scanPrompts();
        const query = args?.query?.toLowerCase() || '';
        const results = prompts.filter(p =>
          p.title.toLowerCase().includes(query) ||
          p.content.toLowerCase().includes(query) ||
          p.tags.some(t => t.toLowerCase().includes(query))
        );

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(results, null, 2),
            },
          ],
        };
      }

      case 'get_repos': {
        const prompts = await scanPrompts();
        const repos = [...new Set(prompts.map(p => p.repo))];

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(repos, null, 2),
            },
          ],
        };
      }

      case 'get_tags': {
        const prompts = await scanPrompts();
        const tags = new Set();
        prompts.forEach(p => p.tags.forEach(t => tags.add(t)));

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(Array.from(tags), null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            error: error.message
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
});

// 서버 시작
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Prompts Storage MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
