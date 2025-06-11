import threading, time, queue
from django.utils import timezone
from django.db import connection, OperationalError
from django.conf import settings
from dltik.flags import FlagManager
from dltik.models import ScheduledTopic, Article, Tag
from autowriter import ArticleGenerator

worker_thread = None
task_queue = queue.Queue()

def worker_loop():

    periodic_interval = 10
    next_periodic = time.time()

    while is_worker_running():

        try:

            if not task_queue.empty():
                task = task_queue.get()
                task.run()
                task_queue.task_done()

            now = time.time()
            if now >= next_periodic:
                periodic_tasks()
                next_periodic = now + periodic_interval

            time.sleep(settings.WORKER_DELAY)
        except Exception as e:
            add_log(f"Worker error: {e}")
            time.sleep(10)
    add_log("Worker stopped", "success")

def periodic_tasks():

    pending_topics = ScheduledTopic.objects.filter(is_generated=False, scheduled__lte=timezone.now())

    if not pending_topics.exists():
        return

    add_log(f"🔄 Đang kiểm tra {pending_topics.count()} chủ đề đã tới lịch.")

    generator = ArticleGenerator(api_key=settings.OPENAI_API_KEY)

    for topic in pending_topics:
        try:
            add_log(f"Đang sinh bài viết cho: {topic.topic}")
            result = generator.generate_article(topic.topic)

            if "error" in result:
                add_log(f"Lỗi: {result['error']}", "error")
                continue

            try:
                connection.close()
                connection.ensure_connection()
            except Exception as e:
                add_log(f"Lỗi kết nối CSDL: {str(e)}")

            article = Article.objects.create(
                title=result.get("title"),
                slug=result.get("slug"),
                description=result.get("description", ""),
                content=result.get("content", ""),
                author=topic.author,
                is_published=True,
            )

            for kw in result.get("keywords", "").split(","):
                kw = kw.strip()
                if kw:
                    tag, _ = Tag.objects.get_or_create(name=kw)
                    article.tags.add(tag)

            topic.is_generated = True
            topic.save()

            add_log(f"Save success: {article.title}", "success")

        except Exception as e:
            add_log(f"'{topic.topic}': {e}", "error")
def enqueue_task(task):
    task_queue.put(task)

class Task:
    def __init__(self, name, callback, *args, **kwargs):
        self.name = name
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def run(self):
        add_log(f"Running: {self.name}", "error")
        self.callback(*self.args, **self.kwargs)

def start_worker():
    global worker_thread
    if not is_worker_running():

        add_log("Worker thread started.", "success")
        FlagManager.enable("worker_running")
        worker_thread = threading.Thread(target=worker_loop, daemon=True)
        worker_thread.start()
    else:
        add_log("Worker is already running.", "warning")

def stop_worker():
    if is_worker_running():
        add_log("Worker stopping...", "warning")
        FlagManager.disable("worker_running")
    else:
        add_log("Worker was not running.", "warning")

def is_worker_running():
    return FlagManager.is_enabled("worker_running")


def add_log(message, level="info", source="worker"):
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{level.upper()}] [{source}] {timestamp}: {message}")

    try:

        from dltik.models import ScheduledTopic, Article, Tag, SystemLog

        connection.close()
        connection.ensure_connection()

        SystemLog.objects.create(
            message=message,
            level=level,
            source=source
        )
    except OperationalError as e:
        print(f"[ERROR] [log-fail] DB error while logging: {e}")
    except Exception as e:
        print(f"[ERROR] [log-fail] Unknown error while logging: {e}")
