(function(root){
  const esc=s=>String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  const clarifications={
    '1.1.1':{
      '2-1':'根据 DaysInHospital 是否严格大于 7 生成 RiskLevel；等于 7 天仍为低风险患者。',
      '2-3':'计算高风险患者占全部患者的比例，分母为数据集总行数，而不是低风险人数。',
      '2-4':'计算低风险患者占全部患者的比例，分母同样为数据集总行数。',
      '3-1':'按 bmi_bins 和 bmi_labels 分组，使用左闭右开区间 [0,18.5)、[18.5,24)、[24,28)、[28,+∞)。',
      '3-2':'计算每个 BMI 组内高风险人数 / 该组总人数，不是该组高风险人数占全体患者的比例。',
      '4-1':'按 age_bins 和 age_labels 左闭右开分组；整数年龄 25 岁属于首组，26 岁属于第二组，66 岁起属于最后一组。',
      '4-2':'计算各年龄组内高风险人数 / 该年龄组总人数。'
    },
    '1.1.2':{'4-3':'筛选 Humidity 传感器中 Value 小于 0 或大于 100 的记录，与上方温度异常条件合并。'},
    '1.1.3':{
      '2-1':'统计每一列的缺失值数量。','2-2':'统计整行重复的数据条数。',
      '3-1':'检查 Age 是否在 18～70 岁之间，包含两个端点。','3-2':'检查 Income 是否严格大于 0。',
      '3-3':'检查 LoanAmount 是否严格小于 Income 的 5 倍，结果存入 is_loan_amount_valid。',
      '3-4':'检查 CreditScore 是否在 300～850 之间，包含两个端点。'
    },
    '1.1.4':{'2-4':'将 ReviewScore 列转换为 int 类型，再继续进行下方标准化处理。'},
    '1.1.5':{
      '2-4':'将 TravelDistance 列转换为 float 类型。','2-5':'将 TravelTime 列转换为 float 类型。',
      '2-6':'保留 Age 在 18～70 之间的记录，包含端点。','2-7':'保留 Speed 在 0～200 之间的记录，包含端点。',
      '2-8':'保留 TravelDistance 在 1～1000 之间的记录，包含端点。','2-9':'保留 TravelTime 在 1～1440 之间的记录，包含端点。',
      '3-1':'检查 Age 是否在 18～70 之间，与其余字段条件共同取反找出不合理记录。',
      '3-2':'检查 Speed 是否在 0～200 之间。','3-3':'检查 TravelDistance 是否在 1～1000 之间。',
      '3-4':'检查 TravelTime 是否在 1～1440 之间。','3-8':'统计 AgeGroup 中各年龄段的驾驶员人数。'
    },
    '2.1.1':{'1-10':'从 data 中取 mpg 列作为目标变量 y；X 只包含选定的特征列，不包含 mpg。'},
    '2.1.2':{
      '1-4':'记录删除缺失值行之后的数据行数，供上方初始行数相减计算删除量。',
      '1-6':'使用已创建的 scaler 对 numerical_features 指定的月生活费列进行标准化，并写回原列。',
      '1-7':'按原题选择性别、年级、生源地、月生活费、低碳生活经历以及第 6～8 项低碳观念，共 8 个特征；使用 Excel 中的完整列名。',
      '1-9':'将“低碳行为积极性”对应列设为目标变量 y，不要将该列同时放入 X。'
    },
    '2.1.3':{'1-5':'计算四分位距 IQR = Q3 - Q1，供下方 1.5 倍 IQR 异常值筛选使用。'},
    '2.1.5':{
      '1-6':'在非法年龄和负数年龄已被移除后，将 Your age 列转换为整数类型。',
      '1-8':'使用 LabelEncoder 将健身水平这一类别列编码为整数标签；这里不是 MinMax 数值归一化。'
    },
    '2.2.3':{
      '1-12':'使用 y_test 和随机森林预测 y_pred 计算均方误差 MSE。','1-13':'使用 y_test 和 y_pred 计算决定系数 R²。',
      '1-17':'计算 xgb_model 在 X_train、y_train 上的得分并写入报告。',
      '1-18':'计算 xgb_model 在 X_test、y_test 上的得分并写入报告。',
      '1-19':'使用 y_test 和 y_pred_xgb 计算 XGBoost 的 MSE 并写入报告。',
      '1-20':'使用 y_test 和 y_pred_xgb 计算 XGBoost 的 R²；填空中补齐对应调用，使整行 f-string 括号配对。'
    },
    '2.2.4':{'1-13':'计算 y_test 与 y_pred 的 R² 并写入线性回归报告。','1-18':'计算 y_test 与 y_pred_xg 的 R² 并写入 XGBoost 报告。'},
    '2.2.5':{'1-13':'计算 y_test 与 y_pred 的平均绝对误差 MAE 并写入报告。','1-14':'计算 y_test 与 y_pred 的 R² 并写入报告。'},
    '3.2.2':{'1-5':'在轴 0 添加 batch 维度，将 (28,28) 变为 (1,28,28)。','1-6':'再次在轴 0 添加通道维度，得到模型需要的 (1,1,28,28)。'},
    '6.1.1':{'2-2':'按当前 Notebook 框架旋转 +15°，保持原图尺寸；本题现有保存文件名为 _rot15.jpg。'}
  };
  function splitParagraphs(text){return String(text||'').replace(/\r/g,'').split(/\n+/).map(x=>x.trim()).filter(Boolean)}
  function decodeQuestionPage(html,id){
    const doc=new DOMParser().parseFromString(String(html||''),'text/html');
    const title=(doc.title||'').replace(new RegExp('^'+id.replace(/\./g,'\\.')+'\\s*'),'').trim()||id+' 实操题';
    const headings=[...doc.querySelectorAll('h1,h2,h3,h4')],start=headings.find(x=>x.textContent.trim()==='工作任务');
    if(!start)return{title,taskText:''};
    const end=headings[headings.indexOf(start)+1],range=doc.createRange();range.setStartAfter(start);
    if(end)range.setEndBefore(end);else range.setEndAfter(start.parentNode.lastChild);
    const fragment=range.cloneContents();
    // 离屏文档的 innerText 不保留段落，显式使用块级标签与 br 还原分隔。
    const walk=node=>node.nodeType===3?node.textContent:node.nodeType===1&&node.tagName==='BR'?'\n':
      [...node.childNodes].map(walk).join('')+(node.nodeType===1&&/^(P|DIV|LI|TR|UL|OL)$/.test(node.tagName)?'\n':'');
    return{title,taskText:splitParagraphs(walk(fragment)).join('\n\n')};
  }
  function notebookTodos(notebook,qid){
    const todos=[];
    (notebook.cells||[]).forEach((cell,index)=>{
      if(cell.cell_type!=='code')return;
      const lines=(Array.isArray(cell.source)?cell.source.join(''):String(cell.source||'')).split(/\r?\n/);
      lines.forEach((line,i)=>{
        if(!line.trimStart().startsWith('#'))return;
        const match=line.match(/\bTODO\s*(\d+(?:-\d+)*)\b\s*[:：]?\s*(.*)/i);if(!match)return;
        let description=match[2].replace(/[=\s]+$/g,'').trim(),next=i+1;
        const comments=[];
        while(next<lines.length&&(lines[next].trim()===''||lines[next].trimStart().startsWith('#'))){
          const text=lines[next].replace(/^\s*#\s*/,'').trim();
          if(/TODO|^=+$/.test(text))break;
          if(text)comments.push(text);next++;
        }
        description=clarifications[qid]?.[match[1]]||description||comments.join('；');
        const context=lines[next]||'';
        if(!description||description==='补全下方代码')description=context.includes('#')?context.slice(context.indexOf('#')+1).trim():'补全本步骤的空白，保持下方变量和后续调用所需的数据类型一致。';
        todos.push({id:match[1],description,cell:index+1,line:i+1,context:context.trim()});
      });
    });
    return todos;
  }
  function renderTaskParagraphs(text){
    const paragraphs=splitParagraphs(text);
    let task=0;
    return paragraphs.map(text=>{
      if(/^(?:[（(]\d+[）)]|\d+[、．](?!\d))/.test(text))return `<p class="task-requirement"><b class="todo-label">TODO ${++task}</b> ${esc(text)}</p>`;
      return `<p>${esc(text)}</p>`;
    }).join('');
  }
  function renderRequirementList(requirements){
    return (requirements||[]).map((text,index)=>{
      const prefix=text.match(/^TODO\s*(\d+(?:-\d+)*)\s*[:：]?\s*/i);
      return '<li><b class="todo-label">TODO '+esc(prefix?prefix[1]:index+1)+'</b> '+esc(prefix?text.slice(prefix[0].length):text)+'</li>';
    }).join('');
  }
  function renderDescription(question){
    const body=renderTaskParagraphs(question.taskText);
    return `${body?'<h3>完整任务说明</h3><div class="task-description">'+body+'</div>':''}${question.req?.length?'<h3>任务要点</h3><ol class="req">'+renderRequirementList(question.req)+'</ol>':''}`;
  }
  root.TaskContent={decodeQuestionPage,notebookTodos,renderDescription,renderTaskParagraphs,renderRequirementList,splitParagraphs};
  if(typeof module!=='undefined')module.exports=root.TaskContent;
})(typeof window==='undefined'?globalThis:window);
