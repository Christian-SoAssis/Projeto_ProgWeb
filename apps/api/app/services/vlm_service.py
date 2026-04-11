import json
from typing import List, Optional, Dict, Any
from google import genai
from google.genai import types
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

CATEGORIES = [
    "Hidráulica", "Elétrica", "Gás", "Construção", "Jardinagem", "Limpeza", 
    "Pintura", "Marcenaria", "Ar-condicionado", "Segurança", "Tecnologia", 
    "Reformas", "Saúde/Beleza", "Jurídico", "Educação", "Pets"
]

SYSTEM_PROMPT = f"""
Você é um especialista em classificação de serviços para um marketplace brasileiro chamado ServiçoJá.
Sua tarefa é analisar imagens de pedidos de serviço e extrair informações técnicas estruturadas.

REGRAS OBRIGATÓRIAS:
1. CLASSIFICAÇÃO: Você DEVE escolher a categoria mais adequada APENAS entre estas 16: {', '.join(CATEGORIES)}.
2. COMPLEXIDADE: Classifique como 'simple' (reparo rápido), 'medium' (exige ferramentas/tempo) ou 'complex' (reforma/projeto grande).
3. URGÊNCIA: Classifique como 'low' (estético/manutenção), 'medium' (funcional mas não crítico) ou 'high' (vazamento, risco elétrico, segurança).
4. ESPECIALIDADES: Liste até 5 termos técnicos (ex: "Troca de fiação", "Pintura de teto", "Desentupimento") que descrevam o serviço.

SAÍDA:
Retorne APENAS um objeto JSON com o seguinte formato:
{{
    "category": "Nome da Categoria",
    "ai_complexity": "simple|medium|complex",
    "ai_urgency": "low|medium|high",
    "ai_specialties": ["especialidade 1", "especialidade 2"]
}}
"""

class VLMService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model_id = settings.GEMINI_MODEL

    async def analyze_images(self, image_contents: List[bytes]) -> Dict[str, Any]:
        """
        Analisa uma ou mais imagens usando Gemini Vision para extrair metadados do pedido.
        """
        try:
            # Preparar as imagens para o Gemini
            contents = []
            for img_bytes in image_contents:
                contents.append(types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"))
            
            # Adicionar o prompt
            contents.append(types.Part.from_text(text="Analise estas imagens e retorne o JSON conforme as instruções."))

            # Chamada ao modelo
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json"
                )
            )

            # Parsing manual da resposta
            if not response.text:
                raise ValueError("Resposta vazia do Gemini")
            
            result = json.loads(response.text)
            
            # Validação básica de categorias (garantir que respeitou a lista)
            if result.get("category") not in CATEGORIES:
                logger.warning(f"IA sugeriu categoria fora da lista: {result.get('category')}. Usando fallback.")
                # Opcional: tentar encontrar a mais próxima ou deixar nulo
            
            return result

        except Exception as e:
            logger.error(f"Erro na análise VLM: {str(e)}")
            # Retorno de fallback seguro em caso de erro da API
            return {
                "category": None,
                "ai_complexity": "medium",
                "ai_urgency": "medium",
                "ai_specialties": []
            }

vlm_service = VLMService()
