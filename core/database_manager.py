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
            try:
                # User basic info
                user_info = await conn.fetchrow("""
                    SELECT id, name, email, created_at
                    FROM users WHERE id = $1
                """, user_id)
                
                if not user_info:
                    return {"error": "User not found"}
                
                # Tasks statistics
                tasks_stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_tasks,
                        COUNT(*) FILTER (WHERE status = 'completed') as completed_tasks,
                        COUNT(*) FILTER (WHERE status = 'pending') as pending_tasks,
                        COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_tasks,
                        COUNT(*) FILTER (WHERE due_date < NOW() AND status != 'completed') as overdue_tasks,
                        AVG(completed_pomodoros) FILTER (WHERE status = 'completed') as avg_pomodoros_per_task
                    FROM tasks WHERE user_id = $1
                """, user_id)
                
                # Recent activity (last 7 days)
                recent_activity = await conn.fetch("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as tasks_created,
                        COUNT(*) FILTER (WHERE status = 'completed') as tasks_completed
                    FROM tasks 
                    WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '7 days'
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                """, user_id)
                
                # Productivity patterns
                productivity_patterns = await conn.fetchrow("""
                    SELECT 
                        EXTRACT(hour FROM started_at) as peak_hour,
                        COUNT(*) as pomodoro_count,
                        AVG(duration) as avg_duration
                    FROM pomodoros p
                    JOIN tasks t ON p.task_id = t.id
                    WHERE t.user_id = $1 AND p.status = 'completed'
                        AND p.started_at >= NOW() - INTERVAL '30 days'
                    GROUP BY EXTRACT(hour FROM started_at)
                    ORDER BY pomodoro_count DESC
                    LIMIT 1
                """, user_id)
                
                # Current streak
                current_streak = await conn.fetchval("""
                    WITH daily_completions AS (
                        SELECT DATE(updated_at) as completion_date
                        FROM tasks
                        WHERE user_id = $1 AND status = 'completed'
                        GROUP BY DATE(updated_at)
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
                
                # Lumi memory
                lumi_memory = await conn.fetchrow("""
                    SELECT personality_profile, behavior_patterns, achievements, 
                           contextual_memory, current_mood, interaction_count,
                           created_at, updated_at
                    FROM lumi_memory WHERE user_id = $1
                """, user_id)
                
                # Recent pomodoros (today)
                today_pomodoros = await conn.fetch("""
                    SELECT p.duration, p.status, p.started_at, p.completed_at, t.title
                    FROM pomodoros p
                    JOIN tasks t ON p.task_id = t.id
                    WHERE t.user_id = $1 
                        AND DATE(p.started_at) = CURRENT_DATE
                    ORDER BY p.started_at DESC
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
        """Update Lumi's memory for a user"""
        async with self.get_connection() as conn:
            try:
                await conn.execute("""
                    INSERT INTO lumi_memory (
                        user_id, personality_profile, behavior_patterns, 
                        achievements, contextual_memory, current_mood, 
                        interaction_count, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
                    ON CONFLICT (user_id) DO UPDATE SET
                        personality_profile = EXCLUDED.personality_profile,
                        behavior_patterns = EXCLUDED.behavior_patterns,
                        achievements = EXCLUDED.achievements,
                        contextual_memory = EXCLUDED.contextual_memory,
                        current_mood = EXCLUDED.current_mood,
                        interaction_count = lumi_memory.interaction_count + 1,
                        updated_at = NOW()
                """, 
                user_id,
                memory_data.get("personality_profile", "{}"),
                memory_data.get("behavior_patterns", "{}"),
                memory_data.get("achievements", "{}"),
                memory_data.get("contextual_memory", "{}"),
                memory_data.get("current_mood", "neutral"),
                memory_data.get("interaction_count", 0)
                )
                return True
            except Exception as e:
                logger.error(f"Error updating lumi memory: {e}")
                return False
    
    async def create_task(self, user_id: str, task_data: Dict[str, Any]) -> Optional[str]:
        """Create a new task"""
        async with self.get_connection() as conn:
            try:
                task_id = await conn.fetchval("""
                    INSERT INTO tasks (
                        user_id, title, description, priority, status,
                        estimated_pomodoros, completed_pomodoros, 
                        created_at, due_date, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), $8, NOW())
                    RETURNING id
                """,
                user_id,
                task_data.get("title", ""),
                task_data.get("description", ""),
                task_data.get("priority", "medium"),
                task_data.get("status", "pending"),
                task_data.get("estimated_pomodoros", 1),
                0,
                task_data.get("due_date")
                )
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
