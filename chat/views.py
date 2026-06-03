from rest_framework.views import APIView
from rest_framework.response import Response
from pgvector.django import CosineDistance
from .models import DocumentChunk, ChatSession, ChatMessage
from .llm_service import get_embedding, generate_llm_response
import uuid


class ChatAPIView(APIView):
    def post(self, request):
        user_query = request.data.get('message')
        session_id = request.data.get('session_id')

        if not user_query:
            return Response({'status': 'error', 'reply': 'Пустой запрос'}, status=400)

        query_vector = get_embedding(user_query)

        if not query_vector:
            return Response({'status': 'error', 'reply': 'Ошибка сервиса векторизации.'}, status=500)

        relevant_chunks = DocumentChunk.objects.annotate(
            distance=CosineDistance('embedding', query_vector)
        ).order_by('distance')[:3]

        context_text = "\n\n".join([chunk.content for chunk in relevant_chunks])

        system_prompt = (
            f"Ты официальный интеллектуальный ассистент Восточно-Казахстанского регионального технопарка Алтай\n"
            f"Твоя основная задача - оказать информационную помощь резидентам и гостям технопарка в максимально вежливой, точной и профессиональной манере"
            f"СТРОГИЕ ПРАВИЛА:"
            f"\nОтвечайте на вопрос пользователя ТОЛЬКО на основе информации из раздела «КОНТЕКСТ» ниже."
            f"\nЕсли запрашиваемая информация полностью вырвана из контекста или неполна, не выдумывайте ничего собственного (не искажайте факты). Вместо этого отвечайте примерно так: «Извините, у меня нет конкретной информации по этому вопросу в базе данных. Пожалуйста, свяжитесь с управляющим технопарка для получения более полной и точной информации»."
            f"\nВаши ответы должны быть структурированными, логически разделенными и легко читаемыми (при необходимости используйте маркированные списки)."
            f"\nКОНТЕКСТ: {context_text}"
        )

        ai_response = generate_llm_response(system_prompt, user_query)

        if not session_id:
            session_id = str(uuid.uuid4())

        session, _ = ChatSession.objects.get_or_create(id=session_id)
        ChatMessage.objects.create(session=session, role='user', content=user_query)
        ChatMessage.objects.create(session=session, role='assistant', content=ai_response)

        # 7. Возвращаем ответ на сайт
        return Response({
            'status': 'success',
            'reply': ai_response,
            'session_id': str(session.id)
        })