#!/bin/bash
# ログを常時ターミナルから確認する（tail -f）
LOG="$HOME/syokou-bot.log"
ERR="$HOME/syokou-bot-error.log"

if [ "$1" = "-e" ] || [ "$1" = "--error" ]; then
    echo "エラーログを表示中: $ERR (Ctrl+C で終了)"
    tail -f "$ERR"
elif [ "$1" = "-a" ] || [ "$1" = "--all" ]; then
    echo "標準出力とエラーを表示中 (Ctrl+C で終了)"
    tail -f "$LOG" "$ERR"
else
    echo "ログを表示中: $LOG (Ctrl+C で終了)"
    echo "オプション: -e エラーのみ  -a 両方"
    tail -f "$LOG"
fi
