# 3つのプログラムのログ確認

## プロジェクト概要

| プログラム | ディレクトリ | 役割 | 標準ログ | エラーログ |
|-----------|--------------|------|----------|------------|
| **syokou-bot** | `~/Desktop/syokou-bot` | 初稿案チェック（Googleドキュメント） | `~/syokou-bot.log` | `~/syokou-bot-error.log` |
| **link-bot-main** | `~/Desktop/link-bot-main` | 内部リンク提案Bot | `~/Desktop/link-bot-main/link_bot.log` | `~/Desktop/link-bot-main/link_bot_error.log` |
| **seo-discord-bot** | `~/Desktop/seo-discord-bot` | スプレッドシート構成案チェック | `~/Desktop/seo-discord-bot/bot.log` | `~/Desktop/seo-discord-bot/bot_error.log` |

## 確認結果（要約）

- **seo-discord-bot**: `bot.py` + SheetsReader + GeminiAnalyzer。スプレッドシートURL検知で分析。ログは Python の logging（標準出力）→ launchd/起動方法で上記ファイルへ。
- **link-bot-main**: `link_bot.py` + `start_link_bot.sh`。`/` コマンドで内部リンク提案。設定は `config/settings.yaml` と `.env`。既に `link_bot.log` / `link_bot_error.log` が存在。
- **logs_all.sh**: 上記3つの標準ログを `tail -f` で同時表示。パスは上表のとおりで問題なし。

## 全ログをまとめて見る

```bash
cd /Users/sukofi/Desktop/syokou-bot
./logs_all.sh
```

エラーまで含めたい場合は、各プロジェクトで:

```bash
tail -f ~/syokou-bot-error.log
tail -f ~/Desktop/link-bot-main/link_bot_error.log
tail -f ~/Desktop/seo-discord-bot/bot_error.log
```
