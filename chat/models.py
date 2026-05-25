from django.db import models
from pgvector.django import VectorField
import uuid

# --- ДОМЕН: База знаний ---

class Document(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название документа")
    content = models.TextField(verbose_name="Текст документа (Регламент, FAQ)", default="")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"


class DocumentChunk(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks',
        verbose_name="Документ"
    )
    content = models.TextField(verbose_name="Текст фрагмента")
    embedding = VectorField(
        dimensions=3072,
        verbose_name="Векторное представление",
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Фрагмент из {self.document.title} ({self.id})"

    class Meta:
        verbose_name = "Фрагмент документа"
        verbose_name_plural = "Фрагменты документов"
        # Индекс HNSW для сверхбыстрого векторного поиска
        # indexes = [
        #     models.Index(fields=['embedding'], name='embedding_hnsw_idx')
        # ]


# --- ДОМЕН: Диалоги ---

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата начала")

    def __str__(self):
        return f"Сессия {self.id}"

    class Meta:
        verbose_name = "Сессия чата"
        verbose_name_plural = "Сессии чатов"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('assistant', 'Ассистент'),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Сессия"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="Роль")
    content = models.TextField(verbose_name="Текст сообщения")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время")

    def __str__(self):
        return f"{self.role}: {self.content[:30]}..."

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['timestamp']