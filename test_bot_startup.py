"""
Bot起動テストスクリプト
設定の検証とBotの初期化をテストします。
"""
import sys
import asyncio
import discord
from config import Config
from sheets_reader import SheetsReader
from gemini_analyzer import GeminiAnalyzer

def test_config():
    """設定の検証"""
    print("=" * 50)
    print("設定検証")
    print("=" * 50)
    
    if not Config.validate():
        print("❌ 設定検証に失敗しました")
        return False
    
    print("✅ 設定検証: 成功")
    print(f"  - DISCORD_BOT_TOKEN: {'✅ 設定済み' if Config.DISCORD_BOT_TOKEN else '❌ 未設定'}")
    print(f"  - GEMINI_API_KEY: {'✅ 設定済み' if Config.GEMINI_API_KEY else '❌ 未設定'}")
    print(f"  - ADMIN_USER_ID: {Config.ADMIN_USER_ID}")
    print(f"  - GOOGLE_SERVICE_ACCOUNT_JSON: {Config.GOOGLE_SERVICE_ACCOUNT_JSON}")
    return True

def test_sheets_reader():
    """SheetsReaderの初期化テスト"""
    print("\n" + "=" * 50)
    print("SheetsReader初期化テスト")
    print("=" * 50)
    
    try:
        reader = SheetsReader()
        print("✅ SheetsReaderの初期化に成功しました")
        return True
    except FileNotFoundError as e:
        print(f"❌ エラー: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False

def test_gemini_analyzer():
    """GeminiAnalyzerの初期化テスト"""
    print("\n" + "=" * 50)
    print("GeminiAnalyzer初期化テスト")
    print("=" * 50)
    
    try:
        analyzer = GeminiAnalyzer()
        print("✅ GeminiAnalyzerの初期化に成功しました")
        return True
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False

async def test_discord_connection():
    """Discord接続テスト"""
    print("\n" + "=" * 50)
    print("Discord接続テスト")
    print("=" * 50)
    
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    try:
        @client.event
        async def on_ready():
            print(f"✅ Discord接続に成功しました")
            print(f"  - Bot名: {client.user.name}")
            print(f"  - Bot ID: {client.user.id}")
            await client.close()
        
        print("Discordに接続中...")
        await client.start(Config.DISCORD_BOT_TOKEN)
        
    except discord.LoginFailure:
        print("❌ Discord Botのログインに失敗しました。トークンを確認してください。")
        return False
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False
    
    return True

async def main():
    """メインテスト実行"""
    print("\n" + "=" * 50)
    print("SEO Discord Bot 起動テスト")
    print("=" * 50 + "\n")
    
    results = []
    
    # 設定検証
    results.append(("設定検証", test_config()))
    
    # SheetsReaderテスト
    results.append(("SheetsReader", test_sheets_reader()))
    
    # GeminiAnalyzerテスト
    results.append(("GeminiAnalyzer", test_gemini_analyzer()))
    
    # Discord接続テスト
    results.append(("Discord接続", await test_discord_connection()))
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("テスト結果サマリー")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"  {name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ すべてのテストが成功しました！Botを起動できます。")
        print("\nBotを起動するには、以下のコマンドを実行してください:")
        print("  python3 bot.py")
    else:
        print("❌ 一部のテストが失敗しました。上記のエラーを確認してください。")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
