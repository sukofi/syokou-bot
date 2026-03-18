#!/bin/bash
# Bot停止スクリプト

if [ -f /Users/sukofi/Desktop/syokou-bot/bot.pid ]; then
    PID=$(cat /Users/sukofi/Desktop/syokou-bot/bot.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "Botを停止しました (PID: $PID)"
        rm /Users/sukofi/Desktop/syokou-bot/bot.pid
    else
        echo "Botは実行されていません"
        rm /Users/sukofi/Desktop/syokou-bot/bot.pid
    fi
else
    echo "PIDファイルが見つかりません"
    echo "実行中のプロセスを検索中..."
    pkill -f "python bot.py"
    echo "Botプロセスを停止しました"
fi
