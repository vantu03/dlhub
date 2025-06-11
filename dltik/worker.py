import threading, time, queue
from django.conf import settings
from django.utils import timezone
from dltik.models import ScheduledTopic, Article, Tag
from autowriter import ArticleGenerator

worker_running = False
worker_thread = None
task_queue = queue.Queue()
worker_logs = []

def worker_loop():
    global worker_running

    periodic_interval = 10
    next_periodic = time.time()

    while worker_running:
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
                from django.db import connection
                connection.close()
                connection.ensure_connection()
            except Exception as e:
                add_log(f"Lỗi kết nối CSDL: {str(e)}", "error")
                continue

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
    global worker_running, worker_thread
    if not worker_running:
        worker_running = True
        worker_thread = threading.Thread(target=worker_loop, daemon=True)
        worker_thread.start()
        add_log("Worker thread started.", "success")
    else:
        add_log("Worker is already running.", "warning")

def stop_worker():
    global worker_running
    if worker_running:
        worker_running = False
        add_log("Worker stopping...", "warning")
    else:
        add_log("Worker was not running.", "warning")

def is_worker_running():
    return worker_running

def add_log(message, level="info", max_pop=1000):
    log_entry = {
        "message": message,
        "level": level,
        "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    print(f"[{level.upper()}] {log_entry['timestamp']}: {message}")
    worker_logs.append(log_entry)

    if len(worker_logs) > max_pop:
        worker_logs.pop(0)
