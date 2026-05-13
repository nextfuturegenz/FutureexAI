# exon/api/ui/serve_ui.py
# Author: Ashish Pal
# Purpose: Serve the chat UI by combining HTML, CSS, and JS files.

import os

_UI_DIR = os.path.dirname(__file__)

async def serve_ui():
    """Read HTML, inline CSS and JS, return complete page."""
    # Read HTML
    html_path = os.path.join(_UI_DIR, "index.html")
    with open(html_path, "r") as f:
        html = f.read()
    
    # Inline CSS
    css_path = os.path.join(_UI_DIR, "style.css")
    with open(css_path, "r") as f:
        css = f.read()
    html = html.replace(
        '<link rel="stylesheet" href="/ui/style.css">',
        f"<style>\n{css}\n</style>"
    )
    
    # Inline JS
    js_path = os.path.join(_UI_DIR, "script.js")
    with open(js_path, "r") as f:
        js = f.read()
    html = html.replace(
        '<script src="/ui/script.js"></script>',
        f"<script>\n{js}\n</script>"
    )
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html, status_code=200)