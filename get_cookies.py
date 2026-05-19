"""
ローカルで一度だけ実行してnote.comのセッションクッキーを取得するスクリプト。
取得したJSON文字列をGitHub Secrets の NOTE_COOKIES に設定してください。
"""
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # ブラウザを表示
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://note.com/login")
    print("ブラウザでnote.comにログインしてください。ログイン完了後、Enterを押してください...")
    input()

    cookies = context.cookies()
    print("\n--- 以下のJSON文字列をGitHub Secrets の NOTE_COOKIES に設定 ---")
    print(json.dumps(cookies))
    browser.close()
