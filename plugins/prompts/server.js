require('dotenv').config();
const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const matter = require('gray-matter');

const app = express();
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';  // 외부 접속 허용
const PROMPTS_DIR = path.join(__dirname, 'prompts');
const API_KEY = process.env.API_KEY || 'your-secret-api-key';  // API 키

// 미들웨어
app.use(express.json());
app.use(express.static('web'));

// CORS 미들웨어
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key');
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
});

// API 키 인증 미들웨어 (외부 API용)
function requireApiKey(req, res, next) {
  const key = req.headers['x-api-key'];
  if (key === API_KEY) {
    next();
  } else {
    res.status(401).json({ error: 'Invalid or missing API key' });
  }
}

// 유틸리티: 모든 프롬프트 파일 스캔
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
            results.push({
              id: path.relative(PROMPTS_DIR, fullPath).replace(/\.md$/, ''),
              title: data.title || 'Untitled',
              repo: data.repo || repoName || 'general',
              tags: data.tags || [],
              created_at: data.created_at || new Date().toISOString(),
              source: data.source || 'unknown',
              content: body
            });
          } catch (err) {
            console.error(`Error reading ${fullPath}:`, err.message);
          }
        }
      }
    } catch (err) {
      console.error(`Error scanning ${dir}:`, err.message);
    }
  }

  await scanDir(PROMPTS_DIR, 'general');
  return results;
}

// API: 모든 프롬프트 조회
app.get('/api/prompts', async (req, res) => {
  try {
    const prompts = await scanPrompts();

    // 검색 필터
    const { search, repo, tag } = req.query;
    let filtered = prompts;

    if (search) {
      const searchLower = search.toLowerCase();
      filtered = filtered.filter(p =>
        p.title.toLowerCase().includes(searchLower) ||
        p.content.toLowerCase().includes(searchLower) ||
        p.tags.some(t => t.toLowerCase().includes(searchLower))
      );
    }

    if (repo) {
      filtered = filtered.filter(p => p.repo === repo);
    }

    if (tag) {
      filtered = filtered.filter(p => p.tags.includes(tag));
    }

    res.json(filtered);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: 개별 프롬프트 조회
app.get('/api/prompts/:id', async (req, res) => {
  try {
    const filePath = path.join(PROMPTS_DIR, req.params.id + '.md');
    const content = await fs.readFile(filePath, 'utf-8');
    const { data, content: body } = matter(content);

    res.json({
      id: req.params.id,
      title: data.title || 'Untitled',
      repo: data.repo || 'general',
      tags: data.tags || [],
      created_at: data.created_at || new Date().toISOString(),
      source: data.source || 'unknown',
      content: body
    });
  } catch (err) {
    res.status(404).json({ error: 'Prompt not found' });
  }
});

// API: 프롬프트 생성
app.post('/api/prompts', async (req, res) => {
  try {
    const { title, repo, tags, content, source } = req.body;

    // repo 폴더 생성 (없으면)
    const repoDir = path.join(PROMPTS_DIR, repo || 'general');
    await fs.mkdir(repoDir, { recursive: true });

    // 파일명 생성 (타임스탬프 + 슬러그)
    const timestamp = Date.now();
    const slug = title.toLowerCase().replace(/[^a-z0-9가-힣]+/g, '-').replace(/^-|-$/g, '') || 'untitled';
    const filename = `${timestamp}-${slug}.md`;
    const filePath = path.join(repoDir, filename);

    // frontmatter + content
    const frontmatter = matter.stringify(content || '', {
      title: title || 'Untitled',
      repo: repo || 'general',
      tags: tags || [],
      created_at: new Date().toISOString(),
      source: source || 'manual'
    });

    await fs.writeFile(filePath, frontmatter);

    res.json({
      id: path.join(repo || 'general', filename.replace('.md', '')),
      title,
      repo: repo || 'general',
      tags: tags || [],
      created_at: new Date().toISOString(),
      source: source || 'manual',
      content: content || ''
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: 프롬프트 수정
app.put('/api/prompts/:id', async (req, res) => {
  try {
    const filePath = path.join(PROMPTS_DIR, req.params.id + '.md');
    const { title, repo, tags, content } = req.body;

    const frontmatter = matter.stringify(content, {
      title,
      repo,
      tags,
      updated_at: new Date().toISOString()
    });

    await fs.writeFile(filePath, frontmatter);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: 프롬프트 삭제
app.delete('/api/prompts/:id', async (req, res) => {
  try {
    const filePath = path.join(PROMPTS_DIR, req.params.id + '.md');
    await fs.unlink(filePath);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: 프롬프트 결합
app.post('/api/prompts/combine', async (req, res) => {
  try {
    const { ids, newTitle, separator } = req.body;

    let combinedContent = [];
    let allTags = new Set();
    let repos = new Set();

    for (const id of ids) {
      const filePath = path.join(PROMPTS_DIR, id + '.md');
      const content = await fs.readFile(filePath, 'utf-8');
      const { data, content: body } = matter(content);

      combinedContent.push(`## ${data.title || 'Untitled'}\n\n${body}`);
      (data.tags || []).forEach(t => allTags.add(t));
      if (data.repo) repos.add(data.repo);
    }

    const finalContent = combinedContent.join(separator || '\n\n---\n\n');

    res.json({
      title: newTitle || 'Combined Prompt',
      content: finalContent,
      tags: Array.from(allTags),
      repos: Array.from(repos)
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: 템플릿 변수 치환
app.post('/api/prompts/template', async (req, res) => {
  try {
    const { id, variables } = req.body;
    const filePath = path.join(PROMPTS_DIR, id + '.md');
    const content = await fs.readFile(filePath, 'utf-8');
    const { data, content: body } = matter(content);

    let processed = body;
    for (const [key, value] of Object.entries(variables || {})) {
      processed = processed.replace(new RegExp(`{{${key}}}`, 'g'), value);
    }

    res.json({
      title: data.title,
      content: processed
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: 모든 repo 목록
app.get('/api/repos', async (req, res) => {
  try {
    const prompts = await scanPrompts();
    const repos = [...new Set(prompts.map(p => p.repo))];
    res.json(repos);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// API: 모든 태그 목록
app.get('/api/tags', async (req, res) => {
  try {
    const prompts = await scanPrompts();
    const tags = new Set();
    prompts.forEach(p => p.tags.forEach(t => tags.add(t)));
    res.json(Array.from(tags));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 서버 시작
app.listen(PORT, HOST, () => {
  console.log(`Prompt Storage Server running at http://${HOST}:${PORT}`);
  console.log(`Local: http://localhost:${PORT}`);
  console.log(`External API: POST http://<your-ip>:${PORT}/external/prompts`);
  console.log(`API Key: ${API_KEY}`);
});

// ===== 외부 API 엔드포인트 (API 키 필요) =====

// 외부 API: 프롬프트 저장 (다른 머신에서 호출 가능)
app.post('/external/prompts', requireApiKey, async (req, res) => {
  try {
    const { title, repo, tags, content, source, hostname } = req.body;

    // repo 폴더 생성 (없으면)
    const repoDir = path.join(PROMPTS_DIR, repo || 'general');
    await fs.mkdir(repoDir, { recursive: true });

    // 파일명 생성 (타임스탬프 + 슬러그)
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
      source: source || 'external',
      hostname: hostname || 'unknown'
    });

    await fs.writeFile(filePath, frontmatter);

    res.json({
      success: true,
      id: path.join(repo || 'general', filename.replace('.md', '')),
      title,
      repo: repo || 'general',
      tags: tags || [],
      created_at: new Date().toISOString(),
      source: source || 'external'
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 외부 API: 대화 내용 일괄 저장
app.post('/external/conversation', requireApiKey, async (req, res) => {
  try {
    const { repo, tags, messages, title } = req.body;

    if (!Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({ error: 'messages array is required' });
    }

    // repo 폴더 생성
    const repoDir = path.join(PROMPTS_DIR, repo || 'general');
    await fs.mkdir(repoDir, { recursive: true });

    // 각 메시지를 개별 프롬프트로 저장
    const results = [];
    for (const msg of messages) {
      const timestamp = Date.now() + Math.random();
      const slug = (msg.title || title || 'conversation').toLowerCase().replace(/[^a-z0-9가-힣]+/g, '-').replace(/^-|-$/g, '') || 'conversation';
      const filename = `${timestamp}-${slug}.md`;
      const filePath = path.join(repoDir, filename);

      const frontmatter = matter.stringify(msg.content || '', {
        title: msg.title || title || 'Conversation',
        repo: repo || 'general',
        tags: msg.tags || tags || [],
        created_at: msg.timestamp || new Date().toISOString(),
        source: 'external-conversation',
        role: msg.role || 'user'
      });

      await fs.writeFile(filePath, frontmatter);
      results.push({
        id: path.join(repo || 'general', filename.replace('.md', '')),
        title: msg.title || title
      });
    }

    res.json({
      success: true,
      saved: results.length,
      prompts: results
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 외부 API: 상태 확인
app.get('/external/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});
