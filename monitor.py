import os
import requests

# 从 GitHub Secrets 中读取配置
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
UID = "7627638226"  # 要监控的微博 UID


def send_telegram_message(text):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
  try:
    response = requests.post(url, json=payload, timeout=10)
    return response.json()
  except Exception as e:
    print(f"发送 Telegram 消息失败: {e}")


def check_weibo_api():
  # 使用一个稳定的备用微博容器接口
  api_url = f"https://m.weibo.cn/api/container/getIndex?containerid=107603{UID}"

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605"
          ".1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
      ),
      "Referer": f"https://m.weibo.cn/u/{UID}",
      "Accept": "application/json, text/plain, */*",
  }

  try:
    print(f"正在请求微博 API: {api_url}")
    response = requests.get(api_url, headers=headers, timeout=10)
    print(f"请求状态码: {response.status_code}")

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
    else:
      print(f"接口返回数据异常: {data}")
  except Exception as e:
    print(f"请求微博发生异常: {e}")

  return None, None, None, None


if __name__ == "__main__":
  print("微博专用 API 监控任务开始...")
  blog_id, text, created_at, blog_url = check_weibo_api()

  if blog_id:
    print(f"成功获取到最新微博 ID: {blog_id}")
    msg = f"🚨 <b>微博更新提醒</b>\n\n🕒 时间：{created_at}\n\n{text}\n\n🔗 <a href='{blog_url}'>点击查看原博</a>"
    send_telegram_message(msg)
    print("Telegram 通知发送成功！")
  else:
    print("未获取到有效内容。")
