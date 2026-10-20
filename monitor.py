import os
import requests

# 从 GitHub Secrets 中读取配置
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
WEIBO_COOKIE = os.environ.get("WEIBO_COOKIE")
UID = "7627638226"
LAST_ID_FILE = "last_id.txt"


def send_telegram_message(text):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
  try:
    response = requests.post(url, json=payload, timeout=10)
    result = response.json()
    if result.get("ok"):
      print("Telegram 官方确认：消息发送成功！")
      return True
    else:
      print(f"❌ Telegram 拒绝发送，错误原因: {result}")
      return False
  except Exception as e:
    print(f"发送 Telegram 消息异常: {e}")
    return False


def get_last_saved_id():
  if os.path.exists(LAST_ID_FILE):
    with open(LAST_ID_FILE, "r", encoding="utf-8") as f:
      return f.read().strip()
  return ""


def save_last_id(blog_id):
  with open(LAST_ID_FILE, "w", encoding="utf-8") as f:
    f.write(str(blog_id))


def check_weibo_with_cookie():
  api_url = f"https://m.weibo.cn/api/container/getIndex?containerid=107603{UID}"

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605"
          ".1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
      ),
      "Referer": f"https://m.weibo.cn/u/{UID}",
      "Accept": "application/json, text/plain, */*",
      "Cookie": f"SUB={WEIBO_COOKIE}",
  }

  try:
    print("正在带 Cookie 请求微博 API...")
    response = requests.get(api_url, headers=headers, timeout=15)
    print(f"请求状态码: {response.status_code}")

    data = response.json()
    if data.get("ok") == 1:
      cards = data["data"]["cards"]
      for card in cards:
        if card.get("card_type") == 9:
          mblog = card["mblog"]
          blog_id = str(mblog["id"])
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
  print("带 Cookie 认证的微博监控任务开始...")
  blog_id, text, created_at, blog_url = check_weibo_with_cookie()

  if blog_id:
    print(f"成功获取到最新微博 ID: {blog_id}")
    last_id = get_last_saved_id()

    # 注意：因为刚才已经把 ID 写入过 last_id.txt 了，
    # 如果想强制再测试一次推送，可以把下面这行改成 if True:
    if blog_id != last_id or True:
      print("准备发送 Telegram 通知...")
      msg = f"🚨 <b>微博更新提醒</b>\n\n🕒 时间：{created_at}\n\n{text}\n\n🔗 <a href='{blog_url}'>点击查看原博</a>"
      send_telegram_message(msg)
      save_last_id(blog_id)
    else:
      print("没有检测到新微博（与上次记录相同）。")
  else:
    print("未获取到有效内容。")
