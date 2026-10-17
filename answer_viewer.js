(function(root){
  let dialog,code='',markdown='',mode='code',requestId=0,returnFocus;
  function ensureDialog(){
    if(dialog)return;
    dialog=document.createElement('dialog');dialog.className='reference-dialog';
    dialog.setAttribute('aria-labelledby','referenceTitle');
    dialog.innerHTML='<div class="reference-head"><h2 id="referenceTitle">参考答案</h2><button type="button" data-action="close" aria-label="关闭参考答案">关闭</button></div><div class="reference-tools"><div role="group" aria-label="答案视图"><button type="button" data-mode="code">完整答案代码</button><button type="button" data-mode="full">完整答案与说明</button></div><button type="button" data-action="copy">复制代码</button><span role="status" id="referenceStatus"></span></div><div class="reference-body"><pre id="referenceText"></pre></div>';
    document.body.append(dialog);
    dialog.querySelector('[data-action="close"]').onclick=close;
    dialog.querySelector('[data-action="copy"]').onclick=copy;
    dialog.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;render()});
    dialog.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();close()}});
    dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)close()}});
    dialog.addEventListener('cancel',e=>{e.preventDefault();close()});
    dialog.addEventListener('close',()=>{if(!dialog.open&&returnFocus?.isConnected)returnFocus.focus()});
  }
  function render(){
    dialog.querySelectorAll('[data-mode]').forEach(b=>{const active=b.dataset.mode===mode;b.classList.toggle('selected',active);b.setAttribute('aria-pressed',String(active))});
    dialog.querySelector('[data-mode="code"]').disabled=!code;
    dialog.querySelector('[data-action="copy"]').textContent=mode==='code'?'复制代码':'复制完整答案';
    dialog.querySelector('[data-action="copy"]').disabled=!(mode==='code'?code:markdown);
    dialog.querySelector('#referenceText').textContent=mode==='code'?code:markdown;
  }
  async function open(qid,label){
    ensureDialog();returnFocus=document.activeElement;const id=++requestId;
    code='';markdown='';mode='code';render();
    dialog.querySelector('#referenceTitle').textContent=label||qid+' 参考答案';
    dialog.querySelector('#referenceStatus').textContent='';
    dialog.querySelector('#referenceText').textContent='正在读取参考答案...';
    if(!dialog.open)dialog.showModal();
    try{
      const r=await fetch('/api/answer?qid='+encodeURIComponent(qid),{cache:'no-store'}),d=await r.json();
      if(!r.ok)throw new Error(d.message||'HTTP '+r.status);
      if(id!==requestId)return;
      code=d.code||'';markdown=d.markdown||'';mode=code?'code':'full';render();
      if(!code)dialog.querySelector('#referenceStatus').textContent='本题为文档或方案题，参考答案以文字形式提供。';
    }catch(e){if(id===requestId)dialog.querySelector('#referenceText').textContent='参考答案读取失败：'+e.message}
  }
  function close(){if(dialog?.open){requestId++;dialog.close()}}
  async function copy(){
    try{await navigator.clipboard.writeText(mode==='code'?code:markdown);dialog.querySelector('#referenceStatus').textContent='已复制'}
    catch(_){dialog.querySelector('#referenceStatus').textContent='复制失败，请在答案中选择需要的内容。'}
  }
  root.AnswerViewer={open,close};
})(window);
