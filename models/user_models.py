from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserModel(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskModel(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    estimated_pomodoros: int = Field(1, ge=1, le=20)
    completed_pomodoros: int = Field(0, ge=0)
    created_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PomodoroStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    CANCELLED = "cancelled"

class PomodoroModel(BaseModel):
    id: Optional[str] = None
    task_id: str
    duration: int = Field(25, ge=5, le=120)  # minutes
    status: PomodoroStatus = PomodoroStatus.PLANNED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    interruption_reason: Optional[str] = None
    focus_quality: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = Field(None, max_length=500)
    
    class Config:
        from_attributes = True

class FlowerType(str, Enum):
    ROSE = "rose"
    TULIP = "tulip"
    SUNFLOWER = "sunflower"
    LILY = "lily"
    ORCHID = "orchid"
    DAISY = "daisy"

class FlowerColor(str, Enum):
    RED = "red"
    BLUE = "blue"
    YELLOW = "yellow"
    PINK = "pink"
    PURPLE = "purple"
    WHITE = "white"
    ORANGE = "orange"

class FlowerModel(BaseModel):
    id: Optional[str] = None
    user_id: str
    color: FlowerColor
    type: FlowerType
    earned_at: datetime
    task_id: Optional[str] = None
    achievement_type: str = Field(..., max_length=50)
    rarity: str = Field("common", max_length=20)  # common, rare, epic, legendary
    
    class Config:
        from_attributes = True

class MoodState(str, Enum):
    MOTIVATED = "motivated"
    STRUGGLING = "struggling"
    FOCUSED = "focused"
    OVERWHELMED = "overwhelmed"
    CELEBRATING = "celebrating"
    RETURNING = "returning"
    NEUTRAL = "neutral"

class LumiMemoryModel(BaseModel):
    id: Optional[str] = None
    user_id: str
    personality_profile: Dict[str, Any] = Field(default_factory=dict)
    behavior_patterns: Dict[str, Any] = Field(default_factory=dict)
    achievements: Dict[str, Any] = Field(default_factory=dict)
    contextual_memory: Dict[str, Any] = Field(default_factory=dict)
    current_mood: MoodState = MoodState.NEUTRAL
    interaction_count: int = Field(0, ge=0)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserStatsModel(BaseModel):
    user_id: str
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    in_progress_tasks: int = 0
    overdue_tasks: int = 0
    total_pomodoros: int = 0
    total_focus_time_minutes: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    flowers_earned: int = 0
    completion_rate: float = 0.0
    avg_pomodoros_per_task: float = 0.0
    
    class Config:
        from_attributes = True

class ProductivityMetricsModel(BaseModel):
    user_id: str
    date: datetime
    tasks_completed: int = 0
    pomodoros_completed: int = 0
    focus_time_minutes: int = 0
    productivity_score: float = 0.0
    mood_state: MoodState = MoodState.NEUTRAL
    peak_focus_hour: Optional[int] = None
    distraction_count: int = 0
    
    class Config:
        from_attributes = True

# Request/Response Models for API

class CreateTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_pomodoros: Optional[int] = Field(None, ge=1, le=20)
    due_date: Optional[datetime] = None

class UpdateTaskRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    estimated_pomodoros: Optional[int] = Field(None, ge=1, le=20)
    due_date: Optional[datetime] = None

class StartPomodoroRequest(BaseModel):
    task_id: str
    duration: int = Field(25, ge=5, le=120)
    notes: Optional[str] = Field(None, max_length=500)

class CompletePomodoroRequest(BaseModel):
    focus_quality: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = Field(None, max_length=500)
    interruption_reason: Optional[str] = Field(None, max_length=200)

class TaskResponse(BaseModel):
    task: TaskModel
    pomodoros: List[PomodoroModel] = []
    estimated_completion_time: Optional[int] = None  # minutes
    optimal_time_slots: List[str] = []
    difficulty_assessment: Optional[str] = None

class PomodoroSessionResponse(BaseModel):
    pomodoro: PomodoroModel
    task: TaskModel
    session_stats: Dict[str, Any] = Field(default_factory=dict)
    next_break_suggestion: Optional[str] = None
    productivity_tips: List[str] = []

class UserDashboardResponse(BaseModel):
    user: UserModel
    stats: UserStatsModel
    current_mood: MoodState
    today_summary: Dict[str, Any]
    active_tasks: List[TaskModel]
    recent_achievements: List[FlowerModel]
    personalized_suggestions: List[str]
    motivational_message: str

class AnalyticsRequest(BaseModel):
    period_days: int = Field(30, ge=1, le=365)
    include_predictions: bool = True
    include_patterns: bool = True
    metrics: List[str] = Field(default_factory=list)

class InsightModel(BaseModel):
    type: str
    title: str
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    actionable: bool = True
    priority: str = "medium"  # low, medium, high
    data_points: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = []

class PredictionModel(BaseModel):
    prediction_type: str
    timeframe: str
    probability: float = Field(..., ge=0.0, le=1.0)
    description: str
    factors: List[str]
    preventive_actions: List[str] = []
    confidence_interval: Dict[str, float] = Field(default_factory=dict)

class RecommendationModel(BaseModel):
    category: str
    title: str
    description: str
    priority: str = "medium"
    estimated_impact: str = "medium"  # low, medium, high
    effort_required: str = "medium"  # low, medium, high
    implementation_steps: List[str] = []
    success_metrics: List[str] = []

class FeedbackRequest(BaseModel):
    interaction_id: str
    rating: int = Field(..., ge=1, le=5)
    response_helpfulness: int = Field(..., ge=1, le=5)
    personality_appropriateness: int = Field(..., ge=1, le=5)
    suggestions_quality: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    improvement_suggestions: Optional[str] = Field(None, max_length=1000)

class ErrorResponse(BaseModel):
    error: str
    message: str
    code: str
    timestamp: datetime
    suggestions: List[str] = []
    
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
