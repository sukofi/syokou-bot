#!/bin/bash
# 3つのプログラムのログをまとめてリアルタイム表示
# syokou-bot / link-bot / seo-discord-bot

SYOKOU="$HOME/syokou-bot.log"
LINK_BOT="/Users/sukofi/Desktop/link-bot-main/link_bot.log"
SEO_BOT="/Users/sukofi/Desktop/seo-discord-bot/bot.log"

FILES=()
[ -f "$SYOKOU"   ] && FILES+=("$SYOKOU")
[ -f "$LINK_BOT" ] && FILES+=("$LINK_BOT")
[ -f "$SEO_BOT"  ] && FILES+=("$SEO_BOT")

if [ ${#FILES[@]} -eq 0 ]; then
    echo "ログファイルが見つかりません。"
    echo "  syokou-bot:       $SYOKOU"
    echo "  link-bot-main:   $LINK_BOT"
    echo "  seo-discord-bot: $SEO_BOT"
    exit 1
fi

echo "表示中: ${FILES[*]}"
echo "Ctrl+C で終了"
echo "---"
tail -f "${FILES[@]}"
