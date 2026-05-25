from django.contrib import admin
from .models import Document, DocumentChunk, ChatSession, ChatMessage


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'uploaded_at')
    search_fields = ('title', 'content')
    list_filter = ('is_active',)


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'content_snippet', 'created_at')
    readonly_fields = ('document', 'content', 'embedding_preview')
    exclude = ('embedding',)

    def content_snippet(self, obj):
        return obj.content[:75] + "..."

    content_snippet.short_description = 'Текст фрагмента'

    # Создаем безопасный метод для отображения кусочка вектора
    def embedding_preview(self, obj):
        if obj.embedding is not None:
            vec = list(obj.embedding)
            return f"Вектор успешно загружен ({len(vec)} мерностей). Начало: {vec[:5]}..."
        return "Вектор отсутствует"

    embedding_preview.short_description = 'Векторное представление'


admin.site.register(ChatSession)
admin.site.register(ChatMessage)