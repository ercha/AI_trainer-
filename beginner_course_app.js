"use strict";
(function () {
  const course=window.BEGINNER_COURSE||{};
  const extras=window.BEGINNER_COURSE_EXTRAS?.lessons||{};
  const modules=course.modules||[];
  const lessons=modules.flatMap(m=>m.steps.map(s=>({...s,moduleId:m.id,moduleName:m.name,detail:extras[s.id]||{}})));
  const ids=new Set(lessons.map(l=>l.id));
  const quizKey="ai_trainer_beginner_course_v1";
  const practiceKey="ai_trainer_beginner_practice_v1";
  const weakKey="ai_trainer_beginner_weak_v1";
  const progressVersion=2;
  const $=id=>document.getElementById(id);
  const esc=v=>String(v??"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
  const getSaved=(key)=>{try{const obj=JSON.parse(localStorage.getItem(key)||"{}");return obj&&typeof obj==="object"&&!Array.isArray(obj)?obj:{}}catch(_){return {}}};
  let passed=getSaved(quizKey),practice=getSaved(practiceKey),wrongAttempts=getSaved(weakKey),current="",search="";
  const sanitize=(obj)=>Object.fromEntries(Object.entries(obj||{}).filter(([k,v])=>ids.has(k)&&v===true));
  passed=sanitize(passed);
  const filterPractice=obj=>Object.fromEntries(Object.entries(obj||{}).filter(([k,v])=>ids.has(k)&&v&&typeof v==="object").map(([k,v])=>[k,{run:v.run===true,challenge:v.challenge===true}]));
  practice=filterPractice(practice);
  const filterWrong=obj=>Object.fromEntries(
    Object.entries(obj||{}).filter(([k,v])=>ids.has(k)&&Number.isInteger(v)&&v>0)
      .map(([k,v])=>[k,Math.min(v,999)])
  );
  wrongAttempts=filterWrong(wrongAttempts);
  const hash=decodeURIComponent(location.hash.slice(1));
  current=ids.has(hash)?hash:(lessons.find(l=>!passed[l.id])||lessons[0]||{}).id;
  const count=(values,predicate)=>values.filter(predicate).length;
  const allDone=l=>!!passed[l.id]&&!!practice[l.id]?.run&&!!practice[l.id]?.challenge;
  function writeStorage(){
    try{localStorage.setItem(quizKey,JSON.stringify(passed));localStorage.setItem(practiceKey,JSON.stringify(practice));localStorage.setItem(weakKey,JSON.stringify(wrongAttempts));return true}
    catch(_){$("storageMessage").textContent="浏览器无法保存进度；请允许本地存储或及时导出备份。";return false}
  }
  function move(id){
    if(!ids.has(id))return;
    current=id;
    history.replaceState(null,"","#"+encodeURIComponent(id));
    render();
    window.scrollTo({top:0,behavior:"instant"});
  }
  function drawNav(){
    const theory=count(lessons,l=>passed[l.id]);
    const finished=count(lessons,allDone);
    const pct=lessons.length?Math.round(100*finished/lessons.length):0;
    $("overall").innerHTML='<b>已完成 '+finished+' / '+lessons.length+' 节</b>'+
      '<div class="progress"><span style="width:'+pct+'%"></span></div>'+
      '<div class="muted">自测通过 '+theory+' 节 · 完整实践 '+finished+' 节</div>';
    const review=lessons.filter(l=>!passed[l.id]&&wrongAttempts[l.id]>0)
      .sort((a,b)=>wrongAttempts[b.id]-wrongAttempts[a.id]).slice(0,3);
    if(review.length){
      $("overall").innerHTML+='<div class="muted" style="margin-top:9px"><b>优先复习（概念自测错误）</b><div>'+
        review.map(l=>'<a href="#'+encodeURIComponent(l.id)+'">'+esc(l.id)+' · '+esc(l.title)+'</a>（'+wrongAttempts[l.id]+'次）').join('、')+
        '</div></div>';
    }
    const showIncomplete=$("unfinished").checked;
    const container=$("nav");container.replaceChildren();
    for(const m of modules){
      const box=document.createElement("div");box.className="mod";
      const title=document.createElement("button");title.type="button";title.className="mod-head";
      const done=count(m.steps,s=>allDone({id:s.id}));
      title.innerHTML='<span>'+esc(m.id)+' · '+esc(m.name)+'</span><span>'+done+'/'+m.steps.length+'</span>';
      const inner=document.createElement("div");inner.className="lessons";
      for(const s of m.steps){
        const item=lessons.find(x=>x.id===s.id);
        const detail=extras[s.id]||{};
        const match=(s.id+" "+s.title+" "+s.concept+" "+(detail.terms||[]).map(t=>t.name+" "+t.meaning).join(" ")+" "+(detail.apis||[]).map(a=>a.api+" "+a.signature).join(" ")).toLowerCase().includes(search);
        if(!match||(showIncomplete&&allDone(item)&&current!==item.id))continue;
        const btn=document.createElement("button");btn.type="button";btn.className="lesson-button"+(current===s.id?" active":"");
        const mark=allDone(item)?" <span class='done'>✓</span>":passed[s.id]?" <span class='muted'>(自测)</span>":"";
        btn.innerHTML='<span class="index">'+esc(s.id)+'</span> '+esc(s.title)+mark;
        btn.addEventListener("click",()=>move(s.id));inner.appendChild(btn);
      }
      if(!inner.children.length)continue;
      title.addEventListener("click",()=>{inner.hidden=!inner.hidden});
      box.append(title,inner);container.appendChild(box);
    }
    if(!container.childElementCount)container.innerHTML='<p class="muted">未找到匹配的课程。</p>';
  }
  const list=arr=>'<ol class="explain-list">'+(arr||[]).map(x=>'<li>'+esc(x)+'</li>').join("")+'</ol>';
  const bullet=arr=>'<ul class="warning">'+(arr||[]).map(x=>'<li>'+esc(x)+'</li>').join("")+'</ul>';
  const section=(heading,body)=>'<section class="section"><h3>'+heading+'</h3>'+body+'</section>';
  function render(){
    const l=lessons.find(l=>l.id===current);if(!l)return;
    const d=l.detail,m=modules.find(m=>m.id===l.moduleId);
    const completed=allDone(l),theory=!!passed[l.id],run=!!practice[l.id]?.run,challenge=!!practice[l.id]?.challenge;
    $("courseTitle").textContent=l.id+" · "+l.title;
    $("moduleIntro").textContent=m.intro;
    $("courseMap").textContent="模块 "+l.moduleId+" · "+m.name+" ｜ 从概念到竞赛 ｜ 推荐约 "+l.minutes+" 分钟（实践可按需增加）";
    let output='<p class="outcome"><b>为什么要学这一课：</b>'+esc(d.why||l.concept)+'</p>';
    if(l.id==="A1") output+=section("开始前：Python 必备语法",'<p>如果完全没有 Python 基础，请先掌握变量、列表、字典、for/if、函数、Path、异常处理和数组索引。</p><a class="action primary" download href="beginner_notebooks/A/Python零基础预备.ipynb">下载零基础预备课 Notebook</a>');
    output+=section("一、学习目标与概念",'<p>'+esc(l.concept)+'</p><div class="terms">'+(d.terms||[]).map(t=>'<div class="term"><strong>'+esc(t.name)+'</strong>'+esc(t.meaning)+'</div>').join("")+'</div>');
    output+=section("二、先运行完整示例",'<p class="muted">建议双击项目根目录的“启动零基础Notebook.bat”，在 Jupyter 中按 Shift+Enter 逐格执行。网页显示代码，不直接运行 Python。</p>'+
       '<pre><code id="exampleCode"></code></pre>'+
       '<div class="actions"><button type="button" id="copyExample">复制完整示例</button>'+
       '<a class="action" href="beginner_notebooks/'+esc(l.moduleId)+'/'+esc(l.id)+'.ipynb" download>下载本课 Notebook</a></div>');
    output+=section("三、逐句看懂代码",list(d.walkthrough||l.steps)+'<p class="muted">延伸知识点：</p>'+bullet(l.steps));
    output+=section("四、重点函数和参数",'<div class="muted">同一个函数的参数顺序、返回值与输入形状是比赛的高频考点。</div>'+
      (d.apis||[]).map(a=>'<details class="summary" open><summary><code>'+esc(a.api)+'</code> · 查看参数</summary><div><p><b>常见写法：</b> <code>'+esc(a.signature)+'</code></p><p><b>参数含义：</b>'+esc(a.parameters)+'</p><p><b>返回结果：</b>'+esc(a.returns)+'</p><p><b>注意：</b>'+esc(a.tip)+'</p></div></details>').join(""));
    output+=section("五、应该看到什么结果？",'<div class="outcome">'+esc(d.expected||"运行后检查输出形状、数据类型、图像或保存文件。")+'</div>'+
      '<p class="muted">这只是一种预期行为，不代表网页已经执行了你的 Python 代码。</p>');
    output+=section("六、常见错误与排查",bullet(d.pitfalls||[]));
    output+=section("七、分层动手练习",'<p>'+esc(l.challenge)+'</p>'+
      (d.levels||[]).map((x,i)=>'<div class="level"><strong>'+["① 入门","② 巩固","③ 挑战"][i]+'</strong><p>'+esc(x.replace(/^(入门|巩固|挑战)：/,""))+'</p></div>').join("")+
      '<div class="actions"><button type="button" id="showHint">查看第 1 级提示</button></div>'+
      '<p id="hintText" class="note" hidden></p>'+
      '<div id="answer"><pre><code id="answerCode"></code></pre><p class="muted">参考代码只是其中一种写法，需在 Jupyter 中运行并核验。</p></div>'+
      '<p class="muted">本课 Notebook 新增可执行检查点：完成指定 answer_ 变量后运行检查单元，成功后记录在本地。概念自测和示例运行需分别完成。</p>'+
      '<div class="actions"><button type="button" id="syncGrades">同步 Notebook 检查</button><span class="muted" id="gradeSyncMessage"></span></div>'+
      '<div class="checklist">'+
      '<label><input type="checkbox" id="runChecked" '+(run?"checked":"")+'><span>我已在 Jupyter 中实际运行本课示例，并对照预期结果检查</span></label>'+
      '<label><input type="checkbox" id="challengeChecked" '+(challenge?"checked":"")+'><span>我已独立完成至少一道练习，并检查代码运行结果</span></label></div>');
    output+=section("八、概念自测",'<p>'+esc(l.quiz.question)+'</p>'+
      '<div id="options">'+l.quiz.options.map((x,i)=>'<label class="option"><input name="quiz" type="radio" value="'+i+'"> '+esc(x)+'</label>').join("")+'</div>'+
      '<div class="actions"><button type="button" id="checkQuiz" class="primary">检查答案</button><span class="muted">'+(theory?"已通过概念自测":"待自测")+'</span></div>'+
      '<div id="feedback" class="feedback" role="status" aria-live="polite"></div>');
    output+=section("九、达到什么程度才能去做竞赛题？",'<p class="note">'+esc(d.check||"能独立理解示例并尝试完成练习。")+'</p>'+
      '<div class="actions"><a class="action" href="practice.html?question='+encodeURIComponent(l.exam)+'">进入 '+esc(l.exam)+' 竞赛强化题</a></div>'+
      '<p class="muted">竞赛题比基础课难，建议先做完当前模块的基础课程。原有实操评分与参考答案不变。</p>');
    if(l.id.endsWith("6")){
      const project=(window.BEGINNER_PROJECTS||[]).find(x=>x.id===l.moduleId);
      if(project){
        output+=section("十、本模块综合小项目",
          '<p><b>'+esc(project.title)+'</b></p><p>'+esc(project.overview)+'</p>'+
          '<ol>'+project.tasks.map(x=>'<li>'+esc(x)+'</li>').join("")+'</ol>'+
          '<p><b>项目交付：</b>'+project.outputs.map(esc).join('、')+'</p>'+
          '<div class="actions"><a class="action primary" download href="beginner_projects/'+esc(project.id)+'_project.ipynb">下载综合项目学员版</a></div>'+
          '<details class="summary"><summary>完成后查看参考项目</summary><div><p>建议独立完成项目 TODO 后再查阅答案。</p>'+
          '<a class="action" download href="beginner_projects/solutions/'+esc(project.id)+'_project_solution.ipynb">下载可运行参考答案 Notebook</a></div></details>');
      }
    }
    $("lessonContent").innerHTML=output;
    $("exampleCode").textContent=l.code;$("answerCode").textContent=l.solution;
    $("copyExample").addEventListener("click",async()=>{
      try{await navigator.clipboard.writeText(l.code);$("copyExample").textContent="复制成功"}
      catch(_){$("copyExample").textContent="复制失败，请手动选中代码"}
    });
    $("syncGrades").addEventListener("click",()=>syncAutoGrades(true));
    let hintStep=0;
    $("showHint").addEventListener("click",()=>{
      hintStep=(hintStep+1)%4;
      const hint=$("hintText");
      $("answer").classList.toggle("show",hintStep===3);
      hint.hidden=hintStep===0||hintStep===3;
      if(hintStep===1)hint.textContent="第 1 级：先明确目标。"+(d.walkthrough?.[0]||l.steps?.[0]||l.challenge);
      if(hintStep===2)hint.textContent="第 2 级：可参考 "+(d.apis||[]).slice(0,2).map(a=>a.signature).join("；")+"。注意结果应符合："+(d.expected||"任务要求");
      if(hintStep===3)hint.textContent="";
      $("showHint").textContent=["查看第 1 级提示","查看第 2 级提示","查看完整参考写法","收起提示并重新开始"][hintStep];
    });
    for(const field of ["run","challenge"]){
      const el=$(field==="run"?"runChecked":"challengeChecked");
      el.addEventListener("change",()=>{
        const old=practice[l.id]||{run:false,challenge:false};
        practice[l.id]={...old,[field]:el.checked};
        writeStorage();drawNav();refreshStatus();
      });
    }
    $("checkQuiz").addEventListener("click",()=>{
      const chosen=document.querySelector('input[name="quiz"]:checked'),feedback=$("feedback");
      feedback.className="feedback";
      if(!chosen){feedback.textContent="请先选一个答案。";return}
      if(Number(chosen.value)!==l.quiz.answer){
        wrongAttempts[l.id]=(wrongAttempts[l.id]||0)+1;
        writeStorage();drawNav();
        feedback.textContent="当前答案不正确。已记录为待复习课程，请回到『概念』和『逐句说明』重新检查。";
        feedback.classList.add("bad");return;
      }
      passed[l.id]=true;writeStorage();feedback.classList.add("good");
      feedback.textContent="自测通过："+l.quiz.reason+"（实践是否完成仍以你在 Jupyter 中运行的情况为准。）";
      drawNav();refreshStatus();
    });
    const index=lessons.findIndex(x=>x.id===l.id);
    $("prev").disabled=index===0;$("next").disabled=index===lessons.length-1;
    $("prev").onclick=()=>move(lessons[index-1].id);
    $("next").onclick=()=>move(lessons[index+1].id);
    function refreshStatus(){
      const good=allDone(l);
      $("pageIndex").textContent="第 "+(index+1)+" / "+lessons.length+" 课 · "+(good?"全部完成":passed[l.id]?"概念自测通过，仍需完成实践":"待完成");
    }
    refreshStatus();drawNav();
  }
  async function syncAutoGrades(showFeedback=false){
    try{
      const response=await fetch("api/beginner/grades",{cache:"no-store"});
      if(!response.ok) throw new Error("HTTP "+response.status);
      const payload=await response.json();
      let newly=0;
      for(const id of Object.keys(payload.grades||{})){
        if(!ids.has(id)||payload.grades[id]?.passed!==true)continue;
        if(!practice[id]?.challenge){
          practice[id]={...(practice[id]||{run:false,challenge:false}),challenge:true};
          newly++;
        }
      }
      if(newly){writeStorage();render()}
      if(showFeedback)$("gradeSyncMessage").textContent="已同步，新增 "+newly+" 节已通过练习。请单独确认示例运行。";
    }catch(err){
      if(showFeedback)$("gradeSyncMessage").textContent="同步失败："+String(err.message||err)+"；请确认本地训练服务已启动。";
    }
  }
  function exportProgress(){
    const payload={schema:"ai-trainer-beginner-progress",version:progressVersion,exportedAt:new Date().toISOString(),quiz:passed,practice,weak:wrongAttempts};
    const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json"});
    const url=URL.createObjectURL(blob);
    const a=document.createElement("a");
    a.href=url;a.download="AI_trainer-零基础学习进度.json";a.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
    $("storageMessage").textContent="已生成进度备份文件。请妥善保存以便以后恢复。";
  }
  async function importProgress(file){
    if(!file)return;
    try{
      const data=JSON.parse(await file.text());
      if(data.schema!=="ai-trainer-beginner-progress"||data.version!==progressVersion)throw Error("文件格式或版本不匹配");
      if(!data.quiz||!data.practice||typeof data.quiz!=="object"||typeof data.practice!=="object")throw Error("学习进度字段缺失");
      if(!window.confirm("导入将覆盖当前浏览器中的零基础学习进度，确定继续吗？"))return;
      passed=sanitize(data.quiz);practice=filterPractice(data.practice);
      wrongAttempts=filterWrong(data.weak||{});
      writeStorage();render();
      $("storageMessage").textContent="进度已恢复。";
    }catch(err){$("storageMessage").textContent="导入失败："+String(err.message||err)}
    finally{$("importFile").value=""}
  }
  $("unfinished").addEventListener("change",drawNav);
  $("findLesson").addEventListener("input",event=>{search=event.target.value.trim().toLowerCase();drawNav()});
  $("exportProgress").addEventListener("click",exportProgress);
  $("importProgress").addEventListener("click",()=>$("importFile").click());
  $("importFile").addEventListener("change",event=>importProgress(event.target.files?.[0]));
  window.addEventListener("hashchange",()=>{
    const id=decodeURIComponent(location.hash.slice(1));
    if(ids.has(id)){current=id;render()}
  });
  render();
  syncAutoGrades(false);
})();