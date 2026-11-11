import json,re,pathlib,shutil,fitz
P=pathlib.Path(__file__).parent
D=json.loads((P/'sources.json').read_text(encoding='utf8'))
OUT=P/'docs';OUT.mkdir(exist_ok=True)
themes={'行政执法':'执法 法治 裁量 监管 处罚 普法','基层治理':'基层 治理 社区 协同 网格 党建','民生服务':'民生 服务 群众 政务 养老 就业 教育 医疗','乡村振兴':'乡村 农村 农业 农民 振兴','经济发展':'经济 产业 企业 营商 市场 消费','科技创新':'科技 创新 技术 数字 人才','文化建设':'文化 文明 传统 文旅 传承','生态文明':'生态 环境 绿色 低碳 污染','担当实干':'奋斗 实干 担当 坚持 理想 信念'}
def classify(t):
 scores={k:sum(t.count(w) for w in v.split()) for k,v in themes.items()}
 return max(scores,key=scores.get) if max(scores.values()) else '担当实干'
def clean(t):
 return '\n'.join(l.strip() for l in t.splitlines() if l.strip() and not re.match(r'^(初心小助手|\d+$|【.*】$|申论领跑营)',l.strip()))
def plain(t):return re.sub(r'\s+','',t)
cards=[];seen={}
def add(title,body,theme,kind,source,page,end=None,**kwargs):
 body=plain(body);key=re.sub(r'[^\w]','',body)
 if key in seen:
  seen[key]['also'].append([source,page]);return
 c=dict(id='c'+str(len(cards)+1),title=title,body=body,theme=theme,kind=kind,source=source,page=page,end=end or page,also=[],**kwargs)
 cards.append(c);seen[key]=c
# Core cards are editorial reading prompts, with quotations retrieved from the PDFs.
cores=[
('刚柔并济','行政执法','刚性立底线｜柔性显温度｜融合提效能','执法不是为了罚','围绕底线、情理、效果展开论证；使用柔性措施须结合适用条件。',2),
('智慧执法守初心','行政执法','技术提效｜人工复核｜人文校准','必须始终坚持技术服务于人','讨论数字工具时，同时说明效率收益与纠偏机制。',2),
('规范权力运行','行政执法','裁量基准｜三项制度｜监督问责','行政执法公示制度','用于公信力、规范执法类题目，分别回答标准、过程、监督。',2),
('群众需求是起点','民生服务','识别需求｜精准供给｜效果反馈','民生服务的精准度','将抽象的以人民为中心落实为服务流程。',3),
('服务下沉与均等化','民生服务','资源下沉｜补齐短板｜公平共享','是推动城乡民生均衡发展','分析服务差距时，关注区域差异与不同群体的获得感。',3),
('治理从细微处着手','基层治理','找堵点｜通断点｜解痛点','是破解治理“堵点”','将治理问题转写为可操作的服务改进方向。',3),
('共建共治共享','基层治理','组织引领｜多方参与｜协同联动','是健全自治法治德治融合体系','按主体分别写职责，避免只列口号。',3),
('乡村产业形成合力','乡村振兴','集群发展｜多元收益｜内生动力','让乡村产业从“单打独斗”','用于分析产业组织方式与农民增收之间的联系。',3),
('人才下乡留得住','乡村振兴','有舞台｜有成长｜有归属','让返乡人才','人才措施可从岗位、发展空间和生活保障展开。',3),
('产业链提升价值','经济发展','原料变商品｜短链变全链｜提升附加值','让农产品从“原材料”','写产业升级时讲清加工、品牌、销售之间的逻辑。',3),
('法治护航营商','经济发展','稳定预期｜公平透明｜服务企业','营商环境是市场主体','把规范执法与企业信心、发展活力联系起来。',2),
('科技自立自强','科技创新','战略支撑｜创新动力｜人才基础','科技是国家强盛之基','用于创新主题开头；论证时补充题干中的具体事实。',3),
('数字工具服务治理','科技创新','数字转型｜精细服务｜治理效能','是加快数字化治理转型','避免将上平台等同于解决问题，补充实际效果。',3),
('文化传承与创新','文化建设','挖掘资源｜转化表达｜融入生活','要系统梳理传统文化资源','文化双创一般指创造性转化、创新性发展；勿与创新创业混同。',0),
('文旅融合的逻辑','文化建设','文化内容｜旅游载体｜体验传播','文化是旅游的灵魂','把文化内容、产品体验与传播效果串成论证链。',3),
('生态产品价值转化','生态文明','生态保护｜价值转化｜绿色发展','转化路径的核心抓手','分析生态与发展关系，结合材料补充具体转化路径。',3),
('保护生态惠及民生','生态文明','环境质量｜生活品质｜长远福祉','生态环境服务','论证环境保护的民生价值，避免空泛拔高。',3),
('久久为功','担当实干','持续行动｜积少成多｜坚持到底','日日行，不怕千万里','适合实干、坚持主题结尾，先回扣题目再升华。',3),
('行动胜于空谈','担当实干','知行合一｜从小处做｜落实见效','道虽迩，不行不至','将名言转译为行动要求，不堆砌引语。',3),
]
for title,theme,cue,needle,use,s in cores:
 for i,p in enumerate(D[s]['pages']):
  text=plain(clean(p))
  pos=text.find(needle)
  if pos>=0:
   start=max(text.rfind('。',0,pos),text.rfind('：',0,pos))+1
   end=text.find('。',pos)
   excerpt=text[start:end+1] if end>=0 else text[start:pos+200]
   excerpt=re.sub(r'^\d+[、.．]','',excerpt)
   if title=='法治护航营商':excerpt=excerpt[excerpt.find(needle):]
   if excerpt.startswith('“') and not excerpt.endswith('”'):excerpt=excerpt[1:]
   add(title,excerpt,theme,'核心卡',s,i+1,cue=cue,use=use);break
# Numbered entries preserve cross-page continuation and actual page ranges.
for s,startpage in [(3,0),(0,77)]:
 buf='';sp=1;ep=1;kind='表达素材'
 def flush():
  global buf
  b=plain(buf)
  if 14<=len(b)<=1000:
   title=re.split('[。；：！?？]',b)[0][:32]
   add(title,b,classify(b),kind,s,sp,ep)
  buf=''
 for i,p in enumerate(D[s]['pages'][startpage:259 if s==0 else None],startpage):
  for line in clean(p).splitlines():
   heading=(re.match(r'^[一二三四五六七八九十]+[、，.]',line) or re.match(r'^\d+[.．].{1,25}[（(].*(必看|岗位)',line))
   if heading:
    flush()
    if '开头' in line:kind='开头'
    elif '结尾' in line:kind='结尾'
    elif '名言' in line:kind='名言摘录'
    elif '案例' in line or '事例' in line:kind='案例'
    elif '影响' in line:kind='意义影响'
    else:kind='表达素材'
    continue
   m=re.match(r'^(?:\d{1,3}[、.．]|开头[一二三四五六七八九十]+|结尾[一二三四五六七八九十]+)\s*(.*)',line)
   if m:
    flush();buf=m.group(1);sp=i+1;ep=i+1
   elif buf:
    buf+=line;ep=i+1
 flush()
# Entire essays, distinct section numbering, with source paragraph leads as outline cues.
essays=[];cur=None
for i,p in enumerate(D[2]['pages'][:44]):
 lines=clean(p).splitlines();j=0
 while j<len(lines):
  l=lines[j];m=re.match(r'^范文\s*(\d+)：(.+)',l)
  if m:
   if cur:essays.append(cur)
   title=m.group(2)
   if j+1<len(lines) and len(lines[j+1])<25 and not re.search('[。；]',lines[j+1]):j+=1;title+=' · '+lines[j]
   cur=dict(id='e'+str(len(essays)+1),title=title,source=2,page=i+1,end=i+1,body='')
  elif cur and not re.match(r'^国考.*范文',l):cur['body']+=l+'\n';cur['end']=i+1
  j+=1
if cur:essays.append(cur)
doc=fitz.open(str(pathlib.Path('C:/Users/86158/Desktop/面试/笔试')/D[2]['name']))
indented=set()
for pdfpage in doc:
 for block in pdfpage.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   if 70<line['bbox'][0]<100:indented.add(''.join(sp['text'] for sp in line['spans']).strip())
for n,e in enumerate(essays):
 e['theme']='行政执法' if n<15 else '民生服务' if n<25 else '基层治理'
 paras=[]
 for line in e['body'].splitlines():
  if line in indented or not paras:paras.append(line)
  else:paras[-1]+=line
 e['body']='\n\n'.join(paras)
 e['outline']=[p.split('。')[0] for p in paras[1:-1] if 8<len(p.split('。')[0])<80][:5]
tests=[]
starts=[]
for i,p in enumerate(D[1]['pages'][4:],4):
 m=re.search(r'【套题实战\s*(\d+)】',p)
 if m and int(m.group(1)) not in [n for n,_ in starts]:starts.append((int(m.group(1)),i))
for j,(num,i) in enumerate(starts):
 end=starts[j+1][1] if j+1<len(starts) else len(D[1]['pages'])
 first=i
 if not re.search(r'20\d{2}\s*年',D[1]['pages'][i]):first=i+1
 title=next((l for l in clean(D[1]['pages'][first]).splitlines() if '年' in l and ('申论' in l or '考试' in l)),'套题实战 '+str(num))
 if num==15:end=240
 tests.append(dict(id='t'+str(num),title=title,source=1,page=first+1,end=end,body='\n\n'.join('〔PDF 第 '+str(k+1)+' 页〕\n'+clean(D[1]['pages'][k]) for k in range(first,end))))
payload=dict(cards=cards,essays=essays,tests=tests,sources=D,themes=list(themes))
(OUT/'data.js').write_text('window.LIB='+json.dumps(payload,ensure_ascii=False)+';',encoding='utf8')
(P/'.gitignore').write_text('sources.json\ncheck.txt\n*.tar.gz\n*.png\n',encoding='utf8')
print(json.dumps(dict(cards=len(cards),core=sum(c['kind']=='核心卡' for c in cards),essays=len(essays),tests=len(tests)),ensure_ascii=False))
