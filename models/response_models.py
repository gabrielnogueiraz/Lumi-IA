from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class PersonalityTone(str, Enum):
    CASUAL = "casual"
    SUPPORTIVE = "supportive"
    DIRECT = "direct"
    CALMING = "calming"
    ENTHUSIASTIC = "enthusiastic"
    WELCOMING = "welcoming"
    ANALYTICAL = "analytical"
    MOTIVATIONAL = "motivational"

class ActionType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    POMODORO_STARTED = "pomodoro_started"
    POMODORO_COMPLETED = "pomodoro_completed"
    INSIGHT_PROVIDED = "insight_provided"
    SUGGESTION_GIVEN = "suggestion_given"
    MOOD_DETECTED = "mood_detected"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    PATTERN_DISCOVERED = "pattern_discovered"
    OPTIMIZATION_APPLIED = "optimization_applied"

class LumiActionModel(BaseModel):
    type: ActionType
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    user_facing: bool = True
    description: Optional[str] = None

class EmotionalContextModel(BaseModel):
    detected_mood: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    adaptation_applied: bool = False
    contributing_factors: List[str] = Field(default_factory=list)
    mood_transition: Optional[Dict[str, Any]] = None
    emotional_stability: float = Field(0.5, ge=0.0, le=1.0)
    support_needed: bool = False
    celebration_worthy: bool = False

class LumiResponseModel(BaseModel):
    response: str = Field(..., min_length=1, max_length=2000)
    mood: str = "neutral"
    personality_tone: PersonalityTone = PersonalityTone.SUPPORTIVE
    actions: List[LumiActionModel] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    emotional_context: EmotionalContextModel
    processing_time: float = 0.0
    session_id: Optional[str] = None
    conversation_context: Dict[str, Any] = Field(default_factory=dict)

class ChatInteractionModel(BaseModel):
    user_id: str
    message: str = Field(..., min_length=1, max_length=5000)
    context: Optional[str] = Field(None, max_length=1000)
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    user_metadata: Dict[str, Any] = Field(default_factory=dict)

class AnalyticsResponseModel(BaseModel):
    status: ResponseStatus = ResponseStatus.SUCCESS
    data: Dict[str, Any] = Field(default_factory=dict)
    insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.now)
    data_freshness: str = "real-time"  # real-time, cached, historical

class InsightResponseModel(BaseModel):
    insights: List[Dict[str, Any]] = Field(default_factory=list)
    predictions: List[Dict[str, Any]] = Field(default_factory=list)
    behavioral_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    optimization_opportunities: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    analysis_period: str = "30_days"
    generated_at: datetime = Field(default_factory=datetime.now)

class TaskSuggestionResponseModel(BaseModel):
    suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    optimization_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    timing_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    complexity_assessments: List[Dict[str, Any]] = Field(default_factory=list)
    context_applied: str = "general"
    confidence_score: float = Field(0.5, ge=0.0, le=1.0)
    generated_at: datetime = Field(default_factory=datetime.now)

class MoodAnalysisResponseModel(BaseModel):
    current_mood: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    mood_history: List[Dict[str, Any]] = Field(default_factory=list)
    mood_patterns: Dict[str, Any] = Field(default_factory=dict)
    triggers: List[str] = Field(default_factory=list)
    stability_indicators: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    analysis_period_days: int = 30

class HealthCheckResponseModel(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "2.0.0"
    services: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    system_metrics: Dict[str, Any] = Field(default_factory=dict)
    dependencies: Dict[str, Any] = Field(default_factory=dict)
    performance_metrics: Optional[Dict[str, Any]] = None

class ErrorDetailModel(BaseModel):
    error_code: str
    error_type: str
    message: str
    details: Optional[str] = None
    suggestions: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    user_friendly_message: str
    technical_details: Optional[Dict[str, Any]] = None

class APIResponseModel(BaseModel):
    status: ResponseStatus
    data: Optional[Union[
        LumiResponseModel,
        AnalyticsResponseModel,
        InsightResponseModel,
        TaskSuggestionResponseModel,
        MoodAnalysisResponseModel,
        HealthCheckResponseModel,
        Dict[str, Any]
    ]] = None
    error: Optional[ErrorDetailModel] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None
    processing_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)

class UserFeedbackModel(BaseModel):
    user_id: str
    interaction_id: str
    rating: int = Field(..., ge=1, le=5)
    response_quality: int = Field(..., ge=1, le=5)
    helpfulness: int = Field(..., ge=1, le=5)
    personality_appropriateness: int = Field(..., ge=1, le=5)
    accuracy: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=2000)
    improvement_suggestions: Optional[str] = Field(None, max_length=2000)
    feature_requests: Optional[str] = Field(None, max_length=1000)
    timestamp: datetime = Field(default_factory=datetime.now)

class LearningFeedbackModel(BaseModel):
    user_id: str
    feedback_category: str  # response_quality, personality_match, suggestion_relevance
    positive_aspects: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    specific_examples: Dict[str, str] = Field(default_factory=dict)
    effectiveness_score: float = Field(..., ge=0.0, le=1.0)
    behavioral_impact: str = "none"  # none, minor, moderate, significant
    timestamp: datetime = Field(default_factory=datetime.now)

class PersonalizationUpdateModel(BaseModel):
    user_id: str
    personality_adjustments: Dict[str, float] = Field(default_factory=dict)
    communication_preferences: Dict[str, Any] = Field(default_factory=dict)
    successful_strategies: List[str] = Field(default_factory=list)
    ineffective_approaches: List[str] = Field(default_factory=list)
    user_goals_updated: List[str] = Field(default_factory=list)
    adaptation_confidence: float = Field(0.5, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)

class ConversationSummaryModel(BaseModel):
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    message_count: int = 0
    topics_covered: List[str] = Field(default_factory=list)
    outcomes_achieved: List[str] = Field(default_factory=list)
    user_satisfaction: Optional[float] = Field(None, ge=0.0, le=1.0)
    key_insights_discovered: List[str] = Field(default_factory=list)
    follow_up_items: List[str] = Field(default_factory=list)
    conversation_quality: str = "good"  # poor, fair, good, excellent

class SystemMetricsModel(BaseModel):
    cpu_usage_percent: float = Field(..., ge=0.0, le=100.0)
    memory_usage_percent: float = Field(..., ge=0.0, le=100.0)
    disk_usage_percent: float = Field(..., ge=0.0, le=100.0)
    active_connections: int = Field(..., ge=0)
    response_time_avg_ms: float = Field(..., ge=0.0)
    error_rate_percent: float = Field(..., ge=0.0, le=100.0)
    requests_per_minute: int = Field(..., ge=0)
    ai_model_latency_ms: float = Field(..., ge=0.0)
    database_query_time_avg_ms: float = Field(..., ge=0.0)
    timestamp: datetime = Field(default_factory=datetime.now)

class PerformanceReportModel(BaseModel):
    period_start: datetime
    period_end: datetime
    total_requests: int = 0
    successful_requests: int = 0
    error_count: int = 0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    user_satisfaction_avg: Optional[float] = Field(None, ge=0.0, le=5.0)
    most_used_features: List[str] = Field(default_factory=list)
    performance_bottlenecks: List[str] = Field(default_factory=list)
    improvement_recommendations: List[str] = Field(default_factory=list)
