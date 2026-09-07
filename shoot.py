#!/usr/bin/env python3
"""Usage: python3 shoot.py <width> <path> <out.png> [scrollY] [clipH] [fullpage]"""
import sys, threading, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

def serve():
    class Quiet(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k): super().__init__(*a, directory='dist', **k)
        def log_message(self, *a): pass
    srv = ThreadingHTTPServer(('127.0.0.1', 8123), Quiet)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv

def main():
    width = int(sys.argv[1]); path = sys.argv[2]; out = sys.argv[3]
    scroll = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    clip_h = int(sys.argv[5]) if len(sys.argv) > 5 else 900
    full = len(sys.argv) > 6 and sys.argv[6] == 'full'
    serve()
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': width, 'height': 900}, device_scale_factor=1)
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('http://127.0.0.1:8123' + path, wait_until='networkidle')
        pg.wait_for_timeout(2200)
        if scroll:
            pg.evaluate(f"window.scrollTo(0, {scroll})"); pg.wait_for_timeout(500)
        if full:
            pg.screenshot(path=out, full_page=True)
        else:
            pg.screenshot(path=out, clip={'x': 0, 'y': 0, 'width': width, 'height': clip_h})
        if errs: print('JS errors:', errs)
        b.close()

if __name__ == '__main__':
    main()
