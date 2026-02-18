"""
Discord Botメインモジュール
メッセージを監視し、GoogleスプレッドシートのURLを検知して分析処理を実行します。
"""
import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional, Dict

from config import Config
from sheets_reader import SheetsReader
from gemini_analyzer import GeminiAnalyzer

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Botの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    """Bot起動時の処理"""
    logger.info(f'{bot.user} としてログインしました')
    logger.info(f'Bot ID: {bot.user.id}')
    
    # 設定の検証
    if not Config.validate():
        logger.error("必須設定が不足しています。.envファイルを確認してください。")
        return
    
    # 管理者ユーザーの確認
    try:
        admin_user = await bot.fetch_user(Config.ADMIN_USER_ID)
        logger.info(f"管理者ユーザー: {admin_user.name} (ID: {admin_user.id})")
    except discord.NotFound:
        logger.warning(f"管理者ユーザーID {Config.ADMIN_USER_ID} が見つかりません。")
    except Exception as e:
        logger.error(f"管理者ユーザーの取得エラー: {str(e)}")


@bot.event
async def on_message(message: discord.Message):
    """メッセージ受信時の処理"""
    # Bot自身のメッセージは無視
    if message.author == bot.user:
        return
    
    # 管理者のメッセージは無視
    if message.author.id == Config.ADMIN_USER_ID:
        return
    
    # スプレッドシートURLの検知
    if 'docs.google.com/spreadsheets' in message.content:
        logger.info(f"スプレッドシートURLを検知: {message.author.name} (チャンネル: {message.channel.name})")
        
        # URLを抽出
        url = _extract_url(message.content)
        if not url:
            logger.warning("URLの抽出に失敗しました")
            return
        
        # チャンネルにはメッセージを送らず、静かに処理
        try:
            # スプレッドシート読み取り
            sheets_reader = SheetsReader()
            sheets_data = sheets_reader.read_all_sheets(url)
            
            # Gemini分析
            analyzer = GeminiAnalyzer()
            report = analyzer.analyze(sheets_data)
            
            # 管理者にDM送信（分析結果、投稿者情報を含む）
            await _send_dm_to_admin(message, url, report)
            
            logger.info("分析処理が正常に完了しました")
            
        except ValueError as e:
            logger.error(f"エラー: {str(e)}")
            # エラー時も管理者に通知
            try:
                await _send_error_to_admin(message, url, str(e))
            except Exception as admin_error:
                logger.error(f"管理者へのエラー通知失敗: {str(admin_error)}")
            
        except Exception as e:
            logger.error(f"分析処理エラー: {str(e)}")
            # エラー時も管理者に通知
            try:
                await _send_error_to_admin(message, url, str(e))
            except Exception as admin_error:
                logger.error(f"管理者へのエラー通知失敗: {str(admin_error)}")
    
    # コマンド処理を継続
    await bot.process_commands(message)


def _extract_url(text: str) -> Optional[str]:
    """
    テキストからGoogleスプレッドシートのURLを抽出
    
    Args:
        text: メッセージテキスト
        
    Returns:
        str: 抽出されたURL、見つからない場合はNone
    """
    import re
    
    # URLパターンを検索
    url_pattern = r'https?://docs\.google\.com/spreadsheets/[^\s<>"{}|\\^`\[\]]+'
    match = re.search(url_pattern, text)
    
    if match:
        return match.group(0)
    
    return None


async def _send_dm_to_admin(original_message: discord.Message, url: str, report: str):
    """
    管理者にDMでレポートを送信（投稿者情報、分析結果を含む）
    
    Args:
        original_message: 元のDiscordメッセージ
        url: スプレッドシートURL
        report: 分析レポート
    """
    try:
        admin_user = await bot.fetch_user(Config.ADMIN_USER_ID)
        
        # ヘッダー部分（投稿者情報のみ）
        header = (
            f"# SEO構成案 分析レポート\n\n"
            f"## 📋 投稿情報\n"
            f"**投稿者**: {original_message.author.mention} ({original_message.author.name})\n"
            f"**投稿者ID**: {original_message.author.id}\n"
            f"**チャンネル**: {original_message.channel.mention} ({original_message.channel.name})\n"
            f"**スプレッドシートURL**: {url}\n"
            f"**投稿日時**: {original_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"---\n\n"
            f"## 📊 修正箇所\n\n"
        )
        
        # メッセージを組み立て（文字数制限なし、分割送信）
        full_message = header + report
        
        # Discordの2000文字制限を考慮して分割送信
        max_length = 2000
        if len(full_message) <= max_length:
            # 1回で送信可能
            await admin_user.send(full_message)
        else:
            # ヘッダーを先に送信
            await admin_user.send(header)
            await asyncio.sleep(0.5)
            
            # レポートを分割して送信（文字数制限なし、すべて送信）
            report_chunks = [report[i:i+max_length] for i in range(0, len(report), max_length)]
            for chunk in report_chunks:
                await admin_user.send(chunk)
                await asyncio.sleep(0.5)  # レート制限対策
        
        logger.info(f"管理者 ({admin_user.name}) にDMを送信しました")
        
    except discord.NotFound:
        logger.error(f"管理者ユーザーID {Config.ADMIN_USER_ID} が見つかりません")
    except discord.Forbidden:
        logger.error(f"管理者 ({Config.ADMIN_USER_ID}) のDMが閉じられています")
    except Exception as e:
        logger.error(f"管理者へのDM送信エラー: {str(e)}")


async def _send_error_to_admin(original_message: discord.Message, url: str, error_message: str):
    """
    エラー発生時に管理者に通知
    
    Args:
        original_message: 元のDiscordメッセージ
        url: スプレッドシートURL
        error_message: エラーメッセージ
    """
    try:
        admin_user = await bot.fetch_user(Config.ADMIN_USER_ID)
        
        error_report = (
            f"# ❌ 分析処理エラー\n\n"
            f"**投稿者**: {original_message.author.mention} ({original_message.author.name})\n"
            f"**チャンネル**: {original_message.channel.mention} ({original_message.channel.name})\n"
            f"**スプレッドシートURL**: {url}\n"
            f"**投稿日時**: {original_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"**エラー内容**:\n```\n{error_message}\n```"
        )
        
        await admin_user.send(error_report)
        logger.info(f"管理者 ({admin_user.name}) にエラー通知を送信しました")
        
    except Exception as e:
        logger.error(f"管理者へのエラー通知送信エラー: {str(e)}")


def main():
    """Botの起動"""
    if not Config.validate():
        logger.error("必須設定が不足しています。.envファイルを確認してください。")
        return
    
    if not Config.DISCORD_BOT_TOKEN:
        logger.error("DISCORD_BOT_TOKENが設定されていません。")
        return
    
    try:
        bot.run(Config.DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        logger.error("Discord Botのログインに失敗しました。トークンを確認してください。")
    except Exception as e:
        logger.error(f"Bot起動エラー: {str(e)}")


if __name__ == "__main__":
    main()
