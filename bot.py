"""
Discord Botメインモジュール
メッセージを監視し、GoogleドキュメントのURLを検知して分析処理を実行します。
"""
import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional, Dict

from config import Config
from document_reader import DocumentReader
from gemini_analyzer import GeminiAnalyzer

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,  # デバッグモードに変更
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
    
    # 参加しているサーバー数を表示
    guild_count = len(bot.guilds)
    logger.info(f'参加しているサーバー数: {guild_count}')
    for guild in bot.guilds:
        logger.info(f'  - {guild.name} (ID: {guild.id})')
    
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
    
    logger.info("Botが正常に起動しました。メッセージの監視を開始します。")


@bot.event
async def on_message(message: discord.Message):
    """メッセージ受信時の処理"""
    # Bot自身のメッセージは無視
    if message.author == bot.user:
        return
    
    # 管理者のメッセージは無視
    if message.author.id == Config.ADMIN_USER_ID:
        return
    
    # デバッグ: メッセージを受信したことをログに記録
    logger.debug(f"メッセージを受信: {message.author.name} (チャンネル: {message.channel.name}) - 内容: {message.content[:100]}")
    
    # ドキュメントURLの検知（様々な形式に対応）
    if 'docs.google.com/document' in message.content or 'drive.google.com' in message.content:
        logger.info(f"ドキュメントURLを検知: {message.author.name} (チャンネル: {message.channel.name})")
        
        # URLを抽出
        url = _extract_url(message.content)
        if not url:
            logger.warning("URLの抽出に失敗しました")
            return
        
        # チャンネルにはメッセージを送らず、静かに処理
        try:
            # ドキュメント読み取り
            document_reader = DocumentReader()
            document_content = document_reader.read_document(url)
            
            # Gemini分析
            analyzer = GeminiAnalyzer()
            report = analyzer.analyze(document_content)
            
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
    テキストからGoogleドキュメントのURLを抽出
    
    Args:
        text: メッセージテキスト
        
    Returns:
        str: 抽出されたURL、見つからない場合はNone
    """
    import re
    
    # 様々なURL形式に対応
    url_patterns = [
        r'https?://docs\.google\.com/document/d/[a-zA-Z0-9-_]+[^\s<>"{}|\\^`\[\]]*',
        r'https?://docs\.google\.com/document/[^\s<>"{}|\\^`\[\]]+',
        r'https?://drive\.google\.com/file/d/[a-zA-Z0-9-_]+[^\s<>"{}|\\^`\[\]]*',
    ]
    
    for pattern in url_patterns:
        match = re.search(pattern, text)
        if match:
            url = match.group(0)
            # URLの末尾の不要な文字を削除
            url = url.rstrip('.,;:!?)')
            logger.debug(f"URLを抽出: {url}")
            return url
    
    logger.debug("URLの抽出に失敗")
    return None


async def _send_dm_to_admin(original_message: discord.Message, url: str, report: str):
    """
    管理者にDMでレポートを送信（投稿者情報、分析結果を含む）
    
    Args:
        original_message: 元のDiscordメッセージ
        url: ドキュメントURL
        report: 分析レポート
    """
    try:
        admin_user = await bot.fetch_user(Config.ADMIN_USER_ID)
        
        # ヘッダー部分（投稿者情報のみ）
        header = (
            f"# 初稿案 分析レポート\n\n"
            f"## 📋 投稿情報\n"
            f"**投稿者**: {original_message.author.mention} ({original_message.author.name})\n"
            f"**投稿者ID**: {original_message.author.id}\n"
            f"**チャンネル**: {original_message.channel.mention} ({original_message.channel.name})\n"
            f"**ドキュメントURL**: {url}\n"
            f"**投稿日時**: {original_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"---\n\n"
            f"## 📊 修正箇所\n\n"
        )
        
        # メッセージを組み立て（1回で送信）
        full_message = header + report
        
        # 2000文字を超える場合はファイルとして送信
        if len(full_message) > 2000:
            # ファイルとして送信
            import io
            file_content = io.BytesIO(full_message.encode('utf-8'))
            file = discord.File(file_content, filename='analysis_report.md')
            await admin_user.send(content="初稿案 分析レポート", file=file)
        else:
            # 通常のメッセージとして送信
            await admin_user.send(full_message)
        
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
        url: ドキュメントURL
        error_message: エラーメッセージ
    """
    try:
        admin_user = await bot.fetch_user(Config.ADMIN_USER_ID)
        
        # ヘッダー部分
        header = (
            f"# ❌ 分析処理エラー\n\n"
            f"**投稿者**: {original_message.author.mention} ({original_message.author.name})\n"
            f"**チャンネル**: {original_message.channel.mention} ({original_message.channel.name})\n"
            f"**ドキュメントURL**: {url}\n"
            f"**投稿日時**: {original_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"**エラー内容**:\n"
        )
        
        error_with_header = header + f"```\n{error_message}\n```"
        
        # 2000文字を超える場合はファイルとして送信
        if len(error_with_header) > 2000:
            # ファイルとして送信
            import io
            file_content = io.BytesIO(error_with_header.encode('utf-8'))
            file = discord.File(file_content, filename='error_report.md')
            await admin_user.send(content="分析処理エラー", file=file)
        else:
            # 通常のメッセージとして送信
            await admin_user.send(error_with_header)
        
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
