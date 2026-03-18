#!/bin/bash
# Bot起動スクリプト（nohup使用）
# ログは常に ~/syokou-bot.log に出力（launchdと同じ場所）

cd /Users/sukofi/Desktop/syokou-bot
nohup python bot.py >> "$HOME/syokou-bot.log" 2>> "$HOME/syokou-bot-error.log" &
echo $! > bot.pid
echo "Botを起動しました。PID: $(cat bot.pid)"
echo "ログ確認: tail -f $HOME/syokou-bot.log  または  ./log.sh"
echo "停止: kill \$(cat bot.pid)"
