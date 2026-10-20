import os
import feedparser
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


def check_weibo_rss():
  # 使用多条备用公开 RSS 线路，轮流请求以确保高可用
  rss_urls = [
      f"https://rsshub.app/weibo/user/{UID}",
      f"https://hub.slarker.me/weibo/user/{UID}",
  ]

  for rss_url in rss_urls:
    try:
      print(f"正在尝试请求 RSS 节点: {rss_url}")
      # 加上浏览器级别的 User-Agent 防止 RSS 节点自身拦截
      headers = {
          "User-Agent": (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
          )
      }
      response = requests.get(rss_url, headers=headers, timeout=15)
      if response.status_code == 200 and len(response.text) > 100:
        # 使用 feedparser 解析获取到的 RSS 内容
        feed = feedparser.parse(response.text)
        if feed.entries:
          latest_entry = feed.entries[0]
          title = latest_entry.get("title", "（无标题）")
          link = latest_entry.get("link", "")
          published = latest_entry.get("published", "")
          guid = latest_entry.get("id", link)
          print(f"成功通过节点获取到动态: {title[:30]}...")
          return guid, title, published, link
    except Exception as e:
      print(f"节点 {rss_url} 请求出错: {e}")

  print("所有 RSS 节点均未能获取到有效数据。")
  return None, None, None, None


if __name__ == "__main__":
  print("微博稳定 RSS 监控任务开始...")
  guid, title, published, link = check_weibo_rss()

  if guid:
    msg = f"🚨 <b>微博更新提醒</b>\n\n🕒 时间：{published}\n\n{title}\n\n🔗 <a href='{link}'>点击查看原博</a>"
    send_telegram_message(msg)
    print("Telegram 通知发送成功！")
  else:
    print("未获取到有效内容。")
