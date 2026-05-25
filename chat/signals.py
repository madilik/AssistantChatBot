from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Document, DocumentChunk
from .llm_service import get_embedding


@receiver(post_save, sender=Document)
def create_document_chunks(sender, instance, **kwargs):
    DocumentChunk.objects.filter(document=instance).delete()

    if instance.is_active and instance.content:
        paragraphs = [p.strip() for p in instance.content.split('\n\n') if p.strip()]

        chunks_to_create = []
        for para in paragraphs:
            embedding = get_embedding(para)
            if embedding:
                chunks_to_create.append(
                    DocumentChunk(
                        document=instance,
                        content=para,
                        embedding=embedding
                    )
                )
            else:
                print("ОШИБКА: Не удалось получить вектор. Проверь API ключ и интернет!")

        if chunks_to_create:
            DocumentChunk.objects.bulk_create(chunks_to_create)