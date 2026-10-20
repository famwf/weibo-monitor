import os
import feedparser  # 用于解析 RSS/XML
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
  # 使用稳定且公开的 RSSHub 节点获取该微博用户的 RSS 动态
  rss_url = f"https://rsshub.app/weibo/user/{UID}"

  try:
    print(f"正在请求 RSS 订阅源: {rss_url}")
    # 使用 feedparser 解析 RSS
    feed = feedparser.parse(rss_url)

    if feed.entries:
      # 获取最新的一条动态
      latest_entry = feed.entries[0]
      title = latest_entry.get("title", "（无标题）")
      link = latest_entry.get("link", "")
      published = latest_entry.get("published", "")
      guid = latest_entry.get("id", link)  # 用作唯一标识

      print(f"成功获取到最新动态: {title[:30]}...")
      return guid, title, published, link
    else:
      print("RSS 列表为空或请求被拦截。")
  except Exception as e:
    print(f"解析 RSS 出错: {e}")

  return None, None, None, None


if __name__ == "__main__":
  print("微博 RSS 监控任务开始...")
  guid, title, published, link = check_weibo_rss()

  if guid:
    # 组装推送消息
    msg = f"🚨 <b>微博更新提醒</b>\n\n🕒 时间：{published}\n\n{title}\n\n🔗 <a href='{link}'>点击查看原博</a>"
    send_telegram_message(msg)
    print("Telegram 通知发送成功！")
  else:
    print("未获取到有效内容。")
