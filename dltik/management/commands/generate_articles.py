import json
import time
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from autowriter import ArticleGenerator
from dltik.models import Article, Tag
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = "Tạo bài viết tự động theo lịch liên tục"

    def handle(self, *args, **kwargs):
        while True:
            try:
                with open("topics.json", "r", encoding="utf-8") as f:
                    topics = json.load(f)
            except Exception as e:
                self.stderr.write(f"❌ Không đọc được topics.json: {e}")
                break

            generator = ArticleGenerator(settings.OPENAI_API_KEY)
            author = User.objects.first()
            if not author:
                self.stderr.write("❌ Không có user nào để gán làm tác giả.")
                break

            changed = False

            for entry in topics:
                if entry.get("created"):
                    continue

                topic = entry.get("topic")
                if not topic:
                    continue

                # Kiểm tra thời gian nếu có
                scheduled = entry.get("scheduled")
                if scheduled:
                    try:
                        scheduled_dt = datetime.strptime(scheduled, "%Y-%m-%d %H:%M")
                        if scheduled_dt > datetime.now():
                            continue
                    except Exception as e:
                        self.stderr.write(f"⚠️ Lỗi định dạng thời gian cho topic '{topic}': {e}")
                        continue

                self.stdout.write(f"✍️ Đang tạo bài viết: {topic}")
                result = generator.generate_article(topic)

                if "error" in result:
                    self.stderr.write(f"❌ Lỗi tạo bài: {result['error']}")
                    continue

                article = Article.objects.create(
                    title=result["title"],
                    slug=result["slug"],
                    description=result.get("description", ""),
                    content=result["content"],
                    author=author,
                    is_published=True,
                )

                for kw in result.get("keywords", []):
                    tag, _ = Tag.objects.get_or_create(name=kw)
                    article.tags.add(tag)

                entry["created"] = True
                changed = True
                self.stdout.write(f"✅ Đã lưu bài: {article.title}")

            if changed:
                try:
                    with open("topics.json", "w", encoding="utf-8") as f:
                        json.dump(topics, f, ensure_ascii=False, indent=4)
                    self.stdout.write("📁 Đã cập nhật file topics.json")
                except Exception as e:
                    self.stderr.write(f"⚠️ Không ghi được topics.json: {e}")

            time.sleep(60)  # Lặp lại sau mỗi 60 giây
