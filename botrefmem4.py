
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
botrefmem3.py
Gửi nhiều mẫu tin nhắn ngẫu nhiên vào danh sách GROUPS bằng Telethon.
"""

import asyncio
import random
import logging
from datetime import datetime, timedelta
from telethon import TelegramClient, errors, functions

# ==== CẤU HÌNH ==== #
api_id = 32969949
api_hash = "b1c472becdb64a852e53da2fe103e2d7"
phone = "+84564562327"

# ==== DANH SÁCH NHÓM CẦN GỬI ==== #
GROUPS = [
    "https://t.me/nhomcheoreffree",
    "https://t.me/giadinhtuhop",
    "https://t.me/kiemtien88hi",
    "https://t.me/congdongcheoref",
    "https://t.me/vinh22chat",
    "https://t.me/cheoreffuytinfree",
    "https://t.me/cheobottin",
    "https://t.me/KiemTien40CLB",
    "https://t.me/nhom4muamayman",
    "https://t.me/keokiemtienmienphiuytin",
    "https://t.me/railinkfreene",
    "https://t.me/codefreenofee",
    "https://t.me/memetauhai",
    "https://t.me/cheorefallbot",
    "https://t.me/cheorefuytinnhe",
    "https://t.me/cheouytin24",
    "https://t.me/codeandchills",
    "https://t.me/baokm48k",
    "https://t.me/nhomnhieukeongon",
    "https://t.me/minepsi2k",
    "https://t.me/QUOCDAOCASINO",
    "https://t.me/cheobotno1",
    "https://t.me/cheobot24h",
    "https://t.me/cheorefs24h",
    "https://t.me/cayrefs24h",
    "https://t.me/groupbotref",
    "https://t.me/cheobottin",
]

# ==== CẤU HÌNH GỬI ==== #
MIN_DELAY = 30       # giây giữa các nhóm
MAX_DELAY = 60
INTERVAL_BETWEEN_ROUNDS = 10 * 60  # 10 phút
SENDS_PER_CYCLE = 5
PAUSE_AFTER_CYCLE = 60 * 60  # 1 giờ
DRY_RUN = False  # True chỉ test, False gửi thật

# ==== NỘI DUNG TIN NHẮN QC (Tập trung vào Mail/SĐT Ảo FREE) ==== #
GROUP_MESSAGES = [
    # Dịch vụ rải link (Kéo User) - Tập trung vào 5K/ngày
    """
🚀 DỊCH VỤ RẢI LINK CHUYÊN NGHIỆP! 🚀
Cam kết user chất lượng, chi phí chỉ 7K/ngày/user.
🔥 Tăng trưởng ngay hôm nay! IB:@railinkuytin7k để nhận báo giá.
---
🔎 Check Bill/Uy Tín: https://t.me/dichvurailiankuytin
""",
    
    """
🎯 CẦN KÉO USER NHANH? CHỈ 7.000Đ/NGÀY! 🎯
Hệ thống rải link tự động, đảm bảo hiệu quả.
✅ Liên hệ IB:@railinkuytin7k để xem mẫu quảng cáo.
---
🔎 Check Bill/Uy Tín: https://t.me/dichvurailiankuytin
""",
    
    """
💰 TÌM USER ĐỀU ĐẶN 7K/NGÀY? 💰
Dịch vụ rải link trọn gói, không cần tự làm.
👉 Bắt đầu chiến dịch, IB:@railinkuytin7k ngay!
---
🔎 Check Bill/Uy Tín: https://t.me/dichvurailiankuytin
""",
    
    """
🛑 STOP TÌM KIẾM! Dịch vụ 7K/ngày ở đây! 🛑
Chuyên rải link thu hút user Telegram/FB.
👉 Muốn user chất lượng: IB:@railinkuytin7k NGAY!
---
🔎 Check Bill/Uy Tín: https://t.me/dichvurailiankuytin
""",
    
    """
⚡ ĐỪNG TỰ RẢI NỮA! THUÊ DỊCH VỤ CHỈ 7K/NGÀY ⚡
Tiết kiệm thời gian, tăng hiệu quả.
➡️ Gửi yêu cầu của bạn qua IB:@railinkuytin7k!
---
🔎 Check Bill/Uy Tín: https://t.me/dichvurailiankuytin
""",
    
    """
🤔 LÀM SAO ĐỂ CÓ USER KHÔNG CẦN QUẢNG CÁO? 🤔
Thuê dịch vụ rải link 7K/ngày của chúng tôi.
✅ Giải pháp thông minh: IB:@railinkuytin7k NGAY!
---
🔎 Check Bill/Uy Tín: https://t.me/dichvurailiankuytin
""",
    
    """
🔥 CHỐT DEAL USER GIÁ SỐC 7.000Đ/NGÀY! 🔥
Dịch vụ rải link 24/7. Cam kết có người dùng.
💥 Đặt lịch ngay: IB:@railinkuytin7k NHANH!
---
🔎 Check Bill/Uy Tín: https://t.me/dichvurailiankuytin
""",
    
    """
✅ UY TÍN SỐ 1 VỀ RẢI LINK - 7K/NGÀY ✅
User Telegram, kéo về theo yêu cầu.
🔗 Chi tiết:IB:@railinkuytin7k ngay!
---
🔎 Check Bill/Uy Tín: https://t.me/dichvurailiankuytin
""",
    
    """
🛡️ DỊCH VỤ RẢI LINK BẢO HÀNH TRỌN ĐỜI! 🛡️
User thật, chi phí rẻ chỉ 7K/ngày.
👉 Bảo hành vĩnh viễn: IB:@railinkuytin7k!
---
🔎 Check Bill/Uy Tín: https://t.me/dichvurailiankuytin
""",
    
    """
💵 DỊCH VỤ RẢI LINK TỐI ƯU CHI PHÍ! 💵
User mới mỗi ngày với giá cố định 7.000đ.
👉 Hỏi đáp và đặt dịch vụ: IB:@railinkuytin7k liền!
---
🔎 Check Bill/Uy Tín: https://t.me/dichvurailiankuytin
"""
]
# ==== LOGGING ==== #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("RefSender4")

# ==== TELETHON CLIENT ==== #
client = TelegramClient("ref_sender4", api_id, api_hash)

# ==== HỖ TRỢ KIỂM TRA MEMBER ==== #
async def is_member(entity):
    try:
        me = await client.get_me()
        await client(functions.channels.GetParticipantRequest(channel=entity, participant=me.id))
        return True
    except (errors.UserNotParticipantError, errors.ChannelPrivateError):
        return False
    except Exception as e:
        log.debug(f"is_member: exception for {entity}: {e}")
        return False

# ==== JOIN GROUP NẾU CẦN ==== #
async def join_if_needed(entity):
    if not await is_member(entity):
        try:
            await client(functions.channels.JoinChannelRequest(entity))
            title = getattr(entity, "title", str(getattr(entity, "id", entity)))
            log.info(f"✅ Đã join group trước khi gửi: {title}")
            await asyncio.sleep(1.5)
            return True
        except errors.UserAlreadyParticipantError:
            return True
        except errors.FloodWaitError as e:
            log.warning(f"🚨 FloodWait khi join {entity}: {e.seconds}s — chờ rồi tiếp tục.")
            await asyncio.sleep(e.seconds + 2)
            return False
        except Exception as e:
            log.warning(f"⚠️ Không thể join {getattr(entity, 'title', entity)}: {e}")
            return False
    return True

# ==== GỬI TIN NHẮN AN TOÀN ==== #
async def send_message_safe(entity):
    text = random.choice(GROUP_MESSAGES)
    try:
        if DRY_RUN:
            log.info(f"[TEST] Sẽ gửi vào {getattr(entity,'title',str(entity))}: {text[:120]}...")
            return True
        await client.send_message(entity, text)
        return True
    except errors.FloodWaitError as e:
        log.warning(f"🚨 FloodWait {e.seconds}s. Chờ {e.seconds + 5}s rồi thử lại...")
        await asyncio.sleep(e.seconds + 5)
        try:
            await client.send_message(entity, text)
            return True
        except Exception as e2:
            log.error(f"❌ Thử lại vẫn lỗi khi gửi vào {entity}: {e2}")
            return False
    except errors.ChatAdminRequiredError:
        log.error(f"❌ Không có quyền gửi vào {getattr(entity,'title',str(entity))}.")
        return False
    except errors.ForbiddenError:
        log.error(f"❌ Bị cấm gửi tin vào {getattr(entity,'title',str(entity))}.")
        return False
    except Exception as e:
        log.error(f"❌ Lỗi khi gửi vào {getattr(entity,'title',str(entity))}: {e}")
        return False

# ==== MAIN ==== #
async def main():
    await client.start(phone)
    entities = []

    for g in GROUPS:
        try:
            ent = await client.get_entity(g)
            entities.append(ent)
            log.info(f"✅ Đã load nhóm: {g} -> {getattr(ent, 'title', getattr(ent, 'id', g))}")
        except Exception as e:
            log.error(f"❌ Lỗi load nhóm {g}: {e}")

    if not entities:
        log.error("Không load được nhóm nào. Kiểm tra lại GROUPS / quyền tài khoản.")
        await client.disconnect()
        return

    round_counter = 0
    try:
        while True:
            round_counter += 1
            log.info(f"=== 🚀 BẮT ĐẦU LƯỢT {round_counter} ===")

            for ent in entities:
                can_send = await join_if_needed(ent)
                if not can_send:
                    title = getattr(ent, "title", str(getattr(ent, "id", ent)))
                    log.warning(f"⛔ Skip {title}: không join/send được.")
                    await asyncio.sleep(1.0)
                    continue

                ok = await send_message_safe(ent)
                if ok:
                    name = getattr(ent, "title", str(getattr(ent, "id", ent)))
                    log.info(f"📩 Đã gửi vào nhóm {name}")

                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                log.info(f"⏳ Nghỉ {delay:.1f}s trước khi gửi nhóm tiếp theo...")
                await asyncio.sleep(delay)

            if round_counter % SENDS_PER_CYCLE == 0:
                resume_time = datetime.now() + timedelta(seconds=PAUSE_AFTER_CYCLE)
                log.info(
                    f"🔁 Đã gửi {SENDS_PER_CYCLE} lượt. Nghỉ {PAUSE_AFTER_CYCLE//60} phút "
                    f"(tiếp tục lúc {resume_time.strftime('%H:%M:%S')})"
                )
                await asyncio.sleep(PAUSE_AFTER_CYCLE)
            else:
                resume_time = datetime.now() + timedelta(seconds=INTERVAL_BETWEEN_ROUNDS)
                log.info(
                    f"⏲ Hoàn tất lượt {round_counter}. Nghỉ {INTERVAL_BETWEEN_ROUNDS//60} phút "
                    f"(tiếp tục lúc {resume_time.strftime('%H:%M:%S')})"
                )
                await asyncio.sleep(INTERVAL_BETWEEN_ROUNDS)

    except KeyboardInterrupt:
        log.info("Dừng bằng tay (KeyboardInterrupt).")
    except Exception as e:
        log.exception(f"❌ Lỗi không mong muốn trong main: {e}")
    finally:
        await client.disconnect()
        log.info("Kết thúc và đã disconnect.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user")
