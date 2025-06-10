from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class IntentType(str, Enum):
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    START_POMODORO = "start_pomodoro"
    CHECK_PROGRESS = "check_progress"
    GET_SUGGESTIONS = "get_suggestions"
    MOTIVATIONAL_CHAT = "motivational_chat"
    CELEBRATE_ACHIEVEMENT = "celebrate_achievement"
    PRODUCTIVITY_INSIGHTS = "productivity_insights"
    MODIFY_SCHEDULE = "modify_schedule"
    REQUEST_HELP = "request_help"
    UNKNOWN = "unknown"

class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    MOTIVATED = "motivated"
    TIRED = "tired"

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ContextAnalysisModel(BaseModel):
    intent: IntentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    entities: Dict[str, Any] = Field(default_factory=dict)
    sentiment: SentimentType = SentimentType.NEUTRAL
    urgency_level: UrgencyLevel = UrgencyLevel.MEDIUM
    suggested_actions: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time_ms: float = 0.0
    
class EntityModel(BaseModel):
    type: str
    value: Any
    confidence: float = Field(..., ge=0.0, le=1.0)
    position: Optional[Dict[str, int]] = None  # start, end positions in text
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ActionSuggestionModel(BaseModel):
    action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0)
    description: str
    expected_outcome: str
    priority: int = Field(1, ge=1, le=10)

class TaskComplexityModel(BaseModel):
    estimated_pomodoros: int = Field(..., ge=1, le=20)
    confidence: float = Field(..., ge=0.0, le=1.0)
    complexity_factors: List[str] = Field(default_factory=list)
    based_on_similar_tasks: int = 0
    user_accuracy_factor: float = 1.0
    difficulty_level: str = "medium"  # easy, medium, hard, expert
    learning_curve: bool = False
    dependencies: List[str] = Field(default_factory=list)
    
class TimingOptimizationModel(BaseModel):
    optimal_hours: List[int] = Field(default_factory=list)
    optimal_days: List[str] = Field(default_factory=list)
    next_available_slots: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning: str = ""
    confidence: float = Field(..., ge=0.0, le=1.0)
    productivity_score: float = Field(..., ge=0.0, le=1.0)
    energy_alignment: str = "medium"  # low, medium, high
    
class TaskOptimizationModel(BaseModel):
    task_id: str
    current_status: str
    optimization_type: str
    suggested_changes: Dict[str, Any] = Field(default_factory=dict)
    expected_improvement: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    implementation_difficulty: str = "easy"  # easy, medium, hard
    estimated_time_saved_minutes: Optional[int] = None
    
class TaskSuggestionModel(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=1000)
    priority: str = "medium"
    estimated_pomodoros: int = Field(..., ge=1, le=20)
    reasoning: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    expected_benefits: List[str] = Field(default_factory=list)
    
class BehavioralPatternModel(BaseModel):
    pattern_type: str
    description: str
    frequency: str  # daily, weekly, monthly, occasional
    strength: float = Field(..., ge=0.0, le=1.0)
    first_observed: datetime
    last_observed: datetime
    examples: List[str] = Field(default_factory=list)
    implications: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
class ProductivityPhaseModel(BaseModel):
    phase_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    characteristics: List[str] = Field(default_factory=list)
    productivity_score: float = Field(..., ge=0.0, le=1.0)
    mood_state: str = "neutral"
    key_activities: List[str] = Field(default_factory=list)
    energy_level: float = Field(..., ge=0.0, le=1.0)
    focus_quality: float = Field(..., ge=0.0, le=1.0)
    
class LearningInsightModel(BaseModel):
    insight_type: str
    title: str
    description: str
    learning_source: str  # user_behavior, feedback, pattern_analysis
    confidence: float = Field(..., ge=0.0, le=1.0)
    actionable_recommendations: List[str] = Field(default_factory=list)
    supporting_data: Dict[str, Any] = Field(default_factory=dict)
    discovered_at: datetime = Field(default_factory=datetime.now)
    validated: bool = False
    impact_potential: str = "medium"  # low, medium, high
    
class PersonalizationModel(BaseModel):
    user_id: str
    personality_traits: Dict[str, float] = Field(default_factory=dict)
    communication_preferences: Dict[str, Any] = Field(default_factory=dict)
    motivation_triggers: List[str] = Field(default_factory=list)
    response_patterns: Dict[str, Any] = Field(default_factory=dict)
    adaptation_history: List[Dict[str, Any]] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)
    effectiveness_score: float = Field(0.5, ge=0.0, le=1.0)
    
class InteractionContextModel(BaseModel):
    session_id: str
    user_id: str
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_goals: List[str] = Field(default_factory=list)
    active_challenges: List[str] = Field(default_factory=list)
    recent_achievements: List[str] = Field(default_factory=list)
    contextual_factors: Dict[str, Any] = Field(default_factory=dict)
    time_context: Dict[str, Any] = Field(default_factory=dict)
    emotional_state: Dict[str, Any] = Field(default_factory=dict)
    
class ResponseGenerationModel(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    personality_tone: str = "friendly"
    emotional_adaptation: Dict[str, Any] = Field(default_factory=dict)
    included_insights: List[str] = Field(default_factory=list)
    suggested_actions: List[ActionSuggestionModel] = Field(default_factory=list)
    personalization_applied: bool = True
    generation_strategy: str = "contextual"
    confidence: float = Field(..., ge=0.0, le=1.0)
    
class ConversationalMemoryModel(BaseModel):
    user_id: str
    conversation_id: str
    turns: List[Dict[str, Any]] = Field(default_factory=list)
    key_topics: List[str] = Field(default_factory=list)
    established_context: Dict[str, Any] = Field(default_factory=dict)
    user_preferences_learned: Dict[str, Any] = Field(default_factory=dict)
    successful_strategies: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    last_interaction: datetime = Field(default_factory=datetime.now)
    interaction_quality_score: float = Field(0.5, ge=0.0, le=1.0)
