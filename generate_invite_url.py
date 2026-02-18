"""
Discord Bot招待URL生成スクリプト
BotをDiscordサーバーに追加するための招待URLを生成します。
"""

# Bot ID（テストから取得した値: seo-bot）
# 注意: この値はテスト実行時に取得したBot IDです
# 異なる場合は、Discord Developer Portalで確認してください
BOT_ID = 1473515840099061861

# 必要な権限（パーミッション値）
# Read Messages/View Channels: 1024
# Send Messages: 2048
# Read Message History: 65536
# Use External Emojis: 262144
# 合計: 1024 + 2048 + 65536 + 262144 = 330752
PERMISSIONS = 330752

# スコープ
SCOPES = "bot"

def generate_invite_url():
    """Bot招待URLを生成"""
    url = f"https://discord.com/api/oauth2/authorize?client_id={BOT_ID}&permissions={PERMISSIONS}&scope={SCOPES}"
    return url

if __name__ == "__main__":
    invite_url = generate_invite_url()
    print("=" * 60)
    print("Discord Bot招待URL")
    print("=" * 60)
    print()
    print("以下のURLをブラウザで開いて、Botをサーバーに追加してください:")
    print()
    print(invite_url)
    print()
    print("=" * 60)
    print("手順:")
    print("1. 上記のURLをブラウザで開く")
    print("2. 追加したいDiscordサーバーを選択")
    print("3. 「認証」をクリック")
    print("4. 権限を確認して「認証」をクリック")
    print("5. Botがサーバーに追加されます")
    print("=" * 60)
