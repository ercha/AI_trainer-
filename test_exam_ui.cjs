// 使用隔离的 Chrome 进行页面回归，不操作用户浏览器或提交考试。
const fs=require('node:fs/promises');
const path=require('node:path');
const os=require('node:os');
const {spawn}=require('node:child_process');
const assert=require('node:assert/strict');

(async()=>{
  const report=JSON.parse(await fs.readFile(process.argv[2],'utf8'));
  // 评分差异展示使用内存样例，不提交或改写读取的历史答卷。
  const displayReport={...report,checks:[{label:'ReviewScore 标准化',ok:false,cell:2,line:1,
    actual:"data['ReviewScore'] = (data['ReviewScore'] - data['ReviewScore'].mean()) / data['ReviewScore']",
    expected:"data['ReviewScore'] = (data['ReviewScore'] - data['ReviewScore'].mean()) / data['ReviewScore'].std()"}]};
  const base=process.argv[3]||'http://127.0.0.1:7000';
  const output=await fs.mkdtemp(path.join(os.tmpdir(),'trainer-ui-regression-'));
  const profile=path.join(output,'profile');
  const chrome=process.env.CHROME_EXECUTABLE||'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe';
  const proc=spawn(chrome,['--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{windowsHide:true,stdio:'ignore'});
  const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
  let socket,id=0;
  const startRequests=[];
  const pending=new Map();
  const send=(method,params={})=>new Promise((resolve,reject)=>{
    const n=++id,timer=setTimeout(()=>{pending.delete(n);reject(new Error(method+' timeout'))},15000);
    pending.set(n,{resolve,reject,timer});socket.send(JSON.stringify({id:n,method,params}));
  });
  const evaluate=async expression=>{
    const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
    if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));
    return r.result.value;
  };
  const waitFor=async expression=>{
    for(let i=0;i<100;i++){if(await evaluate(expression))return;await delay(100)}
    throw new Error('Page not ready: '+expression);
  };
  try{
    let port;
    for(let i=0;i<100;i++){
      try{port=(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break}catch(_){await delay(100)}
    }
    assert.ok(port,'Chrome startup');
    const pages=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();
    const target=pages.find(x=>x.type==='page');
    socket=new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true})});
    socket.addEventListener('message',event=>{
      const m=JSON.parse(event.data);
      if(m.method==='Page.javascriptDialogOpening'){
        send('Page.handleJavaScriptDialog',{accept:true}).catch(()=>{});
        return;
      }
      // 隔离测试中的考试状态，避免连接用户当前正在使用的 Jupyter。
      if(m.method==='Fetch.requestPaused'){
        const isStart=new URL(m.params.request.url).pathname==='/api/exam/start';
        if(isStart)startRequests.push(JSON.parse(m.params.request.postData));
        const response=isStart?{ok:false,message:'回归测试已拦截启动请求，未创建真实考试'}:{ok:true,active:false,session:null,last_result:null};
        send('Fetch.fulfillRequest',{requestId:m.params.requestId,responseCode:isStart?503:200,
          responseHeaders:[{name:'Content-Type',value:'application/json'}],
          body:Buffer.from(JSON.stringify(response)).toString('base64')}).catch(()=>{});
        return;
      }
      const p=pending.get(m.id);if(!p)return;
      clearTimeout(p.timer);pending.delete(m.id);m.error?p.reject(new Error(JSON.stringify(m.error))):p.resolve(m.result);
    });
    await send('Page.enable');
    await send('Fetch.enable',{patterns:[{urlPattern:'*/api/exam/status',requestStage:'Request'},{urlPattern:'*/api/exam/start',requestStage:'Request'}]});
    await send('Page.navigate',{url:base+'/exam_workspace.html'});
    await waitFor("typeof showResult==='function' && typeof ExamHelpers==='object'");
    await evaluate('showResult('+JSON.stringify(displayReport)+')');
    for(const [name,width,height] of [['desktop',1440,1000],['mobile',375,900]]){
      await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
      await delay(150);
      assert.equal(await evaluate('resultBody.scrollWidth>resultBody.clientWidth'),false,name+' horizontal overflow');
      assert.ok(await evaluate("resultBody.innerText.includes('当前代码') && resultBody.innerText.includes('参考写法') && resultBody.innerText.includes('std()')"));
      const codeBoxes=await evaluate("[...resultBody.querySelector('details[open]').querySelectorAll('pre')].map(x=>({height:x.getBoundingClientRect().height,overflow:x.scrollWidth>x.clientWidth}))");
      assert.ok(codeBoxes.length===2&&codeBoxes.every(x=>x.height>40&&!x.overflow),name+' code comparison layout');
      const shot=await send('Page.captureScreenshot',{format:'png'});
      await fs.writeFile(path.join(output,'grading-'+name+'.png'),Buffer.from(shot.data,'base64'));
    }
    const answers=await evaluate(`(async()=>{const qs=['5.1.1','5.1.2','5.1.3','5.1.4','5.1.5',...Array.from({length:5},(_,i)=>Array.from({length:3},(_,j)=>'6.'+(i+1)+'.'+(j+1))).flat()];for(const q of qs){const r=await fetch('/人工智能训练师三级素材/操作题答案/'+q+'_答案.md');if(!r.ok||!extractCode(await r.text()))return false}return true})()`);
    assert.ok(answers,'20 answer code blocks');
    await evaluate("document.querySelector('.result-actions [onclick=\"openAnswer()\"]').click()");
    await waitFor("document.querySelector('.reference-dialog[open]') && document.getElementById('referenceText').textContent.includes('import')");
    assert.ok(await evaluate('referenceTitle.textContent.includes('+JSON.stringify(report.qid)+')'),'submission answer matches report');
    await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape'});
    await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Escape',code:'Escape'});
    await waitFor("!document.querySelector('.reference-dialog[open]')");
    assert.ok(await evaluate("resultMask.classList.contains('show')"),'answer closes without losing score report');

    await send('Page.navigate',{url:base+'/practice.html'});
    await waitFor("document.getElementById('appFrame')?.contentDocument?.querySelectorAll('.task-description p').length > 5");
    const home=await evaluate(`(()=>{const d=appFrame.contentDocument;return{paragraphs:d.querySelectorAll('.task-description p').length,requirements:d.querySelectorAll('.task-requirement').length,todos:d.querySelectorAll('.task-todos li').length,answerVisible:getComputedStyle(d.querySelector('#taskHead .toolbar')).display!=='none',text:d.querySelector('#taskHead').textContent}})()`);
    assert.equal(home.paragraphs,13,'original paragraphs preserved');
    assert.equal(home.requirements,3,'numbered requirements marked TODO');
    assert.equal(home.todos,0,'homepage does not render code-edit TODO block');
    assert.ok(home.answerVisible&&!home.text.includes('代码修改 TODO'),'answer entry remains without code-edit TODO block');
    const coverage=await evaluate(`(()=>{const w=appFrame.contentWindow;return w.eval('Q.filter(q=>q.notebookAvailable).map(q=>({id:q.id}))')})()`);
    assert.equal(coverage.length,40,'forty Notebook questions');
    for(const [name,width,height] of [['desktop',1440,1000],['mobile',375,900]]){
      await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
      await evaluate("appFrame.contentWindow.selectQ('1.1.5');appFrame.contentWindow.setMode('fill');appFrame.contentDocument.querySelector('[data-mode=exam]').click()");
      await waitFor("appFrame.contentDocument.querySelector('[onclick=\"parent.startJupyterExam()\"]:not([disabled])')");
      await evaluate("appFrame.contentDocument.querySelector('.tabs').scrollIntoView();appFrame.contentWindow.scrollBy(0,-appFrame.contentDocument.querySelector('header').offsetHeight-12)");
      const layout=await evaluate(`(()=>{const d=appFrame.contentDocument,rect=s=>d.querySelector(s).getBoundingClientRect();const start=rect('[onclick="parent.startJupyterExam()"]');return{qid:appFrame.contentWindow.getCurrentQuestion().id,available:appFrame.contentWindow.getCurrentQuestion().notebookAvailable,startTop:start.top,startBottom:start.bottom,previewTop:rect('#examQuestionPreview').top,descriptionTop:rect('#taskDescription').top,height:appFrame.clientHeight,overflow:d.documentElement.scrollWidth>d.documentElement.clientWidth,description:d.querySelector('#taskDescription').textContent}})()`);
      assert.equal(layout.qid,'1.1.5');
      assert.equal(layout.available,true,'1.1.5 original Notebook exists');
      assert.ok(layout.startTop>=0&&layout.startBottom<layout.height,name+' start button visible after exam tab click');
      assert.ok(layout.startBottom<layout.previewTop&&layout.startBottom<layout.descriptionTop,name+' start before preview and long description');
      assert.ok(layout.description.includes('cleaned_vehicle_traffic_data.csv')&&layout.description.includes('1.1.5-5'),'full task preserved');
      assert.equal(layout.overflow,false,name+' exam entry overflow');
      const shot=await send('Page.captureScreenshot',{format:'png'});
      await fs.writeFile(path.join(output,'exam-entry-'+name+'.png'),Buffer.from(shot.data,'base64'));
      await evaluate("appFrame.contentDocument.querySelector('[onclick=\"parent.startJupyterExam()\"]').click()");
      await waitFor("appFrame.contentDocument.getElementById('nbExamState').textContent.includes('回归测试已拦截启动请求')");
      assert.deepEqual(startRequests.at(-1),{qid:'1.1.5'},name+' start targets selected question');
    }
    assert.equal(startRequests.length,2,'both start requests intercepted without starting Jupyter');
    await evaluate("appFrame.contentWindow.selectQ('4.2.5')");
    await waitFor("appFrame.contentDocument.querySelector('[onclick=\"parent.startJupyterExam()\"][disabled]')");
    assert.equal(await evaluate('appFrame.contentWindow.getCurrentQuestion().notebookAvailable'),false,'Word-only question remains unavailable');
    await evaluate("appFrame.contentWindow.selectQ('1.1.1')");
    await waitFor("appFrame.contentDocument.querySelector('[onclick=\"parent.startJupyterExam()\"]:not([disabled])')");
    for(const [name,width,height] of [['desktop',1440,1000],['mobile',375,900]]){
      await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
      await delay(150);
      assert.equal(await evaluate('appFrame.contentDocument.documentElement.scrollWidth>appFrame.contentDocument.documentElement.clientWidth'),false,name+' homepage overflow');
      const shot=await send('Page.captureScreenshot',{format:'png'});
      await fs.writeFile(path.join(output,'task-'+name+'.png'),Buffer.from(shot.data,'base64'));
      await evaluate("appFrame.contentDocument.querySelector('#taskHead .toolbar button').click()");
      await waitFor("document.querySelector('.reference-dialog[open]') && referenceText.textContent.includes('import pandas')");
      assert.equal(await evaluate('referenceText.scrollWidth>referenceText.clientWidth'),false,name+' answer overflow');
      await evaluate("Object.defineProperty(navigator.clipboard,'writeText',{configurable:true,value:async t=>{window.__copiedAnswer=t}});document.querySelector('[data-action=copy]').click()");
      await waitFor("referenceStatus.textContent==='已复制'");
      assert.ok(await evaluate("window.__copiedAnswer.includes('age_patient_count')"),'copy complete code');
      await evaluate("document.querySelector('[data-mode=full]').click()");
      assert.ok(await evaluate("referenceText.textContent.includes('## 代码解析')"),'full answer explanation');
      const answerShot=await send('Page.captureScreenshot',{format:'png'});
      await fs.writeFile(path.join(output,'answer-'+name+'.png'),Buffer.from(answerShot.data,'base64'));
      await evaluate('AnswerViewer.close()');
    }
    await evaluate("appFrame.contentWindow.selectQ('6.1.1');appFrame.contentDocument.querySelector('#taskHead .toolbar button').click()");
    await waitFor("document.querySelector('.reference-dialog[open]') && referenceTitle.textContent.includes('6.1.1') && referenceText.textContent.includes('augmentation_preview.png')");
    assert.ok(await evaluate("referenceText.textContent.includes('import cv2') && !referenceText.textContent.includes('_____________')"),'advanced answer includes completed scaffold');
    await evaluate('AnswerViewer.close();AnswerViewer.open("4.1.1")');
    await waitFor("referenceStatus.textContent.includes('文档或方案题')");
    assert.ok(await evaluate("document.querySelector('[data-mode=code]').disabled && referenceText.textContent.length>100"),'noncode answer fallback');
    await evaluate('AnswerViewer.close();AnswerViewer.open("9.9.9")');
    await waitFor("referenceText.textContent.includes('读取失败')");
    assert.ok(await evaluate("document.querySelector('[data-action=copy]').disabled"),'failed load cannot copy stale answer');
    await evaluate('AnswerViewer.close();openExamRecords()');
    await waitFor("recordsBox.querySelector('.record-actions .rbtn:not(.primary)')");
    await evaluate("recordsBox.querySelector('.record-actions .rbtn:not(.primary)').click()");
    await waitFor("document.querySelector('.reference-dialog[open]') && referenceText.textContent.length>100");
    assert.equal(await evaluate("referenceTitle.textContent.split(' ')[0]"),await evaluate("recordsBox.querySelector('.record-title').textContent.trim().split(' ')[0]"),'record answer uses record question not selected question');

    await send('Page.navigate',{url:base+'/exam_review.html?id='+encodeURIComponent(report.id)});
    await waitFor("!document.getElementById('referenceBtn').disabled");
    await evaluate('referenceBtn.click()');
    await waitFor("document.querySelector('.reference-dialog[open]') && referenceText.textContent.includes('import')");
    assert.ok(await evaluate('referenceTitle.textContent.includes('+JSON.stringify(report.qid)+')'),'historic review reference answer');
    const reviewShot=await send('Page.captureScreenshot',{format:'png'});
    await fs.writeFile(path.join(output,'review-mobile.png'),Buffer.from(reviewShot.data,'base64'));
    await send('Page.navigate',{url:base+'/exam_workspace.html'});
    await waitFor("typeof loadQuestion==='function'");
    await evaluate("loadQuestion('1.1.1')");
    await waitFor("questionFrame.contentDocument?.querySelectorAll('.task-requirement').length===3");
    assert.ok(await evaluate("getComputedStyle(questionFrame.contentDocument.querySelector('.right-column')).display==='none'"),'exam sidebar stays hidden after async question load');
    assert.ok(await evaluate("questionFrame.contentDocument.body.textContent.includes('1.1.1-3') && !questionFrame.contentDocument.body.textContent.includes('代码修改 TODO')"),'exam preserves deliverables without code-edit list');
    for(const [name,width,height] of [['desktop',1440,1000],['mobile',375,900]]){
      await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
      await evaluate(width<760?"if(!rightHidden)toggleRight()":"if(rightHidden)toggleRight()");
      await evaluate("questionFrame.contentDocument.querySelector('.task-requirement').scrollIntoView()");
      await delay(100);
      assert.equal(await evaluate('questionFrame.contentDocument.documentElement.scrollWidth>questionFrame.contentDocument.documentElement.clientWidth'),false,name+' exam question overflow');
      const shot=await send('Page.captureScreenshot',{format:'png'});
      await fs.writeFile(path.join(output,'exam-question-'+name+'.png'),Buffer.from(shot.data,'base64'));
    }
    for(const qid of ['5.1.1','6.1.1']){
      await send('Page.navigate',{url:base+'/exam_question.html?qid='+qid});
      await waitFor("document.body.innerText.includes('考核要求')");
      assert.ok(await evaluate('document.body.innerText.includes('+JSON.stringify(qid)+')'));
      const labels=await evaluate("[...document.querySelectorAll('.req .todo-label')].map(x=>x.textContent)");
      assert.ok(labels.length>0&&labels.every((text,i)=>text==='TODO '+(i+1)),'competition requirements use distinct TODO labels');
    }
    await send('Page.navigate',{url:base+'/exam_question.html?qid=2.1.2'});
    await waitFor("document.querySelector('.task-description')");
    assert.ok(await evaluate("document.body.innerText.includes('20min')"));
    assert.ok(await evaluate("document.querySelectorAll('.task-requirement').length>0 && document.body.innerText.includes('技能要求') && document.body.innerText.includes('质量指标') && document.body.innerText.includes('2.1.2.html')"),'original question metadata and submissions preserved');
    console.log(JSON.stringify({output,passed:true,answerCodeCount:40,notebookQuestions:coverage.length,viewports:[1440,375],flows:['home','exam-entry','intercepted-exam-start','copy','submitted-report','records','historic-review','noncode','load-error']}));
  }finally{
    if(socket&&socket.readyState===WebSocket.OPEN){try{await send('Browser.close')}catch(_){}socket.close()}
    if(proc.exitCode===null){await Promise.race([new Promise(resolve=>proc.once('exit',resolve)),delay(5000)])}
    if(proc.exitCode===null)proc.kill();
    for(const p of pending.values()){clearTimeout(p.timer);p.reject(new Error('Browser closed'))}
    if(path.dirname(path.resolve(profile))===path.resolve(output)&&path.resolve(output).startsWith(path.resolve(os.tmpdir())+path.sep)){
      await fs.rm(profile,{recursive:true,force:true,maxRetries:3,retryDelay:200}).catch(()=>{});
    }
  }
})().catch(error=>{console.error(error);process.exitCode=1});
