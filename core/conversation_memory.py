import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import structlog
import re

logger = structlog.get_logger(__name__)

class ConversationMemory:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.short_term_memory = {}
    
    async def save_conversation(self, user_id: str, user_message: str, lumi_response: str, context_data: Dict[str, Any] = None):
        try:
            current_memory = await self.get_lumi_memory(user_id)
            
            if not current_memory:
                current_memory = {}
            
            if not user_message:
                logger.warning(f"user_message é None para usuário {user_id}")
                return
            
            new_conversation = {
                "timestamp": datetime.now().isoformat(),
                "userMessage": user_message,
                "lumiResponse": lumi_response or "",
                "context": context_data.get("detected_context", "general") if context_data else "general",
                "mood": context_data.get("lumi_mood", "encouraging") if context_data else "encouraging",
                "effectiveness": None,
                "topics": context_data.get("topics", []) if context_data else [],
                "sentiment": context_data.get("user_sentiment", "encouraging") if context_data else "encouraging"
            }
            
            conversation_history = current_memory.get("conversationHistory", [])
            if isinstance(conversation_history, str):
                try:
                    conversation_history = json.loads(conversation_history)
                except:
                    conversation_history = []
            
            conversation_history.append(new_conversation)
            
            if len(conversation_history) > 50:
                conversation_history = conversation_history[-50:]
            
            await self._update_lumi_memory(user_id, conversation_history, context_data)
            
            logger.info(f"Conversa salva para usuário {user_id}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar conversa: {str(e)}")
    
    async def get_lumi_memory(self, user_id: str) -> Optional[Dict]:
        try:
            query = """
                SELECT "userId", "conversationHistory", "userPersonality", 
                       "currentMood", "behaviorPatterns", "preferredTopics", 
                       "communicationStyle", "adaptationLevel", "lastInteraction", 
                       "contextualHabits", "emotionalState", "goalOrientation", "createdAt", "updatedAt"
                FROM lumi_memory 
                WHERE "userId" = $1
            """
            result = await self.db_manager.execute_query(query, [user_id])
            
            if result and len(result) > 0:
                memory_data = result[0]
                return {
                    "userId": memory_data.get("userId"),
                    "conversationHistory": memory_data.get("conversationHistory", []),
                    "userPersonality": memory_data.get("userPersonality", {}),
                    "currentMood": memory_data.get("currentMood", "encouraging"),
                    "behaviorPatterns": memory_data.get("behaviorPatterns", {}),
                    "preferredTopics": memory_data.get("preferredTopics", []),
                    "communicationStyle": memory_data.get("communicationStyle", "friendly"),
                    "adaptationLevel": memory_data.get("adaptationLevel", 1),
                    "lastInteraction": memory_data.get("lastInteraction"),
                    "contextualHabits": memory_data.get("contextualHabits", {}),
                    "emotionalState": memory_data.get("emotionalState", "encouraging"),
                    "goalOrientation": memory_data.get("goalOrientation", []),
                    "createdAt": memory_data.get("createdAt"),
                    "updatedAt": memory_data.get("updatedAt")
                }
            else:
                return await self._create_initial_memory(user_id)
                
        except Exception as e:
            logger.error(f"Erro ao buscar memória da Lumi: {str(e)}")
            return None
    
    async def _create_initial_memory(self, user_id: str) -> Dict:
        try:
            initial_memory = {
                "userId": user_id,
                "conversationHistory": [],
                "userPersonality": {},
                "currentMood": "encouraging",
                "behaviorPatterns": {},
                "preferredTopics": [],
                "communicationStyle": "friendly",
                "adaptationLevel": 1,
                "lastInteraction": datetime.now().isoformat(),
                "contextualHabits": {},
                "emotionalState": "encouraging",
                "goalOrientation": []
            }
            
            query = """
                INSERT INTO lumi_memory (
                    "userId", "conversationHistory", "userPersonality", 
                    "currentMood", "behaviorPatterns", "preferredTopics",
                    "communicationStyle", "adaptationLevel", "lastInteraction",
                    "contextualHabits", "emotionalState", "goalOrientation",
                    "createdAt", "updatedAt"
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                RETURNING *
            """
            
            result = await self.db_manager.execute_query(query, [
                user_id,
                json.dumps(initial_memory["conversationHistory"]),
                json.dumps(initial_memory["userPersonality"]),
                initial_memory["currentMood"],
                json.dumps(initial_memory["behaviorPatterns"]),
                json.dumps(initial_memory["preferredTopics"]),
                initial_memory["communicationStyle"],
                initial_memory["adaptationLevel"],
                initial_memory["lastInteraction"],
                json.dumps(initial_memory["contextualHabits"]),
                initial_memory["emotionalState"],
                json.dumps(initial_memory["goalOrientation"]),
                datetime.now(),
                datetime.now()
            ])
            
            if result:
                logger.info(f"Memória inicial criada para usuário {user_id}")
                return initial_memory
            else:
                logger.error(f"Falha ao criar memória inicial para usuário {user_id}")
                return initial_memory
                
        except Exception as e:
            logger.error(f"Erro ao criar memória inicial: {str(e)}")
            return None
    
    async def _update_lumi_memory(self, user_id: str, conversation_history: List[Dict], context_data: Dict[str, Any] = None):
        try:
            current_memory = await self.get_lumi_memory(user_id)
            if not current_memory:
                current_memory = await self._create_initial_memory(user_id)
            
            if not current_memory:
                logger.error(f"Não foi possível obter memória para usuário {user_id}")
                return
            
            updated_mood = context_data.get("lumi_mood", current_memory.get("currentMood", "encouraging")) if context_data else current_memory.get("currentMood", "encouraging")
            updated_emotional_state = context_data.get("user_sentiment", current_memory.get("emotionalState", "encouraging")) if context_data else current_memory.get("emotionalState", "encouraging")
            
            query = """
                UPDATE lumi_memory 
                SET "conversationHistory" = $2,
                    "currentMood" = $3,
                    "emotionalState" = $4,
                    "lastInteraction" = $5,
                    "updatedAt" = $6
                WHERE "userId" = $1
            """
            
            await self.db_manager.execute_query(query, [
                user_id,
                json.dumps(conversation_history),
                updated_mood,
                updated_emotional_state,
                datetime.now().isoformat(),
                datetime.now()
            ])
            
            logger.info(f"Memória da Lumi atualizada para usuário {user_id}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar memória da Lumi: {str(e)}")
    
    async def update_behavior_patterns(self, user_id: str, new_patterns: Dict[str, Any]):
        try:
            current_memory = await self.get_lumi_memory(user_id)
            if not current_memory:
                logger.warning(f"Memória não encontrada para usuário {user_id}")
                return
            
            current_patterns = current_memory.get("behaviorPatterns", {})
            if isinstance(current_patterns, str):
                try:
                    current_patterns = json.loads(current_patterns)
                except:
                    current_patterns = {}
            
            current_patterns.update(new_patterns)
            
            query = """
                UPDATE lumi_memory 
                SET "behaviorPatterns" = $2, "updatedAt" = $3
                WHERE "userId" = $1
            """
            
            await self.db_manager.execute_query(query, [
                user_id,
                json.dumps(current_patterns),
                datetime.now()
            ])
            
            logger.info(f"Padrões de comportamento atualizados para usuário {user_id}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar padrões de comportamento: {str(e)}")
    
    async def get_conversation_context(self, user_id: str, limit: int = 5) -> List[Dict]:
        try:
            memory = await self.get_lumi_memory(user_id)
            if not memory:
                return []
            
            conversation_history = memory.get("conversationHistory", [])
            if isinstance(conversation_history, str):
                try:
                    conversation_history = json.loads(conversation_history)
                except:
                    conversation_history = []
            
            return conversation_history[-limit:] if conversation_history else []
            
        except Exception as e:
            logger.error(f"Erro ao buscar contexto de conversa: {str(e)}")
            return []
    
    async def extract_user_info(self, user_message: str) -> Dict[str, Any]:
        try:
            user_info = {}
            
            name_patterns = [
                r"meu nome é (\w+)",
                r"me chamo (\w+)",
                r"sou (\w+)",
                r"eu sou (\w+)"
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, user_message.lower())
                if match:
                    user_info["name"] = match.group(1).title()
                    break
            
            if "estudar" in user_message.lower():
                user_info["interests"] = user_info.get("interests", []) + ["estudo"]
            
            if "trabalho" in user_message.lower():
                user_info["interests"] = user_info.get("interests", []) + ["trabalho"]
            
            return user_info
            
        except Exception as e:
            logger.error(f"Erro ao extrair informações do usuário: {str(e)}")
            return {}
    
    async def get_user_name(self, user_id: str) -> Optional[str]:
        try:
            memory = await self.get_lumi_memory(user_id)
            if not memory:
                return None
            
            conversation_history = memory.get("conversationHistory", [])
            if isinstance(conversation_history, str):
                try:
                    conversation_history = json.loads(conversation_history)
                except:
                    conversation_history = []
            
            for conversation in conversation_history:
                user_message = conversation.get("userMessage", "").lower()
                
                name_patterns = [
                    r"meu nome é (\w+)",
                    r"me chamo (\w+)",
                    r"sou (\w+)",
                                    r"eu sou (\w+)"
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, user_message)
                    if match:
                        return match.group(1).title()
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar nome do usuário: {str(e)}")
            return None

_conversation_memory = None

def get_conversation_memory():
    global _conversation_memory
    if _conversation_memory is None:
        from core.database_manager import db_manager
        _conversation_memory = ConversationMemory(db_manager)
    return _conversation_memory