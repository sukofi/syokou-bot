"""
Gemini APIで利用可能なモデルを確認するスクリプト
"""
import google.generativeai as genai
from config import Config

def list_available_models():
    """利用可能なモデルをリストアップ"""
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        print("=" * 60)
        print("利用可能なGeminiモデルを確認中...")
        print("=" * 60)
        
        # 利用可能なモデルを取得
        models = genai.list_models()
        
        print("\n利用可能なモデル:")
        print("-" * 60)
        
        available_models = []
        for model in models:
            # generateContentをサポートするモデルのみ表示
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.replace('models/', '')
                available_models.append(model_name)
                print(f"  ✅ {model_name}")
        
        print("-" * 60)
        print(f"\n合計: {len(available_models)}個のモデルが利用可能です")
        print("\n推奨モデル:")
        if 'gemini-1.5-flash' in available_models:
            print("  - gemini-1.5-flash (高速で低コスト)")
        if 'gemini-1.5-pro' in available_models:
            print("  - gemini-1.5-pro (高品質)")
        if 'gemini-pro' in available_models:
            print("  - gemini-pro (標準)")
        
        return available_models
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return []

if __name__ == "__main__":
    list_available_models()
