import re
import string
import unicodedata
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import spacy
import nltk
from collections import Counter

class TextProcessor:
    def __init__(self):
        self.stop_words = self._load_portuguese_stop_words()
        self.task_keywords = self._load_task_keywords()
        self.priority_keywords = self._load_priority_keywords()
        self.time_keywords = self._load_time_keywords()
        
    def _load_portuguese_stop_words(self) -> set:
        """Load Portuguese stop words"""
        return {
            'a', 'à', 'ao', 'aos', 'aquela', 'aquelas', 'aquele', 'aqueles', 'aquilo',
            'as', 'até', 'com', 'como', 'da', 'das', 'de', 'dela', 'delas', 'dele',
            'deles', 'depois', 'do', 'dos', 'e', 'é', 'ela', 'elas', 'ele', 'eles',
            'em', 'entre', 'essa', 'essas', 'esse', 'esses', 'esta', 'está', 'estão',
            'estas', 'estava', 'estavam', 'este', 'estes', 'estive', 'estou', 'eu',
            'foi', 'fomos', 'for', 'foram', 'fosse', 'fossem', 'fui', 'há', 'isso',
            'isto', 'já', 'lhe', 'lhes', 'mais', 'mas', 'me', 'mesmo', 'meu', 'meus',
            'minha', 'minhas', 'muito', 'na', 'não', 'nas', 'nem', 'no', 'nos', 'nós',
            'nossa', 'nossas', 'nosso', 'nossos', 'num', 'numa', 'o', 'os', 'ou',
            'para', 'pela', 'pelas', 'pelo', 'pelos', 'por', 'qual', 'quando', 'que',
            'quem', 'são', 'se', 'sem', 'seu', 'seus', 'só', 'sua', 'suas', 'também',
            'te', 'tem', 'têm', 'teve', 'tive', 'todo', 'todos', 'tu', 'tua', 'tuas',
            'tudo', 'um', 'uma', 'umas', 'uns', 'você', 'vocês', 'vou'
        }
    
    def _load_task_keywords(self) -> Dict[str, List[str]]:
        """Load task-related keywords by category"""
        return {
            'creation': [
                'criar', 'fazer', 'desenvolver', 'construir', 'elaborar', 'produzir',
                'gerar', 'montar', 'organizar', 'planejar', 'preparar', 'iniciar'
            ],
            'study': [
                'estudar', 'aprender', 'revisar', 'ler', 'pesquisar', 'memorizar',
                'praticar', 'treinar', 'exercitar', 'compreender', 'analisar'
            ],
            'work': [
                'trabalhar', 'projeto', 'reunião', 'relatório', 'apresentação',
                'entrega', 'deadline', 'tarefa', 'atividade', 'demanda'
            ],
            'personal': [
                'exercício', 'treino', 'compras', 'casa', 'família', 'hobby',
                'lazer', 'descanso', 'saúde', 'bem-estar'
            ],
            'technology': [
                'programar', 'código', 'desenvolvimento', 'sistema', 'app',
                'website', 'software', 'bug', 'feature', 'deploy'
            ]
        }
    
    def _load_priority_keywords(self) -> Dict[str, List[str]]:
        """Load priority-related keywords"""
        return {
            'high': [
                'urgente', 'importante', 'crítico', 'prioritário', 'essencial',
                'fundamental', 'imediato', 'agora', 'hoje', 'rápido'
            ],
            'medium': [
                'normal', 'médio', 'regular', 'comum', 'padrão', 'depois',
                'amanhã', 'semana', 'moderado'
            ],
            'low': [
                'baixo', 'opcional', 'quando', 'possível', 'tempo', 'livre',
                'futuro', 'eventualmente', 'talvez'
            ]
        }
    
    def _load_time_keywords(self) -> Dict[str, List[str]]:
        """Load time-related keywords"""
        return {
            'immediate': ['agora', 'já', 'imediatamente', 'urgente'],
            'today': ['hoje', 'neste', 'momento', 'atual'],
            'tomorrow': ['amanhã', 'próximo', 'seguinte'],
            'week': ['semana', 'semanal', 'segunda', 'terça', 'quarta', 'quinta', 'sexta'],
            'month': ['mês', 'mensal', 'janeiro', 'fevereiro', 'março'],
            'morning': ['manhã', 'matinal', 'cedo'],
            'afternoon': ['tarde', 'vespertino'],
            'evening': ['noite', 'noturno', 'tarde']
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep Portuguese accents
        text = re.sub(r'[^\w\sáàãâéêíóôõúç]', ' ', text)
        
        # Remove extra spaces again
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """Extract meaningful keywords from text"""
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        
        # Filter out stop words and short words
        keywords = [
            word for word in words 
            if word not in self.stop_words 
            and len(word) >= min_length
            and not word.isdigit()
        ]
        
        return keywords
    
    def extract_task_category(self, text: str) -> Optional[str]:
        """Extract task category from text"""
        cleaned_text = self.clean_text(text)
        
        category_scores = {}
        for category, keywords in self.task_keywords.items():
            score = sum(1 for keyword in keywords if keyword in cleaned_text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def extract_priority(self, text: str) -> str:
        """Extract priority level from text"""
        cleaned_text = self.clean_text(text)
        
        priority_scores = {}
        for priority, keywords in self.priority_keywords.items():
            score = sum(1 for keyword in keywords if keyword in cleaned_text)
            if score > 0:
                priority_scores[priority] = score
        
        if priority_scores:
            return max(priority_scores.items(), key=lambda x: x[1])[0]
        
        return 'medium'
    
    def extract_time_references(self, text: str) -> List[str]:
        """Extract time references from text"""
        cleaned_text = self.clean_text(text)
        time_refs = []
        
        for time_type, keywords in self.time_keywords.items():
            for keyword in keywords:
                if keyword in cleaned_text:
                    time_refs.append(time_type)
                    break
        
        return list(set(time_refs))
    
    def extract_numbers(self, text: str) -> List[int]:
        """Extract numbers from text"""
        # Find digit numbers
        digit_numbers = [int(match) for match in re.findall(r'\d+', text)]
        
        # Find written numbers in Portuguese
        number_words = {
            'um': 1, 'uma': 1, 'dois': 2, 'duas': 2, 'três': 3, 'quatro': 4,
            'cinco': 5, 'seis': 6, 'sete': 7, 'oito': 8, 'nove': 9, 'dez': 10,
            'onze': 11, 'doze': 12, 'treze': 13, 'catorze': 14, 'quinze': 15,
            'dezesseis': 16, 'dezessete': 17, 'dezoito': 18, 'dezenove': 19,
            'vinte': 20, 'trinta': 30, 'quarenta': 40, 'cinquenta': 50
        }
        
        words = self.clean_text(text).split()
        written_numbers = [number_words[word] for word in words if word in number_words]
        
        return digit_numbers + written_numbers
    
    def extract_task_title(self, text: str, max_length: int = 50) -> str:
        """Extract a suitable task title from text"""
        # Remove common task creation phrases
        creation_phrases = [
            'criar tarefa', 'nova tarefa', 'adicionar tarefa', 'preciso fazer',
            'tenho que', 'vou fazer', 'quero', 'gostaria de'
        ]
        
        cleaned_text = self.clean_text(text)
        
        for phrase in creation_phrases:
            cleaned_text = cleaned_text.replace(phrase, '').strip()
        
        # Remove articles and prepositions from the beginning
        start_words_to_remove = ['de', 'da', 'do', 'das', 'dos', 'para', 'um', 'uma']
        words = cleaned_text.split()
        
        while words and words[0] in start_words_to_remove:
            words.pop(0)
        
        # Join words and limit length
        title = ' '.join(words)
        
        if len(title) > max_length:
            title = title[:max_length].rsplit(' ', 1)[0] + '...'
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        
        return title or "Nova tarefa"
    
    def calculate_text_complexity(self, text: str) -> Dict[str, Any]:
        """Calculate text complexity metrics"""
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        sentences = re.split(r'[.!?]+', text)
        
        metrics = {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'unique_words': len(set(words)),
            'complexity_score': 0.0
        }
        
        # Calculate complexity score (0-1)
        complexity_factors = [
            min(metrics['word_count'] / 20, 1.0),  # Word count factor
            min(metrics['avg_word_length'] / 8, 1.0),  # Average word length
            min(metrics['sentence_count'] / 3, 1.0),  # Sentence complexity
            metrics['unique_words'] / max(metrics['word_count'], 1)  # Vocabulary diversity
        ]
        
        metrics['complexity_score'] = sum(complexity_factors) / len(complexity_factors)
        
        return metrics
    
    def sentiment_analysis_basic(self, text: str) -> Dict[str, Any]:
        """Basic sentiment analysis for Portuguese"""
        positive_words = [
            'bom', 'ótimo', 'excelente', 'legal', 'incrível', 'perfeito', 'feliz',
            'animado', 'motivado', 'consegui', 'sucesso', 'vitória', 'conquista'
        ]
        
        negative_words = [
            'ruim', 'péssimo', 'difícil', 'impossível', 'cansado', 'triste',
            'frustrado', 'problema', 'erro', 'falha', 'não consigo', 'desanimado'
        ]
        
        neutral_words = [
            'ok', 'normal', 'regular', 'talvez', 'pode ser', 'não sei'
        ]
        
        cleaned_text = self.clean_text(text)
        
        positive_count = sum(1 for word in positive_words if word in cleaned_text)
        negative_count = sum(1 for word in negative_words if word in cleaned_text)
        neutral_count = sum(1 for word in neutral_words if word in cleaned_text)
        
        total_sentiment_words = positive_count + negative_count + neutral_count
        
        if total_sentiment_words == 0:
            sentiment = 'neutral'
            confidence = 0.5
        else:
            if positive_count > negative_count and positive_count > neutral_count:
                sentiment = 'positive'
                confidence = positive_count / total_sentiment_words
            elif negative_count > positive_count and negative_count > neutral_count:
                sentiment = 'negative'
                confidence = negative_count / total_sentiment_words
            else:
                sentiment = 'neutral'
                confidence = max(neutral_count, 1) / total_sentiment_words
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_words': positive_count,
            'negative_words': negative_count,
            'neutral_words': neutral_count
        }
    
    def extract_entities_basic(self, text: str) -> Dict[str, List[str]]:
        """Basic entity extraction"""
        entities = {
            'times': [],
            'dates': [],
            'durations': [],
            'locations': [],
            'technologies': []
        }
        
        # Time patterns
        time_pattern = r'\b(?:[01]?\d|2[0-3]):[0-5]\d\b'
        entities['times'] = re.findall(time_pattern, text)
        
        # Date patterns (basic)
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{1,2}-\d{1,2}-\d{4}\b'
        ]
        for pattern in date_patterns:
            entities['dates'].extend(re.findall(pattern, text))
        
        # Duration patterns
        duration_pattern = r'\b\d+\s*(?:minutos?|horas?|dias?|semanas?|meses?)\b'
        entities['durations'] = re.findall(duration_pattern, text.lower())
        
        # Technology keywords
        tech_keywords = [
            'python', 'javascript', 'react', 'node', 'api', 'database',
            'github', 'git', 'docker', 'aws', 'frontend', 'backend'
        ]
        cleaned_text = self.clean_text(text)
        entities['technologies'] = [tech for tech in tech_keywords if tech in cleaned_text]
        
        return entities
    
    def suggest_task_breakdown(self, text: str) -> List[str]:
        """Suggest how to break down a complex task"""
        complexity = self.calculate_text_complexity(text)
        
        # If task seems complex, suggest breakdown
        if complexity['complexity_score'] > 0.7 or complexity['word_count'] > 15:
            breakdown_suggestions = []
            
            # Look for action verbs that suggest multiple steps
            action_verbs = [
                'pesquisar', 'estudar', 'planejar', 'desenvolver', 'testar',
                'revisar', 'implementar', 'documentar', 'apresentar'
            ]
            
            found_actions = [verb for verb in action_verbs if verb in self.clean_text(text)]
            
            if len(found_actions) > 1:
                breakdown_suggestions = [f"Etapa: {verb.capitalize()}" for verb in found_actions[:4]]
            elif complexity['word_count'] > 20:
                # Generic breakdown for long tasks
                breakdown_suggestions = [
                    "Fase de planejamento",
                    "Execução principal",
                    "Revisão e finalização"
                ]
            
            return breakdown_suggestions
        
        return []
