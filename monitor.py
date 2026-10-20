import json
import os
import requests

# 从 GitHub Secrets 中读取配置
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
UID = "7627638226"  # 要监控的微博 UID
LAST_ID_FILE = "last_id.txt"


def send_telegram_message(text):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
  try:
    response = requests.post(url, json=payload, timeout=10)
    return response.json()
  except Exception as e:
    print(f"发送 Telegram 消息失败: {e}")


def get_last_saved_id():
  if os.path.exists(LAST_ID_FILE):
    with open(LAST_ID_FILE, "r", encoding="utf-8") as f:
      return f.read().strip()
  return ""


def save_last_id(blog_id):
  with open(LAST_ID_FILE, "w", encoding="utf-8") as f:
    f.write(str(blog_id))


def check_weibo_web():
  # 使用微博公开的主页接口，并带上更完整的浏览器模拟特征
  url = f"https://m.weibo.cn/profile/info?uid={UID}"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605"
          ".1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
      ),
      "Referer": f"https://m.weibo.cn/u/{UID}",
      "Accept": "application/json, text/plain, */*",
      "X-Requested-With": "XMLHttpRequest",
  }

  try:
    print(f"正在请求微博公开主页信息...")
    response = requests.get(url, headers=headers, timeout=15)
    print(f"请求状态码: {response.status_code}")

    data = response.json()
    if data.get("ok") == 1:
      # 从主页数据中提取最近的一条微博
      status = data.get("data", {}).get("status", {})
      if status:
        blog_id = str(status.get("id"))
        text = status.get("text", "（纯图片或视频微博）")
        created_at = status.get("created_at", "")
        bid = status.get("bid", "")
        blog_url = f"https://m.weibo.cn/detail/{bid}"
        return blog_id, text, created_at, blog_url
    else:
      print(f"接口返回数据异常: {data}")
  except Exception as e:
    print(f"请求微博发生异常: {e}")

  return None, None, None, None


if __name__ == "__main__":
  print("微博网页直连监控任务开始...")
  blog_id, text, created_at, blog_url = check_weibo_web()

  if blog_id:
    print(f"成功获取到最新微博 ID: {blog_id}")
    last_id = get_last_saved_id()

    if blog_id != last_id:
      print("检测到新微博，准备发送通知...")
      msg = f"🚨 <b>微博更新提醒</b>\n\n🕒 时间：{created_at}\n\n{text}\n\n🔗 <a href='{blog_url}'>点击查看原博</a>"
      send_telegram_message(msg)
      save_last_id(blog_id)
      print("Telegram 通知发送成功，已更新本地记录！")
    else:
      print("没有检测到新微博（与上次记录相同）。")
  else:
    print("未获取到有效内容。")
