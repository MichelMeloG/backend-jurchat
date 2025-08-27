import openai
import os
import time
import asyncio
from typing import Dict, List, Any
import logging
from config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered document analysis and chat"""
    
    def __init__(self):
        # Initialize OpenAI client
        self.client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY
        )
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.MAX_TOKENS
        
        # Legal domain prompts
        self.system_prompts = {
            'summary': """Você é um assistente jurídico especializado em analisar documentos legais.
Sua tarefa é criar um resumo claro e compreensível do documento fornecido, usando linguagem simples
que possa ser entendida por pessoas sem formação jurídica.

Instruções:
1. Identifique o tipo de documento (contrato, lei, decisão judicial, etc.)
2. Destaque os pontos principais e mais importantes
3. Explique termos jurídicos complexos em linguagem simples
4. Organize o resumo de forma lógica e estruturada
5. Mantenha o tom professional mas acessível""",

            'chat': """Você é um assistente jurídico especializado que ajuda usuários a entender documentos legais.
Você tem acesso ao texto completo do documento e deve responder perguntas baseando-se nele.

Diretrizes:
1. Seja preciso e cite partes específicas do documento quando relevante
2. Use linguagem clara e evite jargão jurídico desnecessário
3. Se a pergunta não puder ser respondida com base no documento, diga isso claramente
4. Forneça contexto legal quando apropriado
5. Seja útil e educativo em suas respostas"""
        }
    
    async def generate_summary(self, text: str, document_type: str = "legal") -> Dict[str, Any]:
        """
        Generate AI summary of document text
        """
        start_time = time.time()
        
        try:
            # Prepare prompt
            user_prompt = f"""
Documento para análise:

{text[:8000]}  # Limit text to avoid token limits

Por favor, forneça um resumo abrangente deste documento jurídico.
"""

            # Call OpenAI API
            response = await self._call_openai_async(
                messages=[
                    {"role": "system", "content": self.system_prompts['summary']},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens
            )
            
            processing_time = time.time() - start_time
            
            return {
                "summary": response['content'],
                "tokens_used": response['tokens_used'],
                "processing_time": processing_time,
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
    
    async def generate_chat_response(
        self, 
        user_message: str, 
        document_content: str, 
        document_summary: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response for chat with document context
        """
        try:
            # Prepare conversation context
            messages = [
                {"role": "system", "content": self.system_prompts['chat']}
            ]
            
            # Add document context
            context_message = f"""
Contexto do Documento:
Resumo: {document_summary}

Texto completo (primeiros 6000 caracteres):
{document_content[:6000]}

---
"""
            messages.append({"role": "system", "content": context_message})
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages
                    if msg['role'] in ['user', 'assistant']:
                        messages.append({
                            "role": msg['role'], 
                            "content": msg['content']
                        })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = await self._call_openai_async(
                messages=messages,
                max_tokens=1500
            )
            
            return {
                "response": response['content'],
                "tokens_used": response['tokens_used'],
                "metadata": {
                    "model_used": self.model,
                    "context_length": len(document_content),
                    "conversation_length": len(conversation_history) if conversation_history else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            raise
    
    async def analyze_document(
        self, 
        document_content: str, 
        document_type: str,
        analysis_type: str
    ) -> Dict[str, Any]:
        """
        Perform specific analysis on document
        """
        analysis_prompts = {
            'key_terms': "Identifique e explique os termos jurídicos mais importantes neste documento.",
            'obligations': "Liste todas as obrigações e responsabilidades mencionadas no documento.",
            'risks': "Identifique possíveis riscos ou pontos de atenção neste documento.",
            'deadlines': "Extraia todas as datas, prazos e cronogramas mencionados.",
            'parties': "Identifique todas as partes envolvidas e seus papéis."
        }
        
        if analysis_type not in analysis_prompts:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
        
        try:
            prompt = analysis_prompts[analysis_type]
            
            messages = [
                {
                    "role": "system", 
                    "content": f"Você é um especialista em análise de documentos jurídicos. {prompt}"
                },
                {
                    "role": "user", 
                    "content": f"Analise este documento:\n\n{document_content[:7000]}"
                }
            ]
            
            response = await self._call_openai_async(
                messages=messages,
                max_tokens=1500
            )
            
            return {
                "analysis_type": analysis_type,
                "result": response['content'],
                "tokens_used": response['tokens_used']
            }
            
        except Exception as e:
            logger.error(f"Error in document analysis: {str(e)}")
            raise
    
    async def _call_openai_async(self, messages: List[Dict], max_tokens: int = None) -> Dict[str, Any]:
        """
        Make async call to OpenAI API
        """
        try:
            # For demo purposes, we'll simulate the API call
            # In production, use the actual OpenAI API
            
            # Simulate API delay
            await asyncio.sleep(1)
            
            # Mock response - replace with actual OpenAI call
            if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your-openai-api-key':
                # Real API call
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens or self.max_tokens,
                    temperature=0.7
                )
                
                return {
                    "content": response.choices[0].message.content,
                    "tokens_used": response.usage.total_tokens
                }
            else:
                # Mock response for demo
                return {
                    "content": "Esta é uma resposta simulada da IA. Configure a chave da API OpenAI para respostas reais.",
                    "tokens_used": 150
                }
                
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get list of available AI models"""
        return [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo-preview"
        ]
    
    def get_current_model(self) -> str:
        """Get current AI model"""
        return self.model
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
