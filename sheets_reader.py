"""
Google Sheets読み取りモジュール
スプレッドシートのURLからデータを抽出し、テキスト形式で整形して返却します。
"""
import re
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, Optional
from config import Config


class SheetsReader:
    """Google Sheets読み取りクラス"""
    
    def __init__(self):
        """初期化：サービスアカウント認証を設定"""
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            creds = Credentials.from_service_account_file(
                Config.GOOGLE_SERVICE_ACCOUNT_JSON,
                scopes=scopes
            )
            self.client = gspread.authorize(creds)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"サービスアカウントJSONファイルが見つかりません: {Config.GOOGLE_SERVICE_ACCOUNT_JSON}"
            )
        except Exception as e:
            raise Exception(f"Google Sheets認証エラー: {str(e)}")
    
    def extract_spreadsheet_id(self, url: str) -> Optional[str]:
        """
        URLからスプレッドシートIDを抽出
        
        Args:
            url: GoogleスプレッドシートのURL
            
        Returns:
            str: スプレッドシートID、抽出できない場合はNone
        """
        # 様々なURL形式に対応
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
            r'/d/([a-zA-Z0-9-_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def read_sheet_data(self, spreadsheet_id: str, sheet_name: str) -> str:
        """
        指定されたシートのデータを読み取り、テキスト形式で整形
        
        Args:
            spreadsheet_id: スプレッドシートID
            sheet_name: シート名
            
        Returns:
            str: 整形されたテキストデータ
        """
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            sheet = spreadsheet.worksheet(sheet_name)
            
            # 全データを取得
            all_values = sheet.get_all_values()
            
            if not all_values:
                return f"[{sheet_name}] シートは空です。\n"
            
            # テキスト形式に整形
            lines = []
            for row in all_values:
                # 空行をスキップ
                if not any(cell.strip() for cell in row):
                    continue
                # 行を結合（空セルは空白として扱う）
                line = " | ".join(cell.strip() if cell.strip() else "" for cell in row)
                lines.append(line)
            
            result = f"=== {sheet_name} ===\n" + "\n".join(lines) + "\n\n"
            return result
            
        except gspread.exceptions.WorksheetNotFound:
            return f"[{sheet_name}] シートが見つかりませんでした。\n\n"
        except Exception as e:
            return f"[{sheet_name}] 読み取りエラー: {str(e)}\n\n"
    
    def read_all_sheets(self, url: str) -> Dict[str, str]:
        """
        スプレッドシートの全シートを読み取り
        
        Args:
            url: GoogleスプレッドシートのURL
            
        Returns:
            Dict[str, str]: シート名をキー、内容を値とする辞書
            
        Raises:
            ValueError: URLが無効な場合
            Exception: スプレッドシートへのアクセス権限がない場合
        """
        spreadsheet_id = self.extract_spreadsheet_id(url)
        
        if not spreadsheet_id:
            raise ValueError("無効なスプレッドシートURLです。")
        
        try:
            # 各シートを読み取り
            sheets_data = {}
            
            # 構成案シート
            sheets_data["outline"] = self.read_sheet_data(
                spreadsheet_id, 
                Config.SHEET_NAME_OUTLINE
            )
            
            # KWリストシート
            sheets_data["keywords"] = self.read_sheet_data(
                spreadsheet_id,
                Config.SHEET_NAME_KEYWORDS
            )
            
            # 検索意図シート
            sheets_data["intent"] = self.read_sheet_data(
                spreadsheet_id,
                Config.SHEET_NAME_INTENT
            )
            
            # 競合データシート
            sheets_data["competitors"] = self.read_sheet_data(
                spreadsheet_id,
                Config.SHEET_NAME_COMPETITORS
            )
            
            return sheets_data
            
        except gspread.exceptions.SpreadsheetNotFound:
            raise Exception("スプレッドシートが見つかりません。URLを確認してください。")
        except gspread.exceptions.APIError as e:
            if "PERMISSION_DENIED" in str(e):
                raise Exception("スプレッドシートへのアクセス権限がありません。サービスアカウントに共有設定を行ってください。")
            raise Exception(f"Google Sheets APIエラー: {str(e)}")
        except Exception as e:
            raise Exception(f"スプレッドシート読み取りエラー: {str(e)}")
