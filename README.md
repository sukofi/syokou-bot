# SEO構成案 自動検閲Discord Bot

Discordに投稿されたGoogleスプレッドシートの構成案を、Gemini APIを用いて自動分析し、管理者にのみDMで詳細な添削レポートを送信するBotです。

## 機能

- DiscordチャンネルでGoogleスプレッドシートのURLを自動検知
- スプレッドシートから4つのシート（構成案、KWリスト、検索意図、競合データ）を自動読み取り
- Gemini API（gemini-1.5-pro）による厳格なSEO分析
- 管理者へのDMで分析レポートを自動送信

## 必要なもの

1. **Discord Bot トークン**
   - [Discord Developer Portal](https://discord.com/developers/applications)でBotを作成
   - Botに「メッセージの内容を読む」権限を付与

2. **Gemini API キー**
   - [Google AI Studio](https://makersuite.google.com/app/apikey)でAPIキーを取得

3. **Googleサービスアカウント**
   - [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
   - サービスアカウントを作成し、JSONキーをダウンロード
   - スプレッドシートにサービスアカウントのメールアドレスを共有設定

4. **管理者のDiscordユーザーID**
   - 自分のDiscordユーザーID（18桁の数字）を取得

## セットアップ手順

### 1. リポジトリのクローンまたはダウンロード

```bash
cd seo-discord-bot
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成：

```bash
cp .env.example .env
```

`.env`ファイルを編集し、以下の情報を設定：

```env
# Discord Bot設定
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Gemini API設定
GEMINI_API_KEY=your_gemini_api_key_here

# Google Sheets設定
GOOGLE_SERVICE_ACCOUNT_JSON=service_account.json

# 管理者DiscordユーザーID（18桁の数字）
ADMIN_USER_ID=your_discord_user_id_here

# スプレッドシートのシート名（オプション、デフォルト値を使用する場合は空欄でも可）
SHEET_NAME_OUTLINE=構成案
SHEET_NAME_KEYWORDS=KWリスト
SHEET_NAME_INTENT=検索意図
SHEET_NAME_COMPETITORS=競合データ
```

### 4. サービスアカウントJSONファイルの配置

Google Cloud ConsoleからダウンロードしたJSONキーファイルを、プロジェクトルートに配置します。
ファイル名は`.env`の`GOOGLE_SERVICE_ACCOUNT_JSON`で指定した名前に合わせてください（デフォルト: `service_account.json`）。

### 5. スプレッドシートの共有設定

分析対象のGoogleスプレッドシートに、サービスアカウントのメールアドレス（JSONファイル内の`client_email`）を共有設定してください。
権限は「閲覧者」で十分です。

## 使用方法

### Botの起動

```bash
python bot.py
```

### 動作確認

1. Discordサーバーで、Botが参加しているチャンネルにGoogleスプレッドシートのURLを投稿
2. Botが自動的にURLを検知し、分析を開始
3. 分析完了後、管理者（`ADMIN_USER_ID`で指定したユーザー）にDMでレポートが送信されます

### スプレッドシートの形式

Botは以下の4つのシートを読み取ります：

1. **構成案**（デフォルト名: `構成案`）
   - SEO記事の見出し（H2/H3）構成

2. **KWリスト**（デフォルト名: `KWリスト`）
   - ターゲットキーワード、関連キーワード

3. **検索意図**（デフォルト名: `検索意図`）
   - ユーザーの悩み、ニーズ

4. **競合データ**（デフォルト名: `競合データ`）
   - 競合他社の見出し一覧

シート名が異なる場合は、`.env`ファイルで`SHEET_NAME_*`を設定してください。

## 分析レポートの内容

Gemini APIが以下の4つの観点から分析を行います：

1. **検索意図との不一致**
   - ユーザーの悩みやニーズに適切に答えているか

2. **競合に対する網羅性**
   - 競合他社と比較して、勝てる見出しになっているか

3. **キーワードの適切な配置**
   - ターゲットKWや関連KWが自然に配置されているか

4. **独自性の欠如**
   - 他サイトの劣化コピーになっていないか

レポートはMarkdown形式で、合格/要修正/不合格の判定と詳細な評価が含まれます。

## エラーハンドリング

- **スプレッドシートへのアクセス権限がない場合**: チャンネルにエラーメッセージを送信
- **管理者のDMが閉じている場合**: ログにエラーを出力
- **解析失敗時**: 投稿者に通知を送信（DMが開いている場合）
- **無効なURL形式**: スキップしてログに出力

## トラブルシューティング

### Botがメッセージを検知しない

- Botに「メッセージの内容を読む」権限があるか確認
- `intents.message_content = True`が設定されているか確認（コード内で設定済み）

### スプレッドシートが読み取れない

- サービスアカウントにスプレッドシートの共有設定がされているか確認
- JSONファイルのパスが正しいか確認
- シート名が`.env`の設定と一致しているか確認

### 管理者にDMが届かない

- `ADMIN_USER_ID`が正しいか確認（18桁の数字）
- 管理者のDM設定が開いているか確認
- ログを確認してエラー内容を確認

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 注意事項

- このBotは機密情報（APIキー、トークンなど）を扱います。`.env`ファイルとサービスアカウントJSONファイルは絶対にGitにコミットしないでください
- Gemini APIの使用には料金が発生する場合があります。APIの利用規約と料金体系を確認してください
- Discord Botの利用規約を遵守してください
