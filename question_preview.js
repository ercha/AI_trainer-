(function(){
  const MOCK_BASE='人工智能训练师三级素材/人工智能训练师三级考试平台模拟界面/';
  const STATE_KEY='ai3_exam_question_preview_open';

  function isOpen(){
    try{
      const v=localStorage.getItem(STATE_KEY);
      return v===null?true:v!=='0';
    }catch(_){return true}
  }
  function saveOpen(open){try{localStorage.setItem(STATE_KEY,open?'1':'0')}catch(_){}}
  function getChildDoc(){try{return typeof childDoc==='function'?childDoc():null}catch(_){return null}}
  function getQid(){try{return typeof currentQid==='function'?currentQid():''}catch(_){return ''}}

  function previewUrl(qid){return MOCK_BASE+encodeURIComponent(qid)+'.html'}

  window.toggleQuestionPreview=function(){
    const d=getChildDoc();if(!d)return;
    const body=d.getElementById('examQuestionPreviewBody');
    const btn=d.getElementById('examQuestionPreviewToggle');
    if(!body)return;
    const open=body.style.display==='none';
    body.style.display=open?'block':'none';
    if(btn)btn.textContent=open?'收起题目':'展开题目';
    saveOpen(open);
  };

  window.openQuestionPreview=function(){
    const qid=getQid();if(qid)window.open(previewUrl(qid),'_blank');
  };

  function injectPreview(){
    const d=getChildDoc();if(!d)return;
    const state=d.getElementById('nbExamState');
    if(!state||d.getElementById('examQuestionPreview'))return;
    const qid=getQid();if(!qid)return;
    const open=isOpen();
    const box=d.createElement('div');
    box.id='examQuestionPreview';
    box.style.cssText='border:1px solid #dbe3ef;border-radius:9px;margin:14px 0;background:#fff;overflow:hidden;';
    box.innerHTML=`
      <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;background:#f8fafc;border-bottom:1px solid #e2e8f0">
        <div style="font-weight:700;flex:1">题目预览</div>
        <div style="font-size:12px;color:#64748b">${qid} · 原始考试题面</div>
        <button id="examQuestionPreviewToggle" class="btn small" onclick="parent.toggleQuestionPreview()">${open?'收起题目':'展开题目'}</button>
        <button class="btn small" onclick="parent.openQuestionPreview()">新窗口打开</button>
      </div>
      <div id="examQuestionPreviewBody" style="display:${open?'block':'none'};background:#fff">
        <iframe title="${qid} 题目预览" src="${previewUrl(qid)}" style="display:block;width:100%;height:min(56vh,620px);min-height:420px;border:0;background:#fff"></iframe>
      </div>`;
    state.parentNode.insertBefore(box,state);
  }

  const original=window.renderNotebookExam;
  if(typeof original==='function'){
    window.renderNotebookExam=function(){
      const r=original.apply(this,arguments);
      injectPreview();
      return r;
    };
  }

  // The inner training page may already be loaded before this script executes.
  setTimeout(()=>{
    try{
      const d=getChildDoc();
      const active=d&&d.querySelector('.tab.active');
      if(active&&active.dataset.mode==='exam'){
        if(typeof window.renderNotebookExam==='function')window.renderNotebookExam();
      }
    }catch(_){}
  },0);
})();
