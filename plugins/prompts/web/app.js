// API 기본 URL
const API = '/api';

// 전역 상태
let currentPrompt = null;
let allPrompts = [];

// DOM 요소
const promptList = document.getElementById('promptList');
const searchInput = document.getElementById('searchInput');
const repoFilter = document.getElementById('repoFilter');
const tagFilter = document.getElementById('tagFilter');
const addBtn = document.getElementById('addBtn');

// 모달 요소
const promptModal = document.getElementById('promptModal');
const viewModal = document.getElementById('viewModal');
const combineModal = document.getElementById('combineModal');
const templateModal = document.getElementById('templateModal');

// 초기화
async function init() {
  await loadFilters();
  await loadPrompts();
  setupEventListeners();
}

// 필터 로드
async function loadFilters() {
  try {
    const [repos, tags] = await Promise.all([
      fetch(`${API}/repos`).then(r => r.json()),
      fetch(`${API}/tags`).then(r => r.json())
    ]);

    repos.forEach(repo => {
      const option = document.createElement('option');
      option.value = repo;
      option.textContent = repo;
      repoFilter.appendChild(option);
    });

    tags.forEach(tag => {
      const option = document.createElement('option');
      option.value = tag;
      option.textContent = tag;
      tagFilter.appendChild(option);
    });
  } catch (err) {
    console.error('Failed to load filters:', err);
  }
}

// 프롬프트 로드
async function loadPrompts() {
  try {
    const params = new URLSearchParams();
    if (searchInput.value) params.append('search', searchInput.value);
    if (repoFilter.value) params.append('repo', repoFilter.value);
    if (tagFilter.value) params.append('tag', tagFilter.value);

    const response = await fetch(`${API}/prompts?${params}`);
    allPrompts = await response.json();
    renderPrompts(allPrompts);
  } catch (err) {
    console.error('Failed to load prompts:', err);
    promptList.innerHTML = '<div class="empty-state">프롬프트를 불러오는데 실패했습니다.</div>';
  }
}

// 프롬프트 렌더링
function renderPrompts(prompts) {
  if (prompts.length === 0) {
    promptList.innerHTML = `
      <div class="empty-state">
        <p>프롬프트가 없습니다.</p>
        <p>+ 새 프롬프트 버튼을 클릭하여 추가하세요.</p>
      </div>
    `;
    return;
  }

  promptList.innerHTML = prompts.map(prompt => `
    <div class="prompt-card" data-id="${prompt.id}">
      <div class="prompt-card-header">
        <div class="prompt-card-title">${escapeHtml(prompt.title)}</div>
      </div>
      <div class="prompt-card-meta">
        <span class="prompt-card-repo">${escapeHtml(prompt.repo)}</span>
        <span>${formatDate(prompt.created_at)}</span>
      </div>
      <div class="prompt-card-tags">
        ${prompt.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
      </div>
      <div class="prompt-card-preview">${escapeHtml(prompt.content.substring(0, 200))}${prompt.content.length > 200 ? '...' : ''}</div>
    </div>
  `).join('');

  // 클릭 이벤트
  promptList.querySelectorAll('.prompt-card').forEach(card => {
    card.addEventListener('click', () => viewPrompt(card.dataset.id));
  });
}

// 프롬프트 보기
async function viewPrompt(id) {
  try {
    const response = await fetch(`${API}/prompts/${encodeURIComponent(id)}`);
    currentPrompt = await response.json();

    document.getElementById('viewTitle').textContent = currentPrompt.title;
    document.getElementById('viewMeta').innerHTML = `
      <strong>Repo:</strong> ${escapeHtml(currentPrompt.repo)}
      ${currentPrompt.tags.length ? `<br><strong>Tags:</strong> ${currentPrompt.tags.map(t => escapeHtml(t)).join(', ')}` : ''}
      <br><strong>Created:</strong> ${formatDate(currentPrompt.created_at)}
    `;
    document.getElementById('viewContent').textContent = currentPrompt.content;

    showModal(viewModal);
  } catch (err) {
    console.error('Failed to load prompt:', err);
    alert('프롬프트를 불러오는데 실패했습니다.');
  }
}

// 프롬프트 저장
async function savePrompt(e) {
  e.preventDefault();

  const data = {
    title: document.getElementById('promptTitle').value,
    repo: document.getElementById('promptRepo').value || 'general',
    tags: document.getElementById('promptTags').value.split(',').map(t => t.trim()).filter(t => t),
    content: document.getElementById('promptContent').value
  };

  try {
    const response = await fetch(`${API}/prompts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      hideModal(promptModal);
      document.getElementById('promptForm').reset();
      await loadPrompts();
    } else {
      alert('저장에 실패했습니다.');
    }
  } catch (err) {
    console.error('Failed to save prompt:', err);
    alert('저장에 실패했습니다.');
  }
}

// 프롬프트 삭제
async function deletePrompt() {
  if (!confirm('정말 삭제하시겠습니까?')) return;

  try {
    const response = await fetch(`${API}/prompts/${encodeURIComponent(currentPrompt.id)}`, {
      method: 'DELETE'
    });

    if (response.ok) {
      hideModal(viewModal);
      await loadPrompts();
    }
  } catch (err) {
    console.error('Failed to delete prompt:', err);
    alert('삭제에 실패했습니다.');
  }
}

// 프롬프트 결합
async function combinePrompts() {
  const selectedIds = Array.from(combineModal.querySelectorAll('.combine-item input:checked'))
    .map(cb => cb.dataset.id);

  if (selectedIds.length < 2) {
    alert('2개 이상의 프롬프트를 선택해주세요.');
    return;
  }

  try {
    const response = await fetch(`${API}/prompts/combine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ids: selectedIds,
        newTitle: document.getElementById('combineTitle').value,
        separator: document.getElementById('combineSeparator').value
      })
    });

    const result = await response.json();

    // 결과로 새 프롬프트 생성
    const saveResponse = await fetch(`${API}/prompts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: result.title,
        repo: result.repos[0] || 'general',
        tags: result.tags,
        content: result.content
      })
    });

    if (saveResponse.ok) {
      hideModal(combineModal);
      await loadPrompts();
      alert('프롬프트가 결합되어 저장되었습니다.');
    }
  } catch (err) {
    console.error('Failed to combine prompts:', err);
    alert('결합에 실패했습니다.');
  }
}

// 템플릿 변수 치환
async function applyTemplate() {
  const inputs = templateModal.querySelectorAll('.template-variable input');
  const variables = {};

  inputs.forEach(input => {
    variables[input.dataset.variable] = input.value;
  });

  try {
    const response = await fetch(`${API}/prompts/template`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: currentPrompt.id,
        variables
      })
    });

    const result = await response.json();

    // 결과 보기
    document.getElementById('viewTitle').textContent = result.title + ' (변환됨)';
    document.getElementById('viewContent').textContent = result.content;
    hideModal(templateModal);
  } catch (err) {
    console.error('Failed to apply template:', err);
    alert('템플릿 적용에 실패했습니다.');
  }
}

// 결합 모달 열기
function openCombineModal() {
  const list = document.getElementById('combineList');
  list.innerHTML = allPrompts.map(p => `
    <label class="combine-item">
      <input type="checkbox" data-id="${p.id}" ${p.id === currentPrompt.id ? 'checked' : ''}>
      <span class="combine-item-label">${escapeHtml(p.title)} (${escapeHtml(p.repo)})</span>
    </label>
  `).join('');

  document.getElementById('combineTitle').value = '결합된 프롬프트';
  showModal(combineModal);
}

// 템플릿 모달 열기
function openTemplateModal() {
  // 템플릿 변수 추출
  const variables = currentPrompt.content.match(/{{(\w+)}}/g) || [];
  const uniqueVars = [...new Set(variables.map(v => v.replace(/[{}]/g, '')))];

  if (uniqueVars.length === 0) {
    alert('템플릿 변수({{variable}})가 없습니다.');
    return;
  }

  const container = document.getElementById('templateVariables');
  container.innerHTML = uniqueVars.map(v => `
    <div class="template-variable">
      <label>${escapeHtml(v)}</label>
      <input type="text" data-variable="${v}" placeholder="${escapeHtml(v)}의 값">
    </div>
  `).join('');

  showModal(templateModal);
}

// 모달 관련
function showModal(modal) {
  modal.classList.add('show');
}

function hideModal(modal) {
  modal.classList.remove('show');
}

// 이벤트 리스너 설정
function setupEventListeners() {
  // 검색
  searchInput.addEventListener('input', debounce(loadPrompts, 300));
  repoFilter.addEventListener('change', loadPrompts);
  tagFilter.addEventListener('change', loadPrompts);

  // 추가 버튼
  addBtn.addEventListener('click', () => {
    document.getElementById('modalTitle').textContent = '새 프롬프트';
    document.getElementById('promptForm').reset();
    document.getElementById('promptRepo').value = 'general';
    showModal(promptModal);
  });

  // 프롬프트 폼
  document.getElementById('promptForm').addEventListener('submit', savePrompt);

  // 모달 닫기
  document.querySelectorAll('.close, .cancel').forEach(btn => {
    btn.addEventListener('click', function() {
      hideModal(this.closest('.modal'));
    });
  });

  // 모달 외부 클릭 시 닫기
  document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) hideModal(modal);
    });
  });

  // 보기 모달 액션
  document.getElementById('deleteBtn').addEventListener('click', deletePrompt);
  document.getElementById('copyBtn').addEventListener('click', () => {
    navigator.clipboard.writeText(currentPrompt.content);
    alert('클립보드에 복사되었습니다.');
  });
  document.getElementById('combineBtn').addEventListener('click', openCombineModal);
  document.getElementById('templateBtn').addEventListener('click', openTemplateModal);
  document.getElementById('editBtn').addEventListener('click', () => {
    hideModal(viewModal);
    document.getElementById('modalTitle').textContent = '프롬프트 편집';
    document.getElementById('promptTitle').value = currentPrompt.title;
    document.getElementById('promptRepo').value = currentPrompt.repo;
    document.getElementById('promptTags').value = currentPrompt.tags.join(', ');
    document.getElementById('promptContent').value = currentPrompt.content;
    showModal(promptModal);
  });

  // 결합
  document.getElementById('doCombineBtn').addEventListener('click', combinePrompts);

  // 템플릿
  document.getElementById('doTemplateBtn').addEventListener('click', applyTemplate);
}

// 유틸리티
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString('ko-KR');
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// 시작
init();
