"use strict";
(function(){
  const source=window.BEGINNER_COURSE;
  const modules=source&&source.modules||[];
  const lessons=modules.flatMap(m=>m.steps.map(s=>Object.assign({moduleId:m.id,moduleName:m.name},s)));
  const storageKey="ai_trainer_beginner_course_v1";
  let completed={};
  try{completed=JSON.parse(localStorage.getItem(storageKey)||"{}")||{}}catch(_){completed={}}
  let current=(location.hash||"").replace(/^#/,"");
  if(!lessons.some(l=>l.id===current)){current=(lessons.find(l=>!completed[l.id])||lessons[0]||{}).id}
  const $=id=>document.getElementById(id);
  const esc=value=>String(value??"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
  const countDone=ids=>ids.filter(id=>completed[id]).length;
  function persist(){try{localStorage.setItem(storageKey,JSON.stringify(completed))}catch(_){$("feedback").textContent="浏览器禁止保存进度，本次结果仅临时有效。"}}
  function openLesson(id){if(!lessons.some(l=>l.id===id))return;current=id;history.replaceState(null,"","#"+encodeURIComponent(id));render()}
  function renderNav(){
    const done=countDone(lessons.map(l=>l.id));
    $("overall").innerHTML='<b>'+done+' / '+lessons.length+' 节已通过自测</b><div class="progress"><span style="width:'+(lessons.length?Math.round(100*done/lessons.length):0)+'%"></span></div><div class="muted">按照 A → B → C → D → E 学习；可随时切换</div>';
    const only=$("unfinished").checked;
    const nav=$("nav");nav.innerHTML="";
    for(const m of modules){
      const ids=m.steps.map(s=>s.id),n=countDone(ids);
      const box=document.createElement("div");box.className="mod";
      const heading=document.createElement("button");heading.type="button";heading.className="mod-head";
      heading.innerHTML='<span>'+esc(m.id)+' · '+esc(m.name)+'</span><span>'+n+'/'+ids.length+'</span>';
      const body=document.createElement("div");body.className="lessons";
      for(const s of m.steps){
        if(only&&completed[s.id]&&s.id!==current)continue;
        const btn=document.createElement("button");btn.type="button";
        btn.className="lesson-button"+(current===s.id?" active":"");
        btn.innerHTML='<span class="index">'+esc(s.id)+'</span> '+esc(s.title)+(completed[s.id]?' <span class="done">✓</span>':'');
        btn.addEventListener("click",()=>openLesson(s.id));body.appendChild(btn);
      }
      heading.addEventListener("click",()=>{body.hidden=!body.hidden});
      box.append(heading,body);nav.appendChild(box);
    }
  }
  function render(){
    const l=lessons.find(x=>x.id===current);if(!l)return;
    const mod=modules.find(m=>m.id===l.moduleId);
    $("courseTitle").textContent=l.id+" · "+l.title;
    $("moduleIntro").textContent="模块 "+mod.id+"："+mod.name+"。"+mod.intro;
    const area=$("lessonContent");area.innerHTML=
      '<span class="tag">模块 '+esc(l.moduleId)+' · 基础课</span> <span class="muted">建议约 '+l.minutes+' 分钟</span>'+
      '<h3>一、先理解概念</h3><p>'+esc(l.concept)+'</p>'+
      '<h3>二、照着代码运行</h3><p class="muted">可在 Jupyter 新建 Python Notebook，或者打开本模块配套入门 Notebook。网页仅展示代码，不会在浏览器内直接运行 Python。</p>'+
      '<pre><code id="exampleCode"></code></pre><div class="actions"><button id="copyExample" type="button">复制示例代码</button>'+
      '<a class="action" download href="beginner_notebooks/'+esc(l.moduleId)+'.ipynb">下载 '+esc(l.moduleId)+' 模块入门 Notebook</a></div>'+
      '<h3>三、逐句理解</h3><ol>'+l.steps.map(x=>'<li>'+esc(x)+'</li>').join("")+'</ol>'+
      '<section class="section"><h3>四、自己动手</h3><p>'+esc(l.challenge)+'</p>'+
      '<button type="button" id="showHint">查看参考写法</button><div id="answer"><pre><code id="answerCode"></code></pre>'+
      '<p class="muted">请先独立尝试，再对照代码。练习是否实际运行成功，需要你在 Jupyter 中自行核验。</p></div></section>'+
      '<section class="section"><h3>五、概念自测</h3><p>'+esc(l.quiz.question)+'</p><div id="options">'+l.quiz.options.map((o,i)=>'<label class="option"><input type="radio" name="quiz" value="'+i+'"> '+esc(o)+'</label>').join("")+'</div>'+
      '<div class="actions"><button id="checkQuiz" type="button" class="primary">检查答案并记录进度</button><span class="muted">'+(completed[l.id]?'这一课已通过概念自测':'尚未通过本课自测')+'</span></div>'+
      '<div id="feedback" role="status" aria-live="polite" class="feedback"></div></section>'+
      '<section class="section"><h3>六、衔接竞赛练习</h3><div class="note">学完基础后，进入 <b>'+esc(l.exam)+'</b> 实操题练习相同知识点。强化题难度更高，不要求第一次就能完成。</div>'+
      '<div class="actions"><a class="action" href="practice.html?question='+encodeURIComponent(l.exam)+'">打开 '+esc(l.exam)+' 竞赛题</a></div></section>';
    $("exampleCode").textContent=l.code;
    $("answerCode").textContent=l.solution;
    $("copyExample").addEventListener("click",async()=>{
      try{await navigator.clipboard.writeText(l.code);$("copyExample").textContent="已复制"}
      catch(_){$("copyExample").textContent="复制失败，请手动选中代码"}
    });
    $("showHint").addEventListener("click",()=>{
      const answer=$("answer");answer.classList.toggle("show");
      $("showHint").textContent=answer.classList.contains("show")?"隐藏参考写法":"查看参考写法";
    });
    $("checkQuiz").addEventListener("click",()=>{
      const chosen=area.querySelector('input[name="quiz"]:checked'),feedback=$("feedback");
      feedback.className="feedback";
      if(!chosen){feedback.textContent="请先选择一个答案。";return}
      if(Number(chosen.value)!==l.quiz.answer){feedback.textContent="还不正确。回看“概念”和“逐句理解”后再试。";feedback.classList.add("bad");return}
      completed[l.id]=true;persist();feedback.classList.add("good");feedback.textContent="自测正确。"+l.quiz.reason+" 当前课程已记录为完成。";
      renderNav();
    });
    const i=lessons.findIndex(x=>x.id===current);
    $("pageIndex").textContent="第 "+(i+1)+" / "+lessons.length+" 课 · "+(completed[l.id]?"自测已通过":"待完成");
    $("prev").disabled=i===0;$("next").disabled=i===lessons.length-1;
    $("prev").onclick=()=>openLesson(lessons[i-1].id);
    $("next").onclick=()=>openLesson(lessons[i+1].id);
    renderNav();
  }
  $("unfinished").addEventListener("change",renderNav);
  window.addEventListener("hashchange",()=>{const id=decodeURIComponent(location.hash.slice(1));if(lessons.some(l=>l.id===id)){current=id;render()}});
  render();
})();