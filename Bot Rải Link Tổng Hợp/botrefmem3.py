#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
botrefmem_single_photo_real_run_okeybtc.py
Gửi 1 ảnh kèm 10 mẫu caption OKEYBTC khác nhau vào danh sách GROUPS.
CHẾ ĐỘ GỬI THẬT (DRY_RUN = False).

Phiên bản tối ưu hóa:
- Xử lý FloodWait cho cả Upload và Send bằng vòng lặp (lên đến 3 lần thử).
- Loại bỏ các nhóm đã xác định lỗi vĩnh viễn (link hỏng/bị cấm gửi).
"""

import asyncio
import random
import logging
import os
from datetime import datetime, timedelta
from telethon import TelegramClient, errors, functions

# =================================================================
# ==== CẤU HÌNH BẮT BUỘC - VUI LÒNG ĐIỀN THÔNG TIN CỦA BẠN VÀO ĐÂY ====
# =================================================================
api_id = 25171035       # <--- ĐIỀN API ID
api_hash = "02663fe920e4a55872a28d756e75236c"  # <--- ĐIỀN API HASH
phone = "+84522572886" # <--- ĐIỀN SĐT (Kèm mã quốc gia)

# ==== CẤU HÌNH MEDIA (CHỈ GỬI MỘT ẢNH) ==== #
MEDIA_FILE = "photo_2025-11-10_20-27-58.jpg" # <--- TÊN FILE ẢNH ĐƠN CẦN GỬI

# ==== DANH SÁCH NHÓM CẦN GỬI (ĐÃ CẬP NHẬT/LOẠI BỎ CÁC NHÓM BỊ LỖI VĨNH VIỄN) ==== #
GROUPS = [
    "https://t.me/giadinhtuhop", "https://t.me/congdongcheoref", "https://t.me/keokiemtienmienphiuytin",
    "https://t.me/railinkfreene", 
    # Đã loại bỏ: "https://t.me/memetauhai" (Không tồn tại)
    "https://t.me/cheorefuytinnhe",
    "https://t.me/cheouytin24", "https://t.me/codeandchills", "https://t.me/minepsi2k",
    "https://t.me/QUOCDAOCASINO", 
    
    # Nhóm mới được thêm vào (Đã loại bỏ nhóm cấm gửi/cấm tài khoản)
    "https://t.me/kiemtien88hi", "https://t.me/nhom4muamayman", "https://t.me/Macaodanhbac",
    "https://t.me/cheorefallbot", "https://t.me/cheobottin", "https://t.me/cheobotno1",
    "https://t.me/cheobot24h", 
    # Đã loại bỏ: "https://t.me/cayrefs24h" (Cấm gửi ảnh - RPCError 403)
    "https://t.me/cheorefs24h",
    "https://t.me/groupbotref", "https://t.me/cheoreffuytinfree", "https://t.me/nhomchatvuivenhamn",
    "https://t.me/thongbaoruttienkiemtienanvat", "https://t.me/nhomcheoreffree",
    "https://t.me/codefreenofee", 
    # Đã loại bỏ: "https://t.me/nhomnhieukeongon" (Tài khoản bị cấm gửi tin - You're banned...)
    "https://t.me/baokm48k",
    "https://t.me/KiemTien40CLB", "https://t.me/nhomcheorefuytinvn", "https://t.me/vinh22chat",
]

# ==== CẤU HÌNH GỬI AN TOÀN (GIỮ NGUYÊN) ==== #
MIN_DELAY = 60       # Tối thiểu 60 giây
MAX_DELAY = 90       # Tối đa 90 giây
INTERVAL_BETWEEN_ROUNDS = 20 * 60  # 20 phút nghỉ giữa các lượt gửi
SENDS_PER_CYCLE = 5
PAUSE_AFTER_CYCLE = 90 * 60  # 90 phút nghỉ sau mỗi chu kỳ 5 lượt
DRY_RUN = False  # <--- CHẾ ĐỘ GỬI THẬT

# ==== 10 NỘI DUNG TIN NHẮN OKEYBTC (GIỮ NGUYÊN) ==== #
GROUP_MESSAGES = [
    """
✅ *Đăng Ký Free* **100K TRẢI NGHIỆM** (Sự Kiện Mới)
✔️ Đăng kí ngay: https://www.okeybtc.net/?fx=28546&rt=matchRegister
🎁 Mã giới thiệu: **28546**
(Thưởng trải nghiệm có thể rút được! 🚀)
""",
    """
🌟 *CƠ HỘI ĐỘC QUYỀN* - Nhận ngay **100K FREE**!
🔥 Đăng ký: https://www.okeybtc.net/?fx=28546&rt=matchRegister
🔑 Mã giới thiệu: **28546**
---
(Áp dụng cho thành viên mới 🤑)
""",
    """
🏆 *SIÊU TẶNG THƯỞNG* 🏆 **FREE 100.000 VNĐ** VỐN TRẢI NGHIỆM!
✅ Đăng kí ngay: https://www.okeybtc.net/?fx=28546&rt=matchRegister
👉 Mã Giới Thiệu: **28546**
(Nhận thưởng miễn phí 💯)
""",
    """
✨ **Đăng Ký 100K Trải Nghiệm Ngay!** ✨
🔔 Link: https://www.okeybtc.net/?fx=28546&rt=matchRegister
---
📌 Mã ref: **28546** (Bắt buộc)
(Tuyệt đối uy tín ✔️)
""",
    """
🎉 *QUÀ TẶNG TÂN THỦ* 🎉 Đăng ký OKEYBTC Free **100K**!
✅ Link ĐK: https://www.okeybtc.net/?fx=28546&rt=matchRegister
Mã giới thiệu: **28546**
👉 Nhận ngay **100K**! 🚀
""",
    """
⭐ **100K FREE TRIAL** (Có thể rút được!)
🚨 Đăng kí ngay: https://www.okeybtc.net/?fx=28546&rt=matchRegister
Mã giới thiệu: **28546**
(Không cần nạp, nhận 100K miễn phí 🎁)
""",
    """
✅ **Đăng Ký Free 100K TRẢI NGHIỆM** ✅
🤗 Đăng kí ngay: https://www.okeybtc.net/?fx=28546&rt=matchRegister

😜 Mã giới thiệu: **28546**
""",
    """
💰 Đăng Ký tài khoản mới nhận **100K Trải Nghiệm**!
➡️ **Bấm Ngay**: https://www.okeybtc.net/?fx=28546&rt=matchRegister
🔑 Mã ref: **28546**
(Ưu đãi đặc biệt chỉ dành cho thành viên mới 💎)
""",
    """
💖 **TẶNG 100K VỐN TRẢI NGHIỆM MIỄN PHÍ!**
✅ Đăng ký: https://www.okeybtc.net/?fx=28546&rt=matchRegister
---
Mã giới thiệu: **28546**
*Uy tín tuyệt đối! 💯*
""",
    """
🛑 **ĐĂNG KÝ FREE NHẬN 100.000 VNĐ**
✔️ Link ĐK chính thức: https://www.okeybtc.net/?fx=28546&rt=matchRegister
Mã mời (Ref Code): **28546**
🎁 Nhận thưởng ngay lập tức! ✨
"""
]


# =================================================================
# ==== LOGIC VÀ HÀM HỖ TRỢ (ĐÃ TỐI ƯU HÓA GỬI ẢNH BẰNG VÒNG LẶP) ====
# =================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("RefSenderSinglePhoto")

client = TelegramClient("ref_sender_single_photo", api_id, api_hash)

# Kiểm tra sự tồn tại của file ảnh
if not os.path.exists(MEDIA_FILE):
    log.error(f"⚠️ LỖI CẤU HÌNH: File ảnh {MEDIA_FILE} không tồn tại.")
    log.error("Vui lòng kiểm tra lại tên và đường dẫn file ảnh.")
    
# ==== HỖ TRỢ KIỂM TRA MEMBER (Giữ nguyên) ==== #
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

# ==== JOIN GROUP NẾU CẦN (Giữ nguyên) ==== #
async def join_if_needed(entity):
    if not await is_member(entity):
        try:
            await client(functions.channels.JoinChannelRequest(entity))
            title = getattr(entity, "title", str(getattr(entity, "id", entity)))
            log.info(f"✅ Đã join group trước khi gửi: {title}")
            await asyncio.sleep(2.0)
            return True
        except errors.UserAlreadyParticipantError:
            return True
        except errors.FloodWaitError as e:
            log.warning(f"🚨 FloodWait khi join {entity}: {e.seconds}s — chờ rồi tiếp tục.")
            await asyncio.sleep(e.seconds + 5) 
            return False
        except errors.InviteHashExpiredError:
            log.warning(f"⚠️ Link mời {entity} đã hết hạn.")
            return False
        except Exception as e:
            log.warning(f"⚠️ Không thể join {getattr(entity, 'title', entity)}: {e}")
            return False
    return True

# ==== GỬI ẢNH ĐƠN AN TOÀN (TỐI ƯU HÓA BẰNG VÒNG LẶP) ==== #
async def send_message_safe(entity):
    text = random.choice(GROUP_MESSAGES)

    if not os.path.exists(MEDIA_FILE):
        log.error(f"❌ Lỗi: Không thể gửi vào {getattr(entity,'title',str(entity))} vì thiếu file ảnh: {MEDIA_FILE}")
        return False
        
    uploaded_file = None
    # Cải tiến 1: Tải ảnh lên trước và xử lý FloodWait (Thử 2 lần)
    for attempt_upload in range(1, 3):
        try:
            log.info(f"Uploading file (Lần {attempt_upload})...")
            uploaded_file = await client.upload_file(MEDIA_FILE)
            break # Upload thành công, thoát vòng lặp
        except errors.FloodWaitError as e:
            log.warning(f"🚨 FloodWait khi Upload (Lần {attempt_upload}/2) {e.seconds}s. Chờ {e.seconds + 5}s...")
            if attempt_upload == 2:
                log.error(f"❌ Upload ảnh thất bại sau 2 lần thử. Bỏ qua nhóm.")
                return False
            await asyncio.sleep(e.seconds + 5)
        except Exception as e:
            log.error(f"❌ Lỗi không xác định khi upload ảnh: {e}")
            return False

    if not uploaded_file:
        return False # Upload thất bại sau các lần thử

    # Cải tiến 2: Gửi ảnh kèm caption (Thử 3 lần nếu gặp FloodWait)
    for attempt_send in range(1, 4):
        try:
            await client.send_file(
                entity,
                file=uploaded_file, 
                caption=text,      
                parse_mode='Markdown'
            )
            return True # Gửi thành công

        except errors.FloodWaitError as e:
            log.warning(f"🚨 FloodWait (Lần {attempt_send}/3) {e.seconds}s khi gửi. Chờ {e.seconds + 5}s...")
            if attempt_send == 3:
                log.error(f"❌ Gửi vào {getattr(entity,'title',str(entity))} thất bại sau 3 lần FloodWait.")
                break # Thử lại thất bại, thoát vòng lặp
            await asyncio.sleep(e.seconds + 5)
        
        # Bắt các lỗi cấm/không có quyền gửi (Lỗi vĩnh viễn)
        except (errors.ChatAdminRequiredError, errors.ChatWriteForbiddenError, errors.ForbiddenError) as e:
            log.error(f"❌ Bị cấm/không có quyền gửi ẢNH ĐƠN vào {getattr(entity,'title',str(entity))}. Lỗi: {e}")
            return False # Lỗi vĩnh viễn, không cần thử lại
        except Exception as e:
            log.error(f"❌ Lỗi không xác định khi gửi ẢNH ĐƠN vào {getattr(entity,'title',str(entity))}: {e}")
            return False # Lỗi khác, không cần thử lại
            
    return False # Gửi thất bại sau các lần thử FloodWait

# ==== MAIN LOOP (Giữ nguyên) ==== #
async def main():
    log.info("Connecting...")
    await client.start(phone)
    log.info("Client connected.")
    
    # Kiểm tra lần cuối file ảnh
    if not os.path.exists(MEDIA_FILE):
        log.error("❌ Dừng lại: File ảnh không hợp lệ. Vui lòng kiểm tra lại cấu hình MEDIA_FILE.")
        await client.disconnect()
        return

    entities = []

    for g in GROUPS:
        try:
            ent = await client.get_entity(g)
            entities.append(ent)
            log.info(f"✅ Đã load nhóm: {g} -> {getattr(ent, 'title', getattr(ent, 'id', g))}")
        except Exception as e:
            log.error(f"❌ Lỗi load nhóm {g}: {e}")
            await asyncio.sleep(1.0) 

    if not entities:
        log.error("Không load được nhóm nào. Kiểm tra lại GROUPS / quyền tài khoản.")
        await client.disconnect()
        return

    round_counter = 0
    try:
        while True:
            round_counter += 1
            log.info(f"\n=== 🚀 BẮT ĐẦU LƯỢT {round_counter} ({datetime.now().strftime('%H:%M:%S')}) ===")

            random.shuffle(entities) 
            
            for ent in entities:
                # 1. Join nếu cần
                can_send = await join_if_needed(ent)
                if not can_send:
                    title = getattr(ent, "title", str(getattr(ent, "id", ent)))
                    log.warning(f"⛔ Skip {title}: không join được.")
                    await asyncio.sleep(2.0)
                    continue

                # 2. Gửi Ảnh Đơn
                ok = await send_message_safe(ent)
                
                # 3. Log và chờ
                name = getattr(ent, "title", str(getattr(ent, "id", ent)))
                if ok:
                    log.info(f"📩 Gửi OK ẢNH ĐƠN vào nhóm {name}")
                else:
                    log.warning(f"❌ Gửi FAILED vào nhóm {name}. Tiếp tục...")
                
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                log.info(f"⏳ Nghỉ {delay:.1f}s trước khi gửi nhóm tiếp theo...")
                await asyncio.sleep(delay)

            # 4. Kiểm tra chu kỳ nghỉ dài
            if round_counter % SENDS_PER_CYCLE == 0:
                resume_time = datetime.now() + timedelta(seconds=PAUSE_AFTER_CYCLE)
                log.info(
                    f"\n\n=======================================================\n"
                    f"🔁 Đã gửi đủ {SENDS_PER_CYCLE} lượt. NGHỈ DÀI {PAUSE_AFTER_CYCLE//60} phút "
                    f"(Tiếp tục lúc {resume_time.strftime('%H:%M:%S')})\n"
                    f"=======================================================\n"
                )
                await asyncio.sleep(PAUSE_AFTER_CYCLE)
            else:
                resume_time = datetime.now() + timedelta(seconds=INTERVAL_BETWEEN_ROUNDS)
                log.info(
                    f"\n--- Hoàn tất lượt {round_counter}. Nghỉ ngắn {INTERVAL_BETWEEN_ROUNDS//60} phút "
                    f"(Tiếp tục lúc {resume_time.strftime('%H:%M:%S')}) ---\n"
                )
                await asyncio.sleep(INTERVAL_BETWEEN_ROUNDS)

    except KeyboardInterrupt:
        log.info("\n\n--- Dừng bằng tay (KeyboardInterrupt). ---")
    except Exception as e:
        log.exception(f"\n\n❌ Lỗi không mong muốn trong main: {e}")
    finally:
        log.info("\n--- Đang disconnect client... ---")
        await client.disconnect()
        log.info("--- Kết thúc và đã disconnect. ---")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
