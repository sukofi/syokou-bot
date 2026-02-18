"""
Gemini API分析モジュール
Google SheetsのデータをGemini APIに送信し、SEO分析レポートを生成します。
"""
import google.generativeai as genai
from typing import Dict
from config import Config


class GeminiAnalyzer:
    """Gemini APIを使用したSEO分析クラス"""
    
    def __init__(self):
        """初期化：Gemini APIを設定"""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            system_instruction=self._get_system_instruction()
        )
    
    def _get_system_instruction(self) -> str:
        """
        System Instruction（AIの役割設定）を取得
        
        Returns:
            str: SEOディレクターの役割設定
        """
        return """あなたは20年以上の実績を持つ、妥協を許さないSEOディレクターです。
以下の4つの観点から、提供されたSEO構成案を厳しく添削してください：

1. **検索意図との不一致**
   - ユーザーの悩みやニーズに適切に答えているか
   - 検索意図シートの内容と構成案が一致しているか

2. **競合に対する網羅性**
   - 競合他社の見出し構成と比較して、勝てる見出しになっているか
   - 競合データシートの内容を踏まえて、不足している要素はないか

3. **キーワードの適切な配置**
   - ターゲットKWや関連KWが自然に配置されているか
   - 不自然なキーワードの詰め込みがないか

4. **独自性の欠如**
   - 他サイトの劣化コピーになっていないか
   - 独自の価値や視点が含まれているか

レポートはMarkdown形式で出力し、以下の形式に従ってください：
- 判定: 合格 / 要修正 / 不合格
- 各チェック項目ごとの詳細な評価
- 具体的な改善提案

厳格かつ建設的なフィードバックを提供してください。"""
    
    def _format_sheets_data(self, sheets_data: Dict[str, str]) -> str:
        """
        シートデータをプロンプト用に整形
        
        Args:
            sheets_data: シート名をキー、内容を値とする辞書
            
        Returns:
            str: 整形されたテキスト
        """
        formatted = "=== SEO構成案データ ===\n\n"
        
        formatted += sheets_data.get("outline", "")
        formatted += sheets_data.get("keywords", "")
        formatted += sheets_data.get("intent", "")
        formatted += sheets_data.get("competitors", "")
        
        return formatted
    
    def analyze(self, sheets_data: Dict[str, str]) -> str:
        """
        SEO構成案を分析し、レポートを生成
        
        Args:
            sheets_data: シート名をキー、内容を値とする辞書
            
        Returns:
            str: Markdown形式の分析レポート
            
        Raises:
            Exception: Gemini API呼び出しに失敗した場合
        """
        try:
            # シートデータを整形
            prompt = self._format_sheets_data(sheets_data)
            
            # Gemini APIに送信
            response = self.model.generate_content(prompt)
            
            # レスポンスを取得
            if response.text:
                return response.text
            else:
                raise Exception("Gemini APIからのレスポンスが空です。")
                
        except Exception as e:
            raise Exception(f"Gemini API分析エラー: {str(e)}")
