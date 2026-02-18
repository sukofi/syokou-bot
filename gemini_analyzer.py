"""
Gemini API分析モジュール
Google SheetsのデータをGemini APIに送信し、SEO分析レポートを生成します。
"""
import google.generativeai as genai
from typing import Dict
from datetime import datetime
from config import Config


class GeminiAnalyzer:
    """Gemini APIを使用したSEO分析クラス"""
    
    def __init__(self):
        """初期化：Gemini APIを設定"""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-pro',
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

重要な指示：
- 良い点や評価できる箇所へのコメントは一切不要です
- 修正が必要な箇所のみを指摘してください
- 問題がない場合は「修正箇所なし」と簡潔に記載してください
- 日付に関する分析を行う際は、必ず提供された「現在の日時」を基準として判断してください
- スプレッドシート内の日付や時期的な表現を評価する際は、現在の日付を参照して適切性を判断してください

レポートはMarkdown形式で出力し、以下の形式に厳密に従ってください：

```
判定: 合格 / 要修正 / 不合格

## [見出しタイトル1]
修正内容の説明

## [見出しタイトル2]
修正内容の説明
```

形式のルール：
- 各修正箇所は「## 見出しタイトル」で始める
- 見出しタイトルは、修正が必要な具体的な箇所や問題点を簡潔に表現する（例：「## H2見出し「〇〇」の検索意図との不一致」）
- 見出しの下に、その箇所の修正内容を具体的に記載する
- 複数の修正箇所がある場合は、それぞれを「## 見出しタイトル」で区切る
- 見出しタイトルと修正内容を明確に分けて記載する

コメントの文体：
- すべてのコメントは「ですます調」で記載してください
- 修正指示は「〜してください」「〜することをおすすめします」などの丁寧な表現を使用してください
- 構成作成者へのコメントとして、分かりやすく丁寧に伝えることを心がけてください
- 例：「この見出しは検索意図と一致していません。より具体的な内容に修正してください。」
- 例：「キーワードの配置が不自然です。自然な文章になるよう調整することをおすすめします。」

簡潔で実用的なフィードバックを提供してください。"""
    
    def _format_sheets_data(self, sheets_data: Dict[str, str]) -> str:
        """
        シートデータをプロンプト用に整形
        
        Args:
            sheets_data: シート名をキー、内容を値とする辞書
            
        Returns:
            str: 整形されたテキスト
        """
        # 現在の日付を取得
        current_date = datetime.now().strftime('%Y年%m月%d日')
        current_datetime = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        
        formatted = f"=== 分析日時 ===\n現在の日時: {current_datetime}\n現在の日付: {current_date}\n\n"
        formatted += "=== SEO構成案データ ===\n\n"
        
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
