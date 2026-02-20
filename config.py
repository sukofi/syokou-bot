"""
設定管理モジュール
環境変数から設定を読み込み、アプリケーション全体で使用する設定を管理します。
"""
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（エラーが発生しても続行）
try:
    load_dotenv()
except (PermissionError, IOError) as e:
    # .envファイルへのアクセス権限がない場合や読み取りエラーの場合
    # 環境変数が既に設定されている場合はそのまま使用
    print(f"警告: .envファイルの読み込みに失敗しました: {e}")
    print("環境変数が直接設定されている場合はそのまま使用します。")


class Config:
    """アプリケーション設定クラス"""
    
    # Discord Bot設定
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
    
    # Gemini API設定
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Google Sheets設定
    GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "service_account.json")
    
    # 管理者DiscordユーザーID（プレースホルダー）
    ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0")) if os.getenv("ADMIN_USER_ID", "0").isdigit() else 0
    
    # スプレッドシートのシート名（デフォルト値、環境変数で上書き可能）
    SHEET_NAME_OUTLINE = os.getenv("SHEET_NAME_OUTLINE", "構成案")
    SHEET_NAME_KEYWORDS = os.getenv("SHEET_NAME_KEYWORDS", "KWリスト")
    SHEET_NAME_INTENT = os.getenv("SHEET_NAME_INTENT", "検索意図")
    SHEET_NAME_COMPETITORS = os.getenv("SHEET_NAME_COMPETITORS", "競合データ")
    
    @classmethod
    def validate(cls) -> bool:
        """
        必須設定が揃っているか検証
        
        Returns:
            bool: 必須設定が全て揃っている場合True
        """
        required_settings = [
            ("DISCORD_BOT_TOKEN", cls.DISCORD_BOT_TOKEN),
            ("GEMINI_API_KEY", cls.GEMINI_API_KEY),
            ("ADMIN_USER_ID", cls.ADMIN_USER_ID),
        ]
        
        missing = [name for name, value in required_settings if not value]
        
        if missing:
            print(f"警告: 以下の必須設定が不足しています: {', '.join(missing)}")
            return False
        
        return True
