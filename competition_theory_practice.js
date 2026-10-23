(function theoryPlugin() {
  'use strict';

  const bank = window.COMPETITION_THEORY_BANK;
  if (!bank || !Array.isArray(bank.questions)) {
    console.error('理论题库数据未加载');
    return;
  }

  const STORAGE_KEY = 'ai_trainer_competition_theory_v1';
  const TYPE_LABEL = { single: '单选题', multi: '多选题', fill: '填空题' };
  const TYPE_ORDER = ['all', 'single', 'multi', 'fill', 'wrong'];
  let filter = 'all';
  let keyword = '';
  let currentId = '';

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function normalizeFill(value) {
    return String(value == null ? '' : value)
      .trim().toLowerCase().replace(/\s+/g, '')
      .replace(/[，。；;！!？?]/g, '');
  }

  function loadState() {
    try {
      const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      if (value && typeof value === 'object') return value;
    } catch (_) {}
    return {};
  }

  function saveState(state) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  function recordFor(id) {
    return loadState()[id] || null;
  }

  function filteredQuestions() {
    const state = loadState();
    const term = keyword.trim().toLowerCase();
    return bank.questions.filter(q => {
      if (filter === 'wrong') {
        const r = state[q.id];
        if (!r || r.lastCorrect !== false) return false;
      } else if (filter !== 'all' && q.type !== filter) {
        return false;
      }
      if (!term) return true;
      const haystack = [q.stem].concat((q.options || []).map(x => x.text)).join(' ').toLowerCase();
      return haystack.includes(term);
    });
  }

  function firstPreferred(list) {
    if (!list.length) return null;
    if (currentId) {
      const existing = list.find(q => q.id === currentId);
      if (existing) return existing;
    }
    const state = loadState();
    return list.find(q => !state[q.id]) || list[0];
  }

  function currentQuestion() {
    const list = filteredQuestions();
    const q = firstPreferred(list);
    if (q) currentId = q.id;
    return { list, q };
  }

  function displayAnswer(q) {
    if (q.type === 'fill') return q.accepted.join(' / ');
    return q.answer.split('').map(letter => {
      const option = (q.options || []).find(x => x.key === letter);
      return option ? `${letter}. ${option.text}` : letter;
    }).join('；');
  }

  function stats() {
    const state = loadState();
    let answered = 0, correct = 0, wrong = 0;
    bank.questions.forEach(q => {
      const r = state[q.id];
      if (!r) return;
      answered += 1;
      if (r.lastCorrect) correct += 1;
      else wrong += 1;
    });
    return {
      answered,
      correct,
      wrong,
      rate: answered ? Math.round(correct * 100 / answered) : 0,
    };
  }

  function savedSelection(q, record) {
    if (!record) return q.type === 'multi' ? [] : '';
    if (q.type === 'multi') return Array.isArray(record.user) ? record.user : [];
    return record.user == null ? '' : record.user;
  }

  function optionHtml(q, record) {
    const saved = savedSelection(q, record);
    const inputType = q.type === 'multi' ? 'checkbox' : 'radio';
    return (q.options || []).map(opt => {
      const checked = q.type === 'multi' ? saved.includes(opt.key) : saved === opt.key;
      return `<label class="theory-option"><input type="${inputType}" name="theoryAnswer" value="${esc(opt.key)}" ${checked ? 'checked' : ''}><span><b>${esc(opt.key)}.</b> ${esc(opt.text).replace(/\n/g, '<br>')}</span></label>`;
    }).join('');
  }

  function questionHtml(q, list, record) {
    const pos = Math.max(0, list.findIndex(x => x.id === q.id)) + 1;
    const feedback = record
      ? `<div class="theory-feedback ${record.lastCorrect ? 'ok' : 'bad'}"><b>${record.lastCorrect ? '回答正确' : '回答错误'}</b>${record.lastCorrect ? '' : `<br>正确答案：${esc(displayAnswer(q))}`}</div>`
      : '';
    const body = q.type === 'fill'
      ? `<input id="theoryFillInput" class="theory-fill" autocomplete="off" placeholder="输入答案" value="${esc(savedSelection(q, record))}">`
      : `<div class="theory-options">${optionHtml(q, record)}</div>`;

    return `
      <div class="theory-card">
        <div class="theory-card-head">
          <div><span class="theory-badge">${esc(TYPE_LABEL[q.type])}</span> <b>第 ${q.number} 题</b></div>
          <div class="theory-position">当前筛选第 ${pos} / ${list.length} 题</div>
        </div>
        <div class="theory-stem">${esc(q.stem)}</div>
        ${body}
        ${feedback}
        <div class="theory-actions">
          <button class="btn" data-theory-action="prev">上一题</button>
          <button class="btn primary" data-theory-action="check">检查答案</button>
          <button class="btn" data-theory-action="next">下一题</button>
          <button class="btn" data-theory-action="random">随机一题</button>
          <button class="btn warn" data-theory-action="clear">清除本题记录</button>
        </div>
      </div>`;
  }

  function render() {
    const area = document.getElementById('theoryArea');
    if (!area) return;
    const { list, q } = currentQuestion();
    const s = stats();
    const labels = {
      all: `全部 ${bank.counts.total}`,
      single: `单选 ${bank.counts.single}`,
      multi: `多选 ${bank.counts.multi}`,
      fill: `填空 ${bank.counts.fill}`,
      wrong: `错题 ${s.wrong}`,
    };

    area.innerHTML = `
      <div class="theory-shell">
        <div class="theory-hero">
          <h2>理论题库练习</h2>
          <div class="muted">共 ${bank.counts.total} 题，答题后即时判定；进度保存在当前浏览器本地。</div>
          <div class="theory-summary">
            <span>单选 ${bank.counts.single}</span>
            <span>多选 ${bank.counts.multi}</span>
            <span>填空 ${bank.counts.fill}</span>
          </div>
        </div>
        <div class="theory-controls">
          <div class="theory-filter-row">
            ${TYPE_ORDER.map(key => `<button class="theory-filter ${filter === key ? 'active' : ''}" data-theory-filter="${key}">${labels[key]}</button>`).join('')}
          </div>
          <input id="theorySearch" class="theory-search" placeholder="搜索题目或选项" value="${esc(keyword)}">
        </div>
        <div class="theory-stats">
          <div class="theory-stat"><b>${s.answered}</b>已作答</div>
          <div class="theory-stat"><b>${s.correct}</b>当前答对</div>
          <div class="theory-stat"><b>${s.rate}%</b>正确率</div>
          <div class="theory-stat"><b>${s.wrong}</b>错题</div>
        </div>
        ${q ? questionHtml(q, list, recordFor(q.id)) : '<div class="theory-empty">当前筛选条件下没有题目。</div>'}
        <div class="theory-actions">
          <button class="btn warn" data-theory-action="reset-all">重置全部理论练习进度</button>
        </div>
      </div>`;

    bind(area);
  }

  function checkedAnswer(q, area) {
    if (q.type === 'fill') {
      return (area.querySelector('#theoryFillInput') || {}).value || '';
    }
    const values = Array.from(area.querySelectorAll('input[name="theoryAnswer"]:checked')).map(x => x.value);
    return q.type === 'multi' ? values.sort() : (values[0] || '');
  }

  function isCorrect(q, user) {
    if (q.type === 'fill') {
      const value = normalizeFill(user);
      return q.accepted.some(x => normalizeFill(x) === value);
    }
    if (q.type === 'multi') return user.join('') === q.answer;
    return user === q.answer;
  }

  function move(delta) {
    const list = filteredQuestions();
    if (!list.length) return;
    let index = list.findIndex(q => q.id === currentId);
    if (index < 0) index = 0;
    index = (index + delta + list.length) % list.length;
    currentId = list[index].id;
    render();
  }

  function randomQuestion() {
    const list = filteredQuestions();
    if (!list.length) return;
    const candidates = list.length > 1 ? list.filter(q => q.id !== currentId) : list;
    currentId = candidates[Math.floor(Math.random() * candidates.length)].id;
    render();
  }

  function checkAnswer() {
    const area = document.getElementById('theoryArea');
    const { q } = currentQuestion();
    if (!q || !area) return;
    const user = checkedAnswer(q, area);
    if ((q.type === 'multi' && !user.length) || (q.type !== 'multi' && !String(user).trim())) {
      alert('请先作答。');
      return;
    }
    const ok = isCorrect(q, user);
    const state = loadState();
    const old = state[q.id] || { attempts: 0, correctAttempts: 0 };
    state[q.id] = {
      user,
      attempts: Number(old.attempts || 0) + 1,
      correctAttempts: Number(old.correctAttempts || 0) + (ok ? 1 : 0),
      lastCorrect: ok,
      updatedAt: Date.now(),
    };
    saveState(state);
    render();
  }

  function clearCurrent() {
    const { q } = currentQuestion();
    if (!q) return;
    const state = loadState();
    delete state[q.id];
    saveState(state);
    render();
  }

  function bind(area) {
    area.querySelectorAll('[data-theory-filter]').forEach(btn => {
      btn.addEventListener('click', () => {
        filter = btn.dataset.theoryFilter || 'all';
        currentId = '';
        render();
      });
    });
    const search = area.querySelector('#theorySearch');
    if (search) {
      search.addEventListener('input', () => {
        keyword = search.value || '';
        currentId = '';
        render();
        const next = document.getElementById('theorySearch');
        if (next) {
          next.focus();
          next.setSelectionRange(next.value.length, next.value.length);
        }
      });
    }
    area.querySelectorAll('[data-theory-action]').forEach(btn => {
      btn.addEventListener('click', () => {
        const action = btn.dataset.theoryAction;
        if (action === 'prev') move(-1);
        else if (action === 'next') move(1);
        else if (action === 'random') randomQuestion();
        else if (action === 'check') checkAnswer();
        else if (action === 'clear') clearCurrent();
        else if (action === 'reset-all') {
          if (confirm('确定清除全部理论题练习记录吗？')) {
            localStorage.removeItem(STORAGE_KEY);
            currentId = '';
            render();
          }
        }
      });
    });
    const fill = area.querySelector('#theoryFillInput');
    if (fill) fill.addEventListener('keydown', e => {
      if (e.key === 'Enter') checkAnswer();
    });
  }

  function install() {
    const tabs = document.querySelector('.tabs');
    const guideArea = document.getElementById('guideArea');
    if (!tabs || !guideArea || document.getElementById('theoryArea')) return;

    const button = document.createElement('button');
    button.className = 'tab';
    button.dataset.mode = 'theory';
    button.textContent = '理论题库';
    button.addEventListener('click', () => window.setMode('theory'));
    tabs.appendChild(button);

    const area = document.createElement('div');
    area.id = 'theoryArea';
    area.className = 'hidden';
    guideArea.insertAdjacentElement('afterend', area);

    const originalSetMode = window.setMode;
    window.setMode = function (name) {
      const layout = document.querySelector('.layout');
      const taskHead = document.getElementById('taskHead');
      const taskDescription = document.getElementById('taskDescription');
      if (name !== 'theory') {
        if (layout) layout.classList.remove('theory-mode');
        area.classList.add('hidden');
        if (taskHead) taskHead.classList.remove('hidden');
        originalSetMode(name);
        return;
      }

      document.querySelectorAll('.tab').forEach(x => x.classList.toggle('active', x.dataset.mode === 'theory'));
      ['examArea', 'fillArea', 'funcArea', 'guideArea'].forEach(id => document.getElementById(id)?.classList.add('hidden'));
      area.classList.remove('hidden');
      if (taskHead) taskHead.classList.add('hidden');
      if (taskDescription) taskDescription.classList.add('hidden');
      if (layout) layout.classList.add('theory-mode');
      render();
    };

    window.TheoryPractice = {
      render,
      reset: () => {
        localStorage.removeItem(STORAGE_KEY);
        currentId = '';
        render();
      },
    };
  }

  install();
})();
