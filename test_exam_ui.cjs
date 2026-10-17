// 使用隔离的 Chrome 进行页面回归，不操作用户浏览器或提交考试。
const fs=require('node:fs/promises');
const path=require('node:path');
const os=require('node:os');
const {spawn}=require('node:child_process');
const assert=require('node:assert/strict');

(async()=>{
  const report=JSON.parse(await fs.readFile(process.argv[2],'utf8'));
  const base=process.argv[3]||'http://127.0.0.1:7000';
  const output=await fs.mkdtemp(path.join(os.tmpdir(),'trainer-ui-regression-'));
  const profile=path.join(output,'profile');
  const chrome=process.env.CHROME_EXECUTABLE||'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe';
  const proc=spawn(chrome,['--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{windowsHide:true,stdio:'ignore'});
  const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
  let socket,id=0;
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
      const m=JSON.parse(event.data),p=pending.get(m.id);if(!p)return;
      clearTimeout(p.timer);pending.delete(m.id);m.error?p.reject(new Error(JSON.stringify(m.error))):p.resolve(m.result);
    });
    await send('Page.enable');
    await send('Page.navigate',{url:base+'/exam_workspace.html'});
    await waitFor("typeof showResult==='function' && typeof ExamHelpers==='object'");
    await evaluate('showResult('+JSON.stringify(report)+')');
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
    for(const qid of ['5.1.1','6.1.1']){
      await send('Page.navigate',{url:base+'/exam_question.html?qid='+qid});
      await waitFor("document.body.innerText.includes('考核要求')");
      assert.ok(await evaluate('document.body.innerText.includes('+JSON.stringify(qid)+')'));
    }
    await send('Page.navigate',{url:base+'/exam_question.html?qid=2.1.2'});
    await waitFor("location.pathname.endsWith('/2.1.2.html')");
    assert.ok(await evaluate("document.body.innerText.includes('20min')"));
    console.log(JSON.stringify({output,passed:true,answerCodeCount:20,viewports:[1440,375]}));
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
