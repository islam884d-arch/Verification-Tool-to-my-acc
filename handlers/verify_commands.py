"""Verification command handlers"""
import asyncio
import logging
import httpx
import time
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import VERIFY_COST
from database_mysql import Database
from one.sheerid_verifier import SheerIDVerifier as OneVerifier
from k12.sheerid_verifier import SheerIDVerifier as K12Verifier
from spotify.sheerid_verifier import SheerIDVerifier as SpotifyVerifier
from youtube.sheerid_verifier import SheerIDVerifier as YouTubeVerifier
from Boltnew.sheerid_verifier import SheerIDVerifier as BoltnewVerifier
from onestudent.sheerid_verifier import GeminiStudentVerifier
from utils.messages import get_insufficient_balance_message, get_verify_usage_message

# 尝试导入并发控制，如果失败则使用空实现
try:
    from utils.concurrency import get_verification_semaphore
except ImportError:
    # 如果导入失败，创建一个简单的实现
    def get_verification_semaphore(verification_type: str):
        return asyncio.Semaphore(3)

logger = logging.getLogger(__name__)


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify 命令 - Gemini One Pro"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked from using this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register first with /start.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify", "Gemini One Pro")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = OneVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link. Please check it and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Could not deduct points. Please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"Starting Gemini One Pro verification...\n"
        f"Verification ID: {verification_id}\n"
        f"Deducted {VERIFY_COST} points\n\n"
        "Please wait; this may take 1–2 minutes..."
    )

    try:
        verifier = OneVerifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "gemini_one_pro",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verification successful!\n\n"
            if result.get("pending"):
                result_msg += "Documents submitted and awaiting manual review.\n"
            if result.get("redirect_url"):
                result_msg += f"Redirect link：\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verification failed:{result.get('message', 'Unknown error')}\n\n"
                f"Refunded {VERIFY_COST} points"
            )
    except Exception as e:
        logger.error("Verification failed: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred while processing:{str(e)}\n\n"
            f"Refunded {VERIFY_COST} points"
        )


async def verify2_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify2 命令 - ChatGPT Teacher K12"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked from using this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register first with /start.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify2", "ChatGPT Teacher K12")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = K12Verifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link. Please check it and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Could not deduct points. Please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"Starting ChatGPT Teacher K12 verification...\n"
        f"Verification ID: {verification_id}\n"
        f"Deducted {VERIFY_COST} points\n\n"
        "Please wait; this may take 1–2 minutes..."
    )

    try:
        verifier = K12Verifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "chatgpt_teacher_k12",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verification successful!\n\n"
            if result.get("pending"):
                result_msg += "Documents submitted and awaiting manual review.\n"
            if result.get("redirect_url"):
                result_msg += f"Redirect link：\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verification failed:{result.get('message', 'Unknown error')}\n\n"
                f"Refunded {VERIFY_COST} points"
            )
    except Exception as e:
        logger.error("Verification failed: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred while processing:{str(e)}\n\n"
            f"Refunded {VERIFY_COST} points"
        )


async def verify3_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify3 命令 - Spotify Student"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked from using this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register first with /start.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify3", "Spotify Student")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # 解析 verificationId
    verification_id = SpotifyVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link. Please check it and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Could not deduct points. Please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"🎵 Starting Spotify Student verification...\n"
        f"Deducted {VERIFY_COST} points\n\n"
        "📝 Generating student details...\n"
        "🎨 Generating student ID PNG...\n"
        "📤 Submitting documents..."
    )

    # 使用信号量控制并发
    semaphore = get_verification_semaphore("spotify_student")

    try:
        async with semaphore:
            verifier = SpotifyVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "spotify_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Spotify Student verification successful!\n\n"
            if result.get("pending"):
                result_msg += "✨ Documents submitted and awaiting SheerID review\n"
                result_msg += "⏱️ Estimated review time: a few minutes\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 Redirect link：\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verification failed:{result.get('message', 'Unknown error')}\n\n"
                f"Refunded {VERIFY_COST} points"
            )
    except Exception as e:
        logger.error("Spotify Verification failed: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred while processing:{str(e)}\n\n"
            f"Refunded {VERIFY_COST} points"
        )


async def verify4_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify4 命令 - Bolt.new Teacher（自动获取code版）"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked from using this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register first with /start.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify4", "Bolt.new Teacher")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # 解析 externalUserId 或 verificationId
    external_user_id = BoltnewVerifier.parse_external_user_id(url)
    verification_id = BoltnewVerifier.parse_verification_id(url)

    if not external_user_id and not verification_id:
        await update.message.reply_text("Invalid SheerID link. Please check it and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Could not deduct points. Please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"🚀 Starting Bolt.new Teacher verification...\n"
        f"Deducted {VERIFY_COST} points\n\n"
        "📤 Submitting documents..."
    )

    # 使用信号量控制并发
    semaphore = get_verification_semaphore("bolt_teacher")

    try:
        async with semaphore:
            # 第1步：提交文档
            verifier = BoltnewVerifier(url, verification_id=verification_id)
            result = await asyncio.to_thread(verifier.verify)

        if not result.get("success"):
            # 提交失败，退款
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Document submission failed:{result.get('message', 'Unknown error')}\n\n"
                f"Refunded {VERIFY_COST} points"
            )
            return
        
        vid = result.get("verification_id", "")
        if not vid:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ No verification ID was returned\n\n"
                f"Refunded {VERIFY_COST} points"
            )
            return
        
        # 更新消息
        await processing_msg.edit_text(
            f"✅ Documents submitted!\n"
            f"📋 Verification ID: `{vid}`\n\n"
            f"🔍 Retrieving the verification code automatically...\n"
            f"(Waiting up to 20 seconds)"
        )
        
        # 第2步：自动获取认证码（最多20seconds）
        code = await _auto_get_reward_code(vid, max_wait=20, interval=5)
        
        if code:
            # 成功获取
            result_msg = (
                f"🎉 Verification successful!\n\n"
                f"✅ Documents submitted\n"
                f"✅ Review approved\n"
                f"✅ Verification code retrieved\n\n"
                f"🎁 Verification code:  `{code}`\n"
            )
            if result.get("redirect_url"):
                result_msg += f"\n🔗 Redirect link:\n{result['redirect_url']}"
            
            await processing_msg.edit_text(result_msg)
            
            # 保存成功记录
            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "success",
                f"Code: {code}",
                vid
            )
        else:
            # 20seconds内未获取到，让用户稍后查询
            await processing_msg.edit_text(
                f"✅ Documents submitted successfully!\n\n"
                f"⏳ The verification code is not ready yet (review may take 1–5 minutes).\n\n"
                f"📋 Verification ID: `{vid}`\n\n"
                f"💡 Run this command later to check:\n"
                f"`/getV4Code {vid}`\n\n"
                f"Note: Points have already been deducted. Checking again later is free."
            )
            
            # 保存待处理记录
            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "pending",
                "Waiting for review",
                vid
            )
            
    except Exception as e:
        logger.error("Bolt.new Verification failed: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred while processing:{str(e)}\n\n"
            f"Refunded {VERIFY_COST} points"
        )


async def _auto_get_reward_code(
    verification_id: str,
    max_wait: int = 20,
    interval: int = 5
) -> Optional[str]:
    """自动获取认证码（轻量级轮询，不影响并发）
    
    Args:
        verification_id: Verification ID
        max_wait: Maximum wait time in seconds
        interval: Polling interval in seconds
        
    Returns:
        str: Verification code, or None if retrieval fails
    """
    import time
    start_time = time.time()
    attempts = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            elapsed = int(time.time() - start_time)
            attempts += 1
            
            # 检查是否超时
            if elapsed >= max_wait:
                logger.info(f"Automatic code retrieval timed out({elapsed}seconds), the user can check manually")
                return None
            
            try:
                # 查询验证状态
                response = await client.get(
                    f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    current_step = data.get("currentStep")
                    
                    if current_step == "success":
                        # 获取认证码
                        code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
                        if code:
                            logger.info(f"✅ Automatic code retrieval succeeded: {code} (耗时{elapsed}seconds)")
                            return code
                    elif current_step == "error":
                        # Review failed
                        logger.warning(f"Review failed: {data.get('errorIds', [])}")
                        return None
                    # else: pending，继续等待
                
                # 等待下次轮询
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.warning(f"Error checking the verification code: {e}")
                await asyncio.sleep(interval)
    
    return None


async def verify5_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify5 命令 - YouTube Student Premium"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked from using this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register first with /start.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify5", "YouTube Student Premium")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # 解析 verificationId
    verification_id = YouTubeVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link. Please check it and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Could not deduct points. Please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"📺 Starting YouTube Student Premium verification...\n"
        f"Deducted {VERIFY_COST} points\n\n"
        "📝 Generating student details...\n"
        "🎨 Generating student ID PNG...\n"
        "📤 Submitting documents..."
    )

    # 使用信号量控制并发
    semaphore = get_verification_semaphore("youtube_student")

    try:
        async with semaphore:
            verifier = YouTubeVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "youtube_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ YouTube Student Premium verification successful!\n\n"
            if result.get("pending"):
                result_msg += "✨ Documents submitted and awaiting SheerID review\n"
                result_msg += "⏱️ Estimated review time: a few minutes\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 Redirect link：\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verification failed:{result.get('message', 'Unknown error')}\n\n"
                f"Refunded {VERIFY_COST} points"
            )
    except Exception as e:
        logger.error("YouTube Verification failed: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred while processing:{str(e)}\n\n"
            f"Refunded {VERIFY_COST} points"
        )


async def verify6_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify6 命令 - Gemini One Student (45+ Universities)"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked from using this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register first with /start.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify6", "Gemini One Student (Advanced)")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # 解析 verificationId
    verification_id = GeminiStudentVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link. Please check it and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Could not deduct points. Please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"🎓 Starting Gemini One Student verification...\n"
        f"Deducted {VERIFY_COST} points\n\n"
        "📝 Generating student details...\n"
        "🏫 Selecting a university (45+)...\n"
        "📄 Generating student documents...\n"
        "📤 Submitting to SheerID..."
    )

    # 使用信号量控制并发
    semaphore = get_verification_semaphore("gemini_student")

    try:
        async with semaphore:
            verifier = GeminiStudentVerifier(verification_id)
            result = await verifier.verify()

        db.add_verification(
            user_id,
            "gemini_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Gemini One Student verification successful!\n\n"
            result_msg += f"👤 Student:  {result.get('student', 'N/A')}\n"
            result_msg += f"🆔 Student ID: {result.get('student_id', 'N/A')}\n"
            result_msg += f"📧 Email: {result.get('email', 'N/A')}\n"
            result_msg += f"🏫 School: {result.get('school', 'N/A')}\n"
            result_msg += f"📄 Documents: {result.get('doc_count', 0)}  ({result.get('doc_types', 'N/A')})\n\n"
            
            if result.get("pending"):
                result_msg += "✨ Documents submitted and awaiting SheerID review\n"
                result_msg += "⏱️ Estimated review time: a few minutes to 1 hour\n\n"
            
            if result.get("redirect_url"):
                result_msg += f"🔗 Redirect link：\n{result['redirect_url']}"
            
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verification failed:{result.get('message', 'Unknown error')}\n\n"
                f"Refunded {VERIFY_COST} points"
            )
    except Exception as e:
        logger.error("Gemini Student Verification failed: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred while processing:{str(e)}\n\n"
            f"Refunded {VERIFY_COST} points"
        )


async def getV4Code_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /getV4Code 命令 - 获取 Bolt.new Teacher verification码"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked from using this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register first with /start.")
        return

    # 检查是否提供了 verification_id
    if not context.args:
        await update.message.reply_text(
            "Usage: /getV4Code <verification_id>\n\n"
            "Example: /getV4Code 6929436b50d7dc18638890d0\n\n"
            "The verification_id is returned after you use /verify4."
        )
        return

    verification_id = context.args[0].strip()

    processing_msg = await update.message.reply_text(
        "🔍 Checking the verification code. Please wait..."
    )

    try:
        # 查询 SheerID API 获取认证码
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
            )

            if response.status_code != 200:
                await processing_msg.edit_text(
                    f"❌ Lookup failed. Status code: {response.status_code}\n\n"
                    "Please try again later or contact an admin."
                )
                return

            data = response.json()
            current_step = data.get("currentStep")
            reward_code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
            redirect_url = data.get("redirectUrl")

            if current_step == "success" and reward_code:
                result_msg = "✅ Verification successful!\n\n"
                result_msg += f"🎉 Verification code: `{reward_code}`\n\n"
                if redirect_url:
                    result_msg += f"Redirect link：\n{redirect_url}"
                await processing_msg.edit_text(result_msg)
            elif current_step == "pending":
                await processing_msg.edit_text(
                    "⏳ Verification is still under review. Please try again later.\n\n"
                    "This usually takes 1–5 minutes. Please wait."
                )
            elif current_step == "error":
                error_ids = data.get("errorIds", [])
                await processing_msg.edit_text(
                    f"❌ Verification failed\n\n"
                    f"Error details: {', '.join(error_ids) if error_ids else 'Unknown error'}"
                )
            else:
                await processing_msg.edit_text(
                    f"⚠️ Current status: {current_step}\n\n"
                    "The verification code is not ready yet. Please try again later."
                )

    except Exception as e:
        logger.error("Failed to retrieve the Bolt.new verification code: %s", e)
        await processing_msg.edit_text(
            f"❌ An error occurred while checking:{str(e)}\n\n"
            "Please try again later or contact an admin."
        )
