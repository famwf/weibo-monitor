import os
import requests

# 从 GitHub Secrets 中读取配置
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
UID = "7627638226"  # 要监控的微博 UID


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
  # 升级版的移动端请求头，加入 Cookie 占位与更完整的防拦截字段
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605"
          ".1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
      ),
      "Accept": "application/json, text/plain, */*",
      "Accept-Language": "zh-CN,zh;q=0.9",
      "Referer": f"https://m.weibo.cn/u/{UID}",
      "X-Requested-With": "XMLHttpRequest",
  }

  try:
    response = requests.get(api_url, headers=headers, timeout=10)
    print(f"微博 API 状态码: {response.status_code}")

    # 打印前 200 个字符看看返回的到底是什么
    print(f"返回内容预览: {response.text[:200]}")

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
      print(f"微博接口返回状态不为1: {data}")
  except Exception as e:
    print(f"检查微博出错: {e}")
  return None, None, None, None


if __name__ == "__main__":
  print("微博监控任务开始...")
  blog_id, text, created_at, blog_url = check_weibo()
  if blog_id:
    print(f"获取到最新微博 ID: {blog_id}")
    msg = (
        f"🚨 **微博更新提醒**\n\n发布时间：{created_at}\n\n{text}\n\n🔗"
        f" [点击查看原博]({blog_url})"
    )
    send_telegram_message(msg)
  else:
    print("未获取到有效微博。")
