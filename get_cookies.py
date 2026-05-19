"""
Windows の Chrome/Edge で note.com にログインしてクッキーを取得するスクリプト。

手順:
1. Chrome/Edge で https://note.com にアクセスしてログイン
2. F12 → Network タブを開く
3. ページを F5 でリロード
4. 左のリクエスト一覧から "note.com" への任意のリクエストをクリック
5. 右側の "Request Headers" の中の "cookie:" の値を全部コピー
6. このスクリプトを実行して貼り付け → Enter

出力されたJSONを GitHub Secrets の NOTE_COOKIES に設定してください。
"""
import json


def cookie_header_to_json(header: str) -> str:
    cookies = []
    for part in header.split(";"):
        part = part.strip()
        if not part:
            continue
        idx = part.find("=")
        if idx == -1:
            continue
        name = part[:idx].strip()
        value = part[idx + 1:].strip()
        cookies.append({
            "name": name,
            "value": value,
            "domain": "note.com",
            "path": "/",
            "httpOnly": False,
            "secure": True,
            "sameSite": "Lax",
        })
    return json.dumps(cookies)


print("=" * 60)
print("Chrome/Edge の DevTools (F12) → Network タブを開き、")
print("note.com へのリクエストの Request Headers にある")
print('"cookie:" の値を全部コピーして、ここに貼り付けてください。')
print("=" * 60)
print()

cookie_header = input("cookie: ").strip()
result = cookie_header_to_json(cookie_header)

print()
print("=" * 60)
print("以下の JSON を GitHub Secrets の NOTE_COOKIES に設定してください:")
print("=" * 60)
print(result)
