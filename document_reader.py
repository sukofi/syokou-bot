"""
Google Docs読み取りモジュール
GoogleドキュメントのURLから内容を抽出し、テキスト形式で整形して返却します。
"""
import os
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import Optional
from config import Config


class DocumentReader:
    """Google Docs読み取りクラス"""
    
    def __init__(self):
        """初期化：サービスアカウント認証を設定"""
        try:
            scopes = [
                'https://www.googleapis.com/auth/documents.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            # ファイルパスを絶対パスに変換
            json_path = Config.GOOGLE_SERVICE_ACCOUNT_JSON
            
            # 絶対パスでない場合、複数のパスを試す
            if not os.path.isabs(json_path):
                # 試すパスのリスト
                possible_paths = [
                    # プロジェクトルート（document_reader.pyと同じディレクトリ）
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), json_path),
                    # 現在の作業ディレクトリ
                    os.path.join(os.getcwd(), json_path),
                    # 相対パスのまま（既にプロジェクトルートにいる場合）
                    json_path
                ]
                
                # 存在するパスを探す
                json_path = None
                for path in possible_paths:
                    if os.path.exists(path) and os.path.isfile(path):
                        json_path = os.path.abspath(path)
                        break
                
                # どのパスでも見つからなかった場合
                if json_path is None:
                    raise FileNotFoundError(
                        f"サービスアカウントJSONファイルが見つかりません: {Config.GOOGLE_SERVICE_ACCOUNT_JSON}\n"
                        f"試したパス: {', '.join([os.path.abspath(p) for p in possible_paths])}\n"
                        f"現在の作業ディレクトリ: {os.getcwd()}"
                    )
            else:
                # 絶対パスの場合、存在確認
                if not os.path.exists(json_path) or not os.path.isfile(json_path):
                    raise FileNotFoundError(
                        f"サービスアカウントJSONファイルが見つかりません: {json_path}"
                    )
                json_path = os.path.abspath(json_path)
            
            creds = Credentials.from_service_account_file(
                json_path,
                scopes=scopes
            )
            self.docs_service = build('docs', 'v1', credentials=creds)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise Exception(f"Google Docs認証エラー: {str(e)}")
    
    def extract_document_id(self, url: str) -> Optional[str]:
        """
        URLからドキュメントIDを抽出
        
        Args:
            url: GoogleドキュメントのURL
            
        Returns:
            str: ドキュメントID、抽出できない場合はNone
        """
        # 様々なURL形式に対応
        patterns = [
            r'/document/d/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
            r'/d/([a-zA-Z0-9-_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def read_document(self, url: str) -> str:
        """
        Googleドキュメントの内容を読み取り、テキスト形式で整形
        
        Args:
            url: GoogleドキュメントのURL
            
        Returns:
            str: 整形されたテキストデータ
            
        Raises:
            ValueError: URLが無効な場合
            Exception: ドキュメントへのアクセス権限がない場合
        """
        document_id = self.extract_document_id(url)
        
        if not document_id:
            raise ValueError("無効なGoogleドキュメントURLです。")
        
        try:
            # ドキュメントを取得
            document = self.docs_service.documents().get(documentId=document_id).execute()
            
            # ドキュメントの内容を抽出
            content = document.get('body', {}).get('content', [])
            
            if not content:
                return "ドキュメントは空です。\n"
            
            # テキストを抽出
            text_parts = []
            self._extract_text_from_elements(content, text_parts)
            
            result = "\n".join(text_parts)
            return result if result.strip() else "ドキュメントの内容を読み取れませんでした。\n"
            
        except Exception as e:
            error_str = str(e)
            if "PERMISSION_DENIED" in error_str or "403" in error_str:
                raise Exception("ドキュメントへのアクセス権限がありません。サービスアカウントに共有設定を行ってください。")
            elif "404" in error_str or "NOT_FOUND" in error_str:
                raise Exception("ドキュメントが見つかりません。URLを確認してください。")
            else:
                raise Exception(f"ドキュメント読み取りエラー: {str(e)}")
    
    def _extract_text_from_elements(self, elements, text_parts):
        """
        ドキュメント要素からテキストを再帰的に抽出
        
        Args:
            elements: ドキュメントの要素リスト
            text_parts: テキストを格納するリスト
        """
        for element in elements:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                para_text = self._extract_text_from_paragraph(paragraph)
                if para_text.strip():
                    text_parts.append(para_text)
            elif 'table' in element:
                # テーブルの処理（必要に応じて実装）
                table = element['table']
                table_text = self._extract_text_from_table(table)
                if table_text.strip():
                    text_parts.append(table_text)
            elif 'sectionBreak' in element:
                # セクション区切りの処理
                text_parts.append("\n")
    
    def _extract_text_from_paragraph(self, paragraph) -> str:
        """
        段落からテキストを抽出
        
        Args:
            paragraph: 段落要素
            
        Returns:
            str: 抽出されたテキスト
        """
        text_parts = []
        elements = paragraph.get('elements', [])
        
        for elem in elements:
            if 'textRun' in elem:
                text_run = elem['textRun']
                text = text_run.get('content', '')
                text_parts.append(text)
        
        return ''.join(text_parts)
    
    def _extract_text_from_table(self, table) -> str:
        """
        テーブルからテキストを抽出
        
        Args:
            table: テーブル要素
            
        Returns:
            str: 抽出されたテキスト
        """
        text_parts = []
        rows = table.get('tableRows', [])
        
        for row in rows:
            row_texts = []
            cells = row.get('tableCells', [])
            
            for cell in cells:
                cell_texts = []
                content = cell.get('content', [])
                for elem in content:
                    if 'paragraph' in elem:
                        para_text = self._extract_text_from_paragraph(elem['paragraph'])
                        cell_texts.append(para_text.strip())
                
                row_texts.append(' | '.join(cell_texts))
            
            if row_texts:
                text_parts.append(' | '.join(row_texts))
        
        return '\n'.join(text_parts) + '\n'
