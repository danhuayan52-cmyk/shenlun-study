from playwright.sync_api import sync_playwright
from pathlib import Path
import json
root=Path(__file__).parent
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,channel='msedge')
 page=b.new_page(viewport={'width':1440,'height':1000})
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto((root/'dist/index.html').as_uri())
 page.wait_for_load_state('networkidle')
 assert page.locator('.theme').count()==9
 page.screenshot(path=str(root/'desktop.png'),full_page=True)
 page.get_by_role('button',name='浏览素材书架',exact=True).click()
 page.locator('#search').fill('刚柔')
 assert page.locator('.card').count()>0
 page.get_by_role('button',name='展开阅读 ↗').first.click()
 assert page.locator('dialog').is_visible()
 page.get_by_role('button',name='☆ 加入收藏',exact=True).click()
 page.get_by_role('button',name='查看原文所在页').click()
 assert '执法' in page.locator('#modal').inner_text()
 page.get_by_role('button',name='关闭 ×').click()
 page.locator('#nav button').nth(2).click()
 page.get_by_role('button',name='核心卡练习（最多 10 张）').click()
 page.locator('#draft').fill('刚性立底线，柔性显温度，融合提效能。')
 page.get_by_role('button',name='展开原文，核对记忆').click()
 page.get_by_role('button',name='记住了 · 延后复习').click()
 assert page.evaluate('Object.keys(state.records).length')==1
 page.reload();page.wait_for_load_state('networkidle')
 assert page.evaluate('Object.keys(state.records).length')==1
 page.locator('#nav button').nth(3).click()
 assert page.locator('.listrow').count()==35
 page.locator('#nav button').nth(4).click()
 assert page.locator('.listrow').count()==15
 page.locator('#nav button').nth(0).click()
 page.set_viewport_size({'width':390,'height':844})
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.screenshot(path=str(root/'mobile.png'),full_page=True)
 assert not errors,errors
 data=page.evaluate('({counts:{cards:LIB.cards.length,essays:LIB.essays.length,tests:LIB.tests.length},cores:LIB.cards.filter(x=>x.kind==="核心卡").map(x=>x.title),tests:LIB.tests.map(x=>({title:x.title,page:x.page,end:x.end}))})')
 print(json.dumps(data,ensure_ascii=False))
 b.close()
