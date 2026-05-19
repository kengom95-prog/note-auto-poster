import os
import sys
import anthropic
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from pytrends.request import TrendReq


def get_trending_topics() -> list[str]:
    pytrends = TrendReq(hl="ja-JP", tz=540)
    df = pytrends.trending_searches(pn="japan")
    return df[0].tolist()[:5]


def generate_article(topics: list[str]) -> tuple[str, str]:
    client = anthropic.Anthropic()

    topics_str = "\n".join(f"- {t}" for t in topics)

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2000,
        system="あなたはnote.comに記事を投稿するライターです。トレンドを踏まえた、読者が思わず読みたくなる記事を書いてください。",
        messages=[
            {
                "role": "user",
                "content": f"""今日の日本のトレンドキーワードを元に、note.com 向けの記事を1つ書いてください。

トレンドキーワード（上位5位）:
{topics_str}

フォーマット（必ずこの形式で出力）:
タイトル: （ここにタイトル）

（ここに本文 800〜1200文字）""",
            }
        ],
    )

    text = message.content[0].text.strip()
    lines = text.split("\n")

    title = lines[0].removeprefix("タイトル:").strip()
    body = "\n".join(lines[2:]).strip()

    return title, body


def post_to_note(title: str, body: str) -> None:
    email = os.environ["NOTE_EMAIL"]
    password = os.environ["NOTE_PASSWORD"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        # ログイン
        page.goto("https://note.com/login?redirectPath=%2F")
        page.wait_for_load_state("networkidle")

        page.fill('input[name="email"]', email)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        if "/login" in page.url:
            raise RuntimeError("ログイン失敗。メール・パスワードを確認してください。")

        # 新規記事作成
        page.goto("https://note.com/notes/new")
        page.wait_for_load_state("networkidle")

        # タイトル入力
        title_selector = '[placeholder="記事タイトル"]'
        page.wait_for_selector(title_selector, timeout=10000)
        page.click(title_selector)
        page.fill(title_selector, title)

        # 本文入力（ProseMirror エディタ）
        page.click(".ProseMirror")
        page.keyboard.press("End")
        # 改行してから本文入力（タイトルとエディタが同じ場合の保険）
        for paragraph in body.split("\n"):
            page.keyboard.type(paragraph)
            page.keyboard.press("Enter")

        # 公開ボタン
        page.click('button:has-text("公開")')

        # 公開設定モーダル → 投稿ボタン
        try:
            page.wait_for_selector('button:has-text("投稿する")', timeout=8000)
            page.click('button:has-text("投稿する")')
        except PlaywrightTimeout:
            # テキストが異なる場合のフォールバック
            page.click('button:has-text("公開する")')

        page.wait_for_load_state("networkidle")
        print(f"投稿完了: {page.url}")

        browser.close()


if __name__ == "__main__":
    print("トレンド取得中...")
    topics = get_trending_topics()
    print(f"トレンド: {topics}")

    print("記事生成中...")
    title, body = generate_article(topics)
    print(f"タイトル: {title}")
    print(f"本文 ({len(body)}文字):\n{body[:200]}...")

    print("note.com に投稿中...")
    post_to_note(title, body)
    print("完了！")
