import os
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "reports")

os.makedirs(OUTPUT_DIR, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def generate_report_image(student, log):
    template = env.get_template("daily_report.html")
    html = template.render(student=student, log=log)

    html_path = os.path.join(OUTPUT_DIR, f"log_{log.id}.html")
    img_path = os.path.join(OUTPUT_DIR, f"log_{log.id}.png")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # viewport 높이를 작게 설정 (내용에 맞게 자동으로 늘어남)
        page = browser.new_page(viewport={"width": 900, "height": 800})

        file_url = "file:///" + html_path.replace("\\", "/")
        page.goto(file_url)

        page.wait_for_load_state("networkidle")
        # full_page=True로 하면 내용에 맞게 이미지 높이가 자동 조정됨
        page.screenshot(path=img_path, full_page=True)

        browser.close()

    return f"/static/reports/log_{log.id}.png"
