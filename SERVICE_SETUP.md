# Bot常時起動の設定方法

macOSでBotを常時起動させる方法をいくつか用意しました。

## 方法1: launchd（推奨 - システムサービスとして起動）

macOSの標準サービス管理システムを使用します。システム起動時に自動で起動し、クラッシュ時も自動再起動します。

### セットアップ手順

1. **plistファイルを配置**:
```bash
cd /Users/sukofi/Desktop/syokou-bot
cp com.syokou.bot.plist ~/Library/LaunchAgents/
```

2. **サービスを読み込む（新しいmacOS）**:
```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.syokou.bot.plist
```

古いmacOSの場合は:
```bash
launchctl load ~/Library/LaunchAgents/com.syokou.bot.plist
```

3. **サービスを開始（必要に応じて）**:
```bash
launchctl kickstart gui/$(id -u)/com.syokou.bot
```

### 管理コマンド（新しいmacOS）

- **起動**: `launchctl kickstart gui/$(id -u)/com.syokou.bot`
- **停止**: `launchctl bootout gui/$(id -u)/com.syokou.bot`
- **再起動**: `launchctl bootout gui/$(id -u)/com.syokou.bot` のあと `sleep 2` してから `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.syokou.bot.plist`
- **状態確認**: `launchctl list | grep syokou`
- **アンロード（削除）**: `launchctl bootout gui/$(id -u)/com.syokou.bot`

### plistを更新したあと（コピー＆ペースト用・コメントなし）

必ず **1. 停止** から順に実行してください。すでに読み込まれていると `bootstrap` が「Bootstrap failed: 5: Input/output error」になることがあります。

```bash
launchctl bootout gui/$(id -u)/com.syokou.bot 2>/dev/null
sleep 2
cp /Users/sukofi/Desktop/syokou-bot/com.syokou.bot.plist ~/Library/LaunchAgents/
plutil -lint ~/Library/LaunchAgents/com.syokou.bot.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.syokou.bot.plist
launchctl list | grep syokou
```

まだ「Bootstrap failed: 5」が出る場合は、従来の `load` を試す:

```bash
launchctl load ~/Library/LaunchAgents/com.syokou.bot.plist
launchctl list | grep syokou
```

### Bootstrap failed: 5 が続く場合

1. **拡張属性を削除してから再試行**（コピー時に付与された属性が原因のことがあります）:
```bash
launchctl bootout gui/$(id -u)/com.syokou.bot 2>/dev/null
xattr -c ~/Library/LaunchAgents/com.syokou.bot.plist
cp /Users/sukofi/Desktop/syokou-bot/com.syokou.bot.plist ~/Library/LaunchAgents/
xattr -c ~/Library/LaunchAgents/com.syokou.bot.plist
sleep 2
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.syokou.bot.plist
launchctl list | grep syokou
```

2. **launchd が使えない場合の代替: ログイン時に実行**  
   システム設定 → 一般 → ログイン項目 → 「+」で「起動時に実行する項目」に追加:
   - 項目: **ターミナル.app** を選ぶ  
   - または、`/Users/sukofi/Desktop/syokou-bot/start_bot.sh` を実行するように AppleScript や Automator で「アプリ」を作成し、そのアプリをログイン項目に追加する。

   手動でログイン後に起動する場合:
```bash
/Users/sukofi/Desktop/syokou-bot/start_bot.sh
```

### トラブルシューティング（エラーコード78 / service inactive）

- **状態**: `launchctl list` で `-	78	com.syokou.bot` と表示され、サービスが起動しない場合
- **対処1**: 手動で起動を試す  
  `launchctl kickstart gui/$(id -u)/com.syokou.bot`  
  ログイン後にこのコマンドを実行すると起動することがあります。
- **対処2**: plistを再配置して再読み込み  
  「plistを更新したあと」の手順を実行し、最新の plist を使っているか確認する。
- **対処3**: ログ確認  
  下記「ログの確認」のパスで起動失敗の原因を確認する。

### ログの確認（常時ターミナルから確認可能）

ログは常にホーム直下に出力されます（launchd / start_bot.sh 共通）。

- **標準出力をリアルタイム表示**: `tail -f ~/syokou-bot.log`
- **エラーのみ表示**: `tail -f ~/syokou-bot-error.log`
- **プロジェクトの log.sh を使う場合**:
```bash
cd /Users/sukofi/Desktop/syokou-bot
./log.sh          # 標準出力
./log.sh -e       # エラーのみ
./log.sh -a       # 両方
```
- **3つのプログラム（syokou-bot / link-bot / seo-discord-bot）のログをまとめて見る**:
```bash
cd /Users/sukofi/Desktop/syokou-bot
./logs_all.sh
```

---

## 方法2: nohup（簡単なバックグラウンド実行）

シンプルにバックグラウンドで実行する方法です。

### 起動

```bash
cd /Users/sukofi/Desktop/syokou-bot
./start_bot.sh
```

### 停止

```bash
./stop_bot.sh
```

### ログの確認

```bash
tail -f ~/syokou-bot.log
```
または `./log.sh`（プロジェクト内で実行）

---

## 方法3: screen（セッション管理）

ターミナルセッションを維持したまま実行できます。

### 起動

```bash
cd /Users/sukofi/Desktop/syokou-bot
screen -S syokou-bot python bot.py
```

### セッションから離脱

`Ctrl + A` を押してから `D` を押す

### セッションに再接続

```bash
screen -r syokou-bot
```

### セッション一覧

```bash
screen -ls
```

### 停止

セッション内で `Ctrl + C` を押すか、セッションをkill:
```bash
screen -X -S syokou-bot quit
```

---

## 方法4: tmux（セッション管理）

screenと同様の機能を提供します。

### 起動

```bash
cd /Users/sukofi/Desktop/syokou-bot
tmux new-session -d -s syokou-bot 'python bot.py'
```

### セッションに接続

```bash
tmux attach-session -t syokou-bot
```

### セッションから離脱

`Ctrl + B` を押してから `D` を押す

### セッション一覧

```bash
tmux list-sessions
```

### 停止

セッション内で `Ctrl + C` を押すか、セッションをkill:
```bash
tmux kill-session -t syokou-bot
```

---

## 推奨設定

- **本番環境**: launchd（方法1）- システム起動時に自動起動、クラッシュ時も自動再起動
- **開発・テスト**: screen/tmux（方法3/4）- ログを確認しながら実行
- **簡単な運用**: nohup（方法2）- シンプルで手軽

---

## 注意事項

- Pythonのパス（`/Users/sukofi/opt/anaconda3/bin/python`）は環境に合わせて変更してください
- プロジェクトのパス（`/Users/sukofi/Desktop/syokou-bot`）も環境に合わせて変更してください
- `.env`ファイルが正しく配置されていることを確認してください
