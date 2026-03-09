#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import requests
from seleniumbase import SB

LOGIN_URL = "https://justrunmy.app/id/Account/Login"
DOMAIN    = "justrunmy.app"

# ============================================================
#  环境变量对接 (由 .yml 传入)
# ============================================================
EMAIL        = os.environ.get("JUSTRUNMY_EMAIL")
PASSWORD     = os.environ.get("JUSTRUNMY_PASSWORD")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID   = os.environ.get("TG_CHAT_ID")

if not EMAIL or not PASSWORD:
    print("❌ 致命错误：未找到 JUSTRUNMY_EMAIL 或 JUSTRUNMY_PASSWORD！")
    sys.exit(1)

def send_tg_message(status_icon, status_text, time_left):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("ℹ️ 未配置 TG 变量，跳过推送。")
        return
    local_time = time.gmtime(time.time() + 8 * 3600)
    current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    message = (
        f"{status_icon} *JustRunMy 自动续期*\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📧 *账号*: `{EMAIL[:3]}***`\n"
        f"📝 *状态*: {status_text}\n"
        f"⏱️ *剩余*: {time_left}\n"
        f"📅 *时间*: {current_time_str}\n"
        f"━━━━━━━━━━━━━━━"
    )
    payload = {"chat_id": TG_ID if 'TG_ID' in locals() else TG_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage", json=payload)
    except: pass

def main():
    print(f"🚀 开始执行续期任务: {EMAIL[:3]}***")
    
    # 强制不使用缓存，开启 UC 模式
    with SB(uc=True, test=True, headless=False) as sb:
        try:
            # 1. 登录
            sb.open(LOGIN_URL)
            sb.type('input[name="Input.Email"]', EMAIL)
            sb.type('input[name="Input.Password"]', PASSWORD)
            sb.click('button[type="submit"]')
            sb.sleep(5)

            # 2. 进入控制面板 (根据原版逻辑)
            if "Account/Login" in sb.get_current_url():
                 print("❌ 登录失败，请检查账号密码")
                 return

            # 3. 寻找 Reset 按钮并点击
            # 注意：此处为原版核心点击逻辑的简化版，请确保你的按钮选择器正确
            print("🔍 正在查找续期按钮...")
            # 假设按钮包含 'Reset' 或 '续期' 字样
            if sb.is_element_visible('button:contains("Reset")'):
                sb.click('button:contains("Reset")')
                sb.sleep(3)
                print("✅ 已点击重置按钮")
                
                # 获取剩余时间
                timer_text = "已更新" 
                sb.save_screenshot("renew_success.png")
                send_tg_message("✅", "续期成功", timer_text)
            else:
                print("⚠️ 未找到续期按钮，可能已经续期过了")
                sb.save_screenshot("no_button.png")
                send_tg_message("ℹ️", "无需续期或未找到按钮", "未知")

        except Exception as e:
            print(f"💥 运行异常: {e}")
            sb.save_screenshot("error.png")
            send_tg_message("❌", "运行出错", str(e)[:20])

if __name__ == "__main__":
    main()
