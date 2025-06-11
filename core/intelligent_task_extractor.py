"""
Sistema de Extração Inteligente de Tarefas
Detecta automaticamente quando o usuário quer criar uma tarefa e extrai todos os detalhes
"""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class TaskIntent:
    """Dados extraídos de uma intenção de criação de tarefa"""
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    time: Optional[str] = None
    priority: str = "medium"
    estimated_pomodoros: int = 1
    confidence: float = 0.0
    extracted_entities: Dict[str, Any] = field(default_factory=dict)

class IntelligentTaskExtractor:
    def __init__(self):
        self.time_patterns = self._init_time_patterns()
        self.priority_patterns = self._init_priority_patterns()
        self.task_patterns = self._init_task_patterns()
    
    def _init_time_patterns(self) -> Dict[str, str]:
        """Padrões para detectar tempo"""
        return {
            # Horários específicos
            r'(\d{1,2}):(\d{2})': 'specific_time',
            r'às (\d{1,2}):(\d{2})': 'at_specific_time',
            r'(\d{1,2})h(\d{2})?': 'hour_format',
            r'às (\d{1,2})h(\d{2})?': 'at_hour_format',
            r'às (\d{1,2})': 'at_hour',
            
            # Dias relativos
            r'amanhã': 'tomorrow',
            r'hoje': 'today',
            r'depois de amanhã': 'day_after_tomorrow',
            
            # Dias da semana
            r'segunda': 'monday',
            r'terça': 'tuesday', 
            r'quarta': 'wednesday',
            r'quinta': 'thursday',
            r'sexta': 'friday',
            r'sábado': 'saturday',
            r'domingo': 'sunday',
            
            # Períodos
            r'manhã': 'morning',
            r'tarde': 'afternoon',
            r'noite': 'evening'
        }
    
    def _init_priority_patterns(self) -> Dict[str, str]:
        """Padrões para detectar prioridade"""
        return {
            r'urgente|crítico|importante': 'high',
            r'rápido|agora|já': 'high',
            r'quando der|depois|mais tarde': 'low',
            r'normal|comum': 'medium'
        }
    
    def _init_task_patterns(self) -> List[Dict[str, Any]]:
        """Padrões para extrair diferentes tipos de tarefa"""
        return [
            # Padrões de configuração/setup - MOVIDO PARA CIMA para maior prioridade
            {
                'pattern': r'(?:preciso|tenho que|vou|quero) (?:configurar|instalar|implementar|setup) (.+?)(?:\s+(?:hoje|amanhã|às|até|\d)|$)',
                'task_type': 'configuration',
                'title_template': 'Configurar {system}',
                'default_duration': 3
            },
            {
                'pattern': r'(?:configurar|instalar|implementar|setup) (?:o |a )?(.+?)(?:\s+(?:hoje|amanhã|às|até|\d)|$)',
                'task_type': 'configuration',
                'title_template': 'Configurar {system}',
                'default_duration': 3
            },
            
            # Padrões de estudo
            {
                'pattern': r'(?:preciso|tenho que|vou|quero) estudar (.+?)(?:\s+(?:hoje|amanhã|às|até|\d)|$)',
                'task_type': 'study',
                'title_template': 'Estudar {subject}',
                'default_duration': 2
            },
            {
                'pattern': r'estudar (.+?)(?:\s+(?:hoje|amanhã|às|até|\d)|$)',
                'task_type': 'study',
                'title_template': 'Estudar {subject}',
                'default_duration': 2
            },
            
            # Padrões de finalização
            {
                'pattern': r'(?:preciso|tenho que|vou|quero) (?:terminar|concluir|finalizar) (.+?)(?:\s+(?:hoje|amanhã|às|até|\d)|$)',
                'task_type': 'completion',
                'title_template': 'Terminar {task}',
                'default_duration': 2
            },
            {
                'pattern': r'(?:terminar|concluir|finalizar) (?:a |o |de )?(.+?)(?:\s+(?:hoje|amanhã|às|até|\d)|$)',
                'task_type': 'completion',
                'title_template': 'Terminar {task}',
                'default_duration': 2
            },
            
            # Padrões de reunião
            {
                'pattern': r'reunião (com|sobre) (.+?)(?:\s+(?:hoje|amanhã|às|até|\d)|$)',
                'task_type': 'meeting',
                'title_template': 'Reunião {details}',
                'default_duration': 1
            },
            
            # Padrões gerais - mais abrangentes
            {
                'pattern': r'(?:preciso|tenho que|vou|quero) (.+?)(?:\s+(?:hoje|amanhã|às|até|\d)|$)',
                'task_type': 'general',
                'title_template': '{activity}',
                'default_duration': 1
            },
            {
                'pattern': r'(?:fazer|realizar|executar) (?:a |o |de )?(.+?)(?:\s+(?:hoje|amanhã|às|até|\d)|$)',
                'task_type': 'general',
                'title_template': 'Fazer {activity}',
                'default_duration': 1
            }
        ]

    def extract_task_from_message(self, message: str) -> Optional[TaskIntent]:
        """Extrai informações de tarefa de uma mensagem natural"""
        message_lower = message.lower()
        
        # Verificar se é intenção de criar tarefa
        task_keywords = [
            'adicione na minha agenda', 'agendar', 'marcar para', 'programar',
            'estudar', 'fazer', 'trabalhar em', 'reunião', 'compromisso',
            'lembrar de', 'não esquecer de', 'preciso', 'tenho que',
            'configurar', 'instalar', 'implementar', 'setup', 'terminar',
            'concluir', 'finalizar', 'completar', 'resolver', 'executar',
            'realizar', 'desenvolver', 'criar', 'construir', 'montar'
        ]
        
        has_task_intent = any(keyword in message_lower for keyword in task_keywords)
        if not has_task_intent:
            return None
        
        # Extrair entidades
        extracted_time = self._extract_time(message_lower)
        extracted_priority = self._extract_priority(message_lower)
        task_details = self._extract_task_details(message_lower)
        
        if not task_details:
            return None
        
        # Criar intent
        task_intent = TaskIntent(
            title=task_details['title'],
            description=task_details.get('description'),
            due_date=extracted_time.get('date') if extracted_time else None,
            time=extracted_time.get('time') if extracted_time else None,
            priority=extracted_priority,
            estimated_pomodoros=task_details.get('duration', 1),
            confidence=0.9,
            extracted_entities={
                'time_info': extracted_time,
                'original_message': message,
                'task_type': task_details.get('type', 'general')
            }
        )
        
        logger.info(f"✅ Tarefa extraída: {task_intent.title}")
        return task_intent
    
    def _extract_time(self, message: str) -> Optional[Dict[str, str]]:
        """Extrai informações de tempo da mensagem"""
        result = {}
        
        # Procurar horários específicos primeiro
        for pattern, time_type in self.time_patterns.items():
            match = re.search(pattern, message)
            if match:
                if time_type == 'tomorrow':
                    tomorrow = datetime.now() + timedelta(days=1)
                    result['date'] = tomorrow.strftime('%Y-%m-%d')
                elif time_type == 'today':
                    result['date'] = datetime.now().strftime('%Y-%m-%d')
                
                result['type'] = time_type
                break
        
        return result if result else None
    
    def _extract_priority(self, message: str) -> str:
        """Extrai prioridade da mensagem"""
        for pattern, priority in self.priority_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                return priority
        return 'medium'
    
    def _extract_task_details(self, message: str) -> Optional[Dict[str, Any]]:
        """Extrai detalhes específicos da tarefa"""
        for task_pattern in self.task_patterns:
            match = re.search(task_pattern['pattern'], message, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if task_pattern['task_type'] == 'configuration':
                    system = groups[0]
                    return {
                        'title': f"Configurar {system.title()}",
                        'description': f"Configuração: {system}",
                        'duration': task_pattern['default_duration'],
                        'type': 'configuration'
                    }
                elif task_pattern['task_type'] == 'study':
                    subject = groups[0]
                    return {
                        'title': f"Estudar {subject.title()}",
                        'description': f"Sessão de estudos de {subject}",
                        'duration': task_pattern['default_duration'],
                        'type': 'study'
                    }
                elif task_pattern['task_type'] == 'completion':
                    task = groups[0]
                    return {
                        'title': f"Terminar {task.title()}",
                        'description': f"Finalizar: {task}",
                        'duration': task_pattern['default_duration'],
                        'type': 'completion'
                    }
                elif task_pattern['task_type'] == 'meeting':
                    details = ' '.join(groups)
                    return {
                        'title': f"Reunião {details}",
                        'description': f"Reunião: {details}",
                        'duration': task_pattern['default_duration'],
                        'type': 'meeting'
                    }
                elif task_pattern['task_type'] == 'general':
                    activity = groups[0]
                    return {
                        'title': activity.title(),
                        'description': f"Tarefa: {activity}",
                        'duration': task_pattern['default_duration'],
                        'type': 'general'
                    }
        
        return None

# Instância global para uso
task_extractor = IntelligentTaskExtractor()
