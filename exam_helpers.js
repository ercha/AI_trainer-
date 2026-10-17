(function(root){
  function extractCode(markdown){
    const blocks=[],pattern=/(```|~~~)(?:python|py)?[ \t]*\r?\n([\s\S]*?)\1/gi;
    let match;
    while((match=pattern.exec(markdown))!==null)blocks.push(match[2].trim());
    return blocks.join('\n\n');
  }
  function questionUrl(qid){return '/exam_question.html?qid='+encodeURIComponent(qid)}
  root.ExamHelpers={extractCode,questionUrl};
  if(typeof module!=='undefined')module.exports=root.ExamHelpers;
})(typeof window==='undefined'?globalThis:window);
