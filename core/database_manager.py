import asyncpg
import asyncio
import logging
from typing import Optional, Dict, List, Any
from contextlib import asynccontextmanager
from config.database import DATABASE_CONFIG, POOL_CONFIG
import structlog

logger = structlog.get_logger(__name__)

class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=DATABASE_CONFIG["host"],
                port=DATABASE_CONFIG["port"],
                database=DATABASE_CONFIG["database"],
                user=DATABASE_CONFIG["user"],
                password=DATABASE_CONFIG["password"],
                **POOL_CONFIG
            )
            logger.info("Database pool initialized successfully")
            
            # Test connection
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            logger.info("Database connection test successful")
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"Database operation error: {e}")
                raise
    
    async def fetch_user_context(self, user_id: str) -> Dict[str, Any]:
        """Fetch complete user context for AI processing"""
        async with self.get_connection() as conn:
            try:                # User basic info - usando tabela correta do Toivo
                user_info = await conn.fetchrow("""
                    SELECT id, name, email, "createdAt" as created_at
                    FROM "user" WHERE id = $1
                """, user_id)
                
                if not user_info:
                    return {"error": "User not found"}
                
                # Tasks statistics - usando tabela correta do Toivo
                tasks_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_tasks,
                        COUNT(*) FILTER (WHERE status = 'completed') as completed_tasks,
                        COUNT(*) FILTER (WHERE status = 'PENDING') as pending_tasks,
                        COUNT(*) FILTER (WHERE status = 'IN_PROGRESS') as in_progress_tasks,                        COUNT(*) FILTER (WHERE "dueDate" < NOW() AND status != 'completed') as overdue_tasks,
                        AVG("completedPomodoros") FILTER (WHERE status = 'completed') as avg_pomodoros_per_task
                    FROM task WHERE "userId" = $1
                """, user_id)
                  # Recent activity (last 7 days) - usando tabela correta do Toivo
                recent_activity = await conn.fetch("""
                    SELECT 
                        DATE("createdAt") as date,
                        COUNT(*) as tasks_created,
                        COUNT(*) FILTER (WHERE status = 'completed') as tasks_completed
                    FROM task 
                    WHERE "userId" = $1 AND "createdAt" >= NOW() - INTERVAL '7 days'
                    GROUP BY DATE("createdAt")
                    ORDER BY date DESC
                """, user_id)
                
                # Productivity patterns - usando tabela correta do Toivo
                productivity_patterns = await conn.fetchrow("""
                    SELECT 
                        EXTRACT(hour FROM "startedAt") as peak_hour,
                        COUNT(*) as pomodoro_count,
                        AVG(duration) as avg_duration
                    FROM pomodoro p
                    JOIN task t ON p."taskId" = t.id
                    WHERE t."userId" = $1 AND p.status = 'completed'
                        AND p."startedAt" >= NOW() - INTERVAL '30 days'
                    GROUP BY EXTRACT(hour FROM "startedAt")
                    ORDER BY pomodoro_count DESC
                    LIMIT 1
                """, user_id)
                
                # Current streak - usando tabela correta do Toivo
                current_streak = await conn.fetchval("""
                    WITH daily_completions AS (
                        SELECT DATE("updatedAt") as completion_date
                        FROM task
                        WHERE "userId" = $1 AND status = 'completed'
                        GROUP BY DATE("updatedAt")
                        HAVING COUNT(*) > 0
                        ORDER BY completion_date DESC
                    ),
                    streak_calc AS (
                        SELECT 
                            completion_date,
                            ROW_NUMBER() OVER (ORDER BY completion_date DESC) as rn,
                            completion_date - INTERVAL '1 day' * (ROW_NUMBER() OVER (ORDER BY completion_date DESC) - 1) as expected_date
                        FROM daily_completions
                    )
                    SELECT COUNT(*) 
                    FROM streak_calc
                    WHERE completion_date = expected_date
                        AND completion_date >= (
                            SELECT MIN(expected_date) 
                            FROM streak_calc 
                            WHERE completion_date = expected_date
                        )
                """, user_id)
                
                # Lumi memory - usando tabela correta do Toivo
                lumi_memory = await conn.fetchrow("""
                    SELECT "personalityProfile", "behaviorPatterns", achievements, 
                           "contextualMemory", "currentMood", "interactionCount",
                           "createdAt", "updatedAt"
                    FROM lumi_memory WHERE "userId" = $1
                """, user_id)
                  # Recent pomodoros (today) - usando tabela correta do Toivo
                today_pomodoros = await conn.fetch("""
                    SELECT p.duration, p.status, p."startedAt", p."completedAt", t.title
                    FROM pomodoro p
                    JOIN task t ON p."taskId" = t.id
                    WHERE t."userId" = $1 
                        AND DATE(p."startedAt") = CURRENT_DATE
                    ORDER BY p."startedAt" DESC
                """, user_id)
                
                return {
                    "user_info": dict(user_info) if user_info else None,
                    "tasks_stats": dict(tasks_stats) if tasks_stats else {},
                    "recent_activity": [dict(row) for row in recent_activity],
                    "productivity_patterns": dict(productivity_patterns) if productivity_patterns else {},
                    "current_streak": current_streak or 0,
                    "lumi_memory": dict(lumi_memory) if lumi_memory else None,
                    "today_pomodoros": [dict(row) for row in today_pomodoros]
                }
                
            except Exception as e:
                logger.error(f"Error fetching user context: {e}")
                return {"error": str(e)}
    
    async def update_lumi_memory(self, user_id: str, memory_data: Dict[str, Any]) -> bool:
        """Update Lumi's memory for a user - usando tabela correta do Toivo"""
        async with self.get_connection() as conn:
            try:
                await conn.execute("""
                    INSERT INTO lumi_memory (
                        "userId", "personalityProfile", "behaviorPatterns", 
                        achievements, "contextualMemory", "currentMood", 
                        "interactionCount", "helpfulnessScore", "createdAt", "updatedAt"
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
                    ON CONFLICT ("userId") DO UPDATE SET
                        "personalityProfile" = EXCLUDED."personalityProfile",
                        "behaviorPatterns" = EXCLUDED."behaviorPatterns",
                        achievements = EXCLUDED.achievements,
                        "contextualMemory" = EXCLUDED."contextualMemory",
                        "currentMood" = EXCLUDED."currentMood",
                        "interactionCount" = lumi_memory."interactionCount" + 1,
                        "helpfulnessScore" = EXCLUDED."helpfulnessScore",
                        "updatedAt" = NOW()
                """, 
                user_id,
                memory_data.get("personality_profile", "{}"),
                memory_data.get("behavior_patterns", "{}"),
                memory_data.get("achievements", "{}"),
                memory_data.get("contextual_memory", "{}"),
                memory_data.get("current_mood", "encouraging"),                memory_data.get("interaction_count", 0),
                memory_data.get("helpfulness_score", 0)
                )
                return True
            except Exception as e:
                logger.error(f"Error updating lumi memory: {e}")
                return False
    
    async def create_task(self, user_id: str, task_data: Dict[str, Any]) -> Optional[str]:
        """Create a new task - usando tabela correta do Toivo"""
        async with self.get_connection() as conn:
            try:
                # Validar dados obrigatórios
                if not task_data.get("title"):
                    logger.error("Task title is required")
                    return None
                
                # Preparar due_date se fornecido
                due_date = None
                if task_data.get("due_date"):
                    due_date_str = task_data["due_date"]
                    time_str = task_data.get("time", "00:00")
                    if due_date_str and time_str:
                        try:
                            due_date = f"{due_date_str} {time_str}:00"
                        except:
                            due_date = due_date_str
                
                # Log para debugging
                logger.info(f"Creating task for user {user_id}: {task_data.get('title')}")
                logger.info(f"Task data: {task_data}")
                
                # Usar a tabela correta do Toivo com camelCase
                task_id = await conn.fetchval("""                    INSERT INTO task (
                        "userId", title, description, priority, status,
                        "estimatedPomodoros", "completedPomodoros", 
                        "createdAt", "dueDate", "updatedAt", "startTime", "endTime"
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), $8, NOW(), $9, $10)
                    RETURNING id
                """,
                user_id,  # UUID do usuário
                task_data.get("title", ""),
                task_data.get("description", ""),
                task_data.get("priority", "MEDIUM"),
                task_data.get("status", "PENDING"),
                task_data.get("estimated_pomodoros", 1),
                0,
                due_date,
                task_data.get("start_time"),
                task_data.get("end_time")
                )
                
                logger.info(f"✅ Task created successfully with ID: {task_id}")
                return str(task_id)
            except Exception as e:
                logger.error(f"Error creating task: {e}")
                return None
    
    async def get_productivity_insights(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get productivity insights for the user"""
        async with self.get_connection() as conn:
            try:
                # Hourly productivity patterns
                hourly_patterns = await conn.fetch("""
                    SELECT 
                        EXTRACT(hour FROM started_at) as hour,
                        COUNT(*) as pomodoro_count,
                        AVG(duration) as avg_duration,
                        COUNT(*) FILTER (WHERE status = 'completed') as completed_count
                    FROM pomodoros p
                    JOIN tasks t ON p.task_id = t.id
                    WHERE t.user_id = $1 
                        AND p.started_at >= NOW() - INTERVAL '%s days'
                    GROUP BY EXTRACT(hour FROM started_at)
                    ORDER BY hour
                """, user_id, days)
                
                # Daily productivity trends
                daily_trends = await conn.fetch("""
                    SELECT 
                        DATE(updated_at) as date,
                        COUNT(*) FILTER (WHERE status = 'completed') as completed_tasks,
                        COUNT(*) as total_tasks,
                        ROUND(
                            COUNT(*) FILTER (WHERE status = 'completed')::numeric / 
                            NULLIF(COUNT(*), 0) * 100, 2
                        ) as completion_rate
                    FROM tasks
                    WHERE user_id = $1 
                        AND updated_at >= NOW() - INTERVAL '%s days'
                    GROUP BY DATE(updated_at)
                    ORDER BY date DESC
                """, user_id, days)
                
                # Task complexity analysis
                complexity_analysis = await conn.fetchrow("""
                    SELECT 
                        AVG(estimated_pomodoros) as avg_estimated,
                        AVG(completed_pomodoros) as avg_actual,
                        COUNT(*) FILTER (WHERE completed_pomodoros > estimated_pomodoros) as underestimated,
                        COUNT(*) FILTER (WHERE completed_pomodoros < estimated_pomodoros) as overestimated,
                        COUNT(*) FILTER (WHERE completed_pomodoros = estimated_pomodoros) as accurate
                    FROM tasks
                    WHERE user_id = $1 AND status = 'completed'
                        AND updated_at >= NOW() - INTERVAL '%s days'
                """, user_id, days)
                
                return {
                    "hourly_patterns": [dict(row) for row in hourly_patterns],
                    "daily_trends": [dict(row) for row in daily_trends],
                    "complexity_analysis": dict(complexity_analysis) if complexity_analysis else {}
                }
                
            except Exception as e:
                logger.error(f"Error getting productivity insights: {e}")
                return {}

# Global database manager instance
db_manager = DatabaseManager()
