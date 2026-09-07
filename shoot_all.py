import threading, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
class Quiet(SimpleHTTPRequestHandler):
    def __init__(self,*a,**k): super().__init__(*a,directory='dist',**k)
    def log_message(self,*a): pass
srv=ThreadingHTTPServer(('127.0.0.1',8124),Quiet); threading.Thread(target=srv.serve_forever,daemon=True).start()
pages=["/","/about/","/services/","/services/wholesale-voice/","/services/retail-voice/","/services/premium-cli/","/services/virtual-numbers/","/coverage/","/partners/","/contact/","/contact/thanks/","/privacy/","/terms/","/404.html"]
errors={}; console={}
with sync_playwright() as p:
    b=p.chromium.launch()
    for width,tag in ((1440,"desk"),(390,"mob")):
        ctx=b.new_context(viewport={'width':width,'height':900},device_scale_factor=1)
        for path in pages:
            pg=ctx.new_page(); errs=[]; cons=[]
            pg.on('pageerror',lambda e,errs=errs: errs.append(str(e)))
            pg.on('console',lambda m,cons=cons: cons.append(m.text) if m.type in ('error','warning') else None)
            pg.goto('http://127.0.0.1:8124'+path,wait_until='networkidle'); pg.wait_for_timeout(1800)
            # force all reveals so full-page shots show final state
            pg.evaluate("document.querySelectorAll('[data-reveal]').forEach(e=>e.classList.add('is-on'))"); pg.wait_for_timeout(900)
            name=path.strip('/').replace('/','-') or 'home'
            pg.screenshot(path=f'shots/{tag}-{name}.png',full_page=True)
            if errs: errors[f'{tag}{path}']=errs
            if cons: console[f'{tag}{path}']=cons
            pg.close()
        # interactive states
        pg=ctx.new_page(); pg.goto('http://127.0.0.1:8124/contact/',wait_until='networkidle'); pg.wait_for_timeout(800)
        pg.click('button[type=submit]'); pg.wait_for_timeout(400)
        pg.evaluate("window.scrollTo(0, document.querySelector('#contactForm').getBoundingClientRect().top + window.scrollY - 120)"); pg.wait_for_timeout(300)
        pg.screenshot(path=f'shots/{tag}-q-contact-errors.png',clip={'x':0,'y':0,'width':width,'height':900}); pg.close()
        pg=ctx.new_page(); pg.goto('http://127.0.0.1:8124/coverage/',wait_until='networkidle'); pg.wait_for_timeout(800)
        pg.click('button[data-filter="europe"]'); pg.wait_for_timeout(500)
        pg.evaluate("window.scrollTo(0, document.querySelector('.filters').getBoundingClientRect().top + window.scrollY - 160)"); pg.wait_for_timeout(300)
        pg.screenshot(path=f'shots/{tag}-q-coverage-filter.png',clip={'x':0,'y':0,'width':width,'height':900}); pg.close()
        if tag=="desk":
            pg=ctx.new_page(); pg.goto('http://127.0.0.1:8124/',wait_until='networkidle'); pg.wait_for_timeout(600)
            pg.hover('.has-sub'); pg.wait_for_timeout(400)
            pg.screenshot(path='shots/desk-q-dropdown.png',clip={'x':0,'y':0,'width':1440,'height':400}); pg.close()
        else:
            pg=ctx.new_page(); pg.goto('http://127.0.0.1:8124/',wait_until='networkidle'); pg.wait_for_timeout(600)
            pg.click('#navToggle'); pg.wait_for_timeout(700)
            pg.screenshot(path='shots/mob-q-menu.png',clip={'x':0,'y':0,'width':390,'height':900})
            pg.click('.sub__toggle'); pg.wait_for_timeout(400)
            pg.screenshot(path='shots/mob-q-menu-sub.png',clip={'x':0,'y':0,'width':390,'height':900}); pg.close()
        ctx.close()
    b.close()
print("JS errors:",errors or "none"); print("console:",console or "none")
