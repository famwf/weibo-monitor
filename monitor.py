import os
import time
import requests

# 从 GitHub Secrets 中读取配置
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
UID = "7627638226"  # 要监控的微博 UID

# GitHub Actions 每次运行时间有限，我们这里设定循环检查 3 次（每次间隔 20 秒）后自动退出，靠定时触发器重复执行
CHECK_TIMES = 3
INTERVAL = 20


def send_telegram_message(text):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
  try:
    response = requests.post(url, json=payload, timeout=10)
    return response.json()
  except Exception as e:
    print(f"发送 Telegram 消息失败: {e}")


def check_weibo():
  api_url = f"https://m.weibo.cn/api/container/getIndex?type=uid&value={UID}"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605"
          ".1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
      ),
      "Referer": f"https://m.weibo.cn/u/{UID}",
  }

  try:
    response = requests.get(api_url, headers=headers, timeout=10)
    data = response.json()

    if data.get("ok") == 1:
      cards = data["data"]["cards"]
      for card in cards:
        if card.get("card_type") == 9:
          mblog = card["mblog"]
          blog_id = mblog["id"]
          text = mblog.get("text", "（纯图片或视频微博）")
          created_at = mblog.get("created_at", "")
          bid = mblog.get("bid", "")
          blog_url = f"https://m.weibo.cn/detail/{bid}"
          return blog_id, text, created_at, blog_url
  except Exception as e:
    print(f"检查微博出错: {e}")
  return None, None, None, None


if __name__ == "__main__":
  print("微博监控任务开始...")
  # 这里可以通过一个简单文件记录上一次的 id（GitHub Actions 每次运行环境是干净的，
  # 但我们可以抓取最新的一条，或者通过对比实现。为了最简单，我们直接播报当前最新的一条，
  # 或者配合推送逻辑。如果你希望只看“新”发的，可以看下一步）
  # 实际上，由于 GitHub Actions 定时触发，我们每次运行只需要抓取最新的一条，
  # 并判断它是否在短时间内发布，或者直接发出来。
  blog_id, text, created_at, blog_url = check_weibo()
  if blog_id:
    print(f"获取到最新微博 ID: {blog_id}")
    msg = (
        f"🚨 **微博更新提醒**\n\n发布时间：{created_at}\n\n{text}\n\n🔗"
        f" [点击查看原博]({blog_url})"
    )
    # 发送通知
    send_telegram_message(msg)
