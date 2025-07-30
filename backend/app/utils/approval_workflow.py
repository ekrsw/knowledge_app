"""
Utilities for approval workflow management
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from app.schemas.approval import ApprovalAction, ApprovalQueue


class WorkflowStage(str, Enum):
    """Stages in the approval workflow"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    ESCALATED = "escalated"


class ApprovalWorkflowUtils:
    """Utilities for managing approval workflows"""
    
    # Workflow stage transitions
    VALID_TRANSITIONS = {
        WorkflowStage.DRAFT: [WorkflowStage.SUBMITTED],
        WorkflowStage.SUBMITTED: [
            WorkflowStage.UNDER_REVIEW,
            WorkflowStage.APPROVED,
            WorkflowStage.REJECTED,
            WorkflowStage.CHANGES_REQUESTED,
            WorkflowStage.ESCALATED
        ],
        WorkflowStage.UNDER_REVIEW: [
            WorkflowStage.APPROVED,
            WorkflowStage.REJECTED,
            WorkflowStage.CHANGES_REQUESTED,
            WorkflowStage.ESCALATED
        ],
        WorkflowStage.CHANGES_REQUESTED: [WorkflowStage.SUBMITTED],
        WorkflowStage.ESCALATED: [
            WorkflowStage.APPROVED,
            WorkflowStage.REJECTED,
            WorkflowStage.CHANGES_REQUESTED
        ],
        WorkflowStage.APPROVED: [],  # Final state
        WorkflowStage.REJECTED: []   # Final state
    }
    
    # Priority escalation rules
    ESCALATION_RULES = {
        "low": {"days": 7, "escalate_to": "medium"},
        "medium": {"days": 3, "escalate_to": "high"},
        "high": {"days": 1, "escalate_to": "urgent"},
        "urgent": {"days": 0.5, "escalate_to": "critical"}
    }
    
    # Capacity thresholds for approvers
    CAPACITY_THRESHOLDS = {
        "low": {"max_pending": 3, "max_overdue": 0},
        "medium": {"max_pending": 8, "max_overdue": 2},
        "high": {"max_pending": 15, "max_overdue": 5},
        "overloaded": {"max_pending": float('inf'), "max_overdue": float('inf')}
    }
    
    @staticmethod
    def is_valid_transition(current_stage: str, target_stage: str) -> bool:
        """Check if a workflow stage transition is valid"""
        try:
            current = WorkflowStage(current_stage)
            target = WorkflowStage(target_stage)
            return target in ApprovalWorkflowUtils.VALID_TRANSITIONS.get(current, [])
        except ValueError:
            return False
    
    @staticmethod
    def get_next_stages(current_stage: str) -> List[str]:
        """Get valid next stages from current stage"""
        try:
            current = WorkflowStage(current_stage)
            return [stage.value for stage in ApprovalWorkflowUtils.VALID_TRANSITIONS.get(current, [])]
        except ValueError:
            return []
    
    @staticmethod
    def calculate_priority_score(
        impact_level: str,
        days_pending: int,
        critical_changes: int,
        business_priority: Optional[str] = None
    ) -> int:
        """Calculate numerical priority score for sorting"""
        base_scores = {
            "critical": 1000,
            "high": 500,
            "medium": 200,
            "low": 100
        }
        
        score = base_scores.get(impact_level, 50)
        
        # Add time penalty
        if days_pending > 7:
            score += 200  # Very overdue
        elif days_pending > 3:
            score += 100  # Overdue
        elif days_pending > 1:
            score += 50   # Approaching deadline
        
        # Add critical changes penalty
        score += critical_changes * 50
        
        # Business priority modifier
        if business_priority:
            priority_multipliers = {
                "urgent": 2.0,
                "high": 1.5,
                "medium": 1.0,
                "low": 0.8
            }
            score = int(score * priority_multipliers.get(business_priority, 1.0))
        
        return score
    
    @staticmethod
    def should_escalate(priority: str, days_pending: float) -> bool:
        """Determine if a revision should be escalated"""
        rules = ApprovalWorkflowUtils.ESCALATION_RULES.get(priority)
        if not rules:
            return False
        
        return days_pending >= rules["days"]
    
    @staticmethod
    def get_escalation_target(current_priority: str) -> str:
        """Get the target priority level for escalation"""
        rules = ApprovalWorkflowUtils.ESCALATION_RULES.get(current_priority)
        return rules["escalate_to"] if rules else current_priority
    
    @staticmethod
    def sort_approval_queue(queue: List[ApprovalQueue]) -> List[ApprovalQueue]:
        """Sort approval queue by priority and urgency"""
        def sort_key(item: ApprovalQueue) -> Tuple[int, int, int]:
            # Primary: Priority score (higher = more urgent)
            priority_score = ApprovalWorkflowUtils.calculate_priority_score(
                item.impact_level,
                item.days_pending,
                item.critical_changes,
                item.priority
            )
            
            # Secondary: Days pending (older first)
            days_score = item.days_pending
            
            # Tertiary: Critical changes count
            critical_score = item.critical_changes
            
            return (-priority_score, -days_score, -critical_score)
        
        return sorted(queue, key=sort_key)
    
    @staticmethod
    def calculate_approver_capacity(
        pending_count: int,
        overdue_count: int,
        completed_today: int = 0
    ) -> str:
        """Calculate approver capacity level"""
        # Check overdue first (critical indicator)
        if overdue_count > 5:
            return "overloaded"
        elif overdue_count > 2:
            return "high"
        
        # Check pending workload
        if pending_count <= 3:
            return "low"
        elif pending_count <= 8:
            return "medium"
        elif pending_count <= 15:
            return "high"
        else:
            return "overloaded"
    
    @staticmethod
    def estimate_completion_time(
        queue_item: ApprovalQueue,
        approver_capacity: str
    ) -> datetime:
        """Estimate when an approval will be completed"""
        base_time = queue_item.estimated_review_time
        
        # Capacity multipliers
        capacity_multipliers = {
            "low": 1.0,
            "medium": 1.5,
            "high": 2.0,
            "overloaded": 3.0
        }
        
        multiplier = capacity_multipliers.get(approver_capacity, 2.0)
        estimated_minutes = int(base_time * multiplier)
        
        # Add to current time
        return datetime.utcnow() + timedelta(minutes=estimated_minutes)
    
    @staticmethod
    def generate_approval_recommendations(
        queue: List[ApprovalQueue],
        approver_capacity: str
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for approval workflow"""
        recommendations = []
        
        # Sort queue by priority
        sorted_queue = ApprovalWorkflowUtils.sort_approval_queue(queue)
        
        # Check for urgent items
        urgent_items = [item for item in sorted_queue if item.priority == "urgent"]
        if urgent_items:
            recommendations.append({
                "type": "urgent_attention",
                "message": f"{len(urgent_items)}件の緊急承認待ちがあります",
                "action": "immediate_review",
                "items": urgent_items[:3]  # Top 3 urgent items
            })
        
        # Check for overdue items
        overdue_items = [item for item in sorted_queue if item.is_overdue]
        if len(overdue_items) > 3:
            recommendations.append({
                "type": "overdue_cleanup",
                "message": f"{len(overdue_items)}件の期限超過承認があります",
                "action": "bulk_review",
                "items": overdue_items[:5]  # Top 5 overdue items
            })
        
        # Capacity recommendations
        if approver_capacity == "overloaded":
            recommendations.append({
                "type": "workload_management",
                "message": "承認者の負荷が高すぎます。タスクの再配分を検討してください",
                "action": "redistribute_workload",
                "items": []
            })
        
        # Time-based recommendations
        high_review_time_items = [
            item for item in sorted_queue 
            if item.estimated_review_time > 30
        ]
        if high_review_time_items:
            recommendations.append({
                "type": "complex_reviews",
                "message": f"{len(high_review_time_items)}件の複雑な承認があります",
                "action": "schedule_focused_time",
                "items": high_review_time_items[:3]
            })
        
        return recommendations
    
    @staticmethod
    def create_approval_checklist(
        impact_level: str,
        critical_changes: int,
        change_categories: List[str]
    ) -> List[Dict[str, Any]]:
        """Create a dynamic approval checklist"""
        checklist = []
        
        # Base checks
        checklist.append({
            "category": "基本確認",
            "item": "変更理由の妥当性確認",
            "required": True,
            "description": "提案された変更の理由が適切かどうか確認"
        })
        
        # Impact-based checks
        if impact_level in ["high", "critical"]:
            checklist.append({
                "category": "影響度確認",
                "item": "システム影響度評価",
                "required": True,
                "description": "変更がシステム全体に与える影響を評価"
            })
        
        # Critical changes checks
        if critical_changes > 0:
            checklist.append({
                "category": "重要変更確認",
                "item": f"{critical_changes}件の重要変更の詳細確認",
                "required": True,
                "description": "重要度の高いフィールドの変更内容を詳細確認"
            })
        
        # Category-specific checks
        if "scheduling" in change_categories:
            checklist.append({
                "category": "スケジュール確認",
                "item": "公開日程の妥当性確認",
                "required": True,
                "description": "公開スケジュールの変更が適切かどうか確認"
            })
        
        if "content" in change_categories:
            checklist.append({
                "category": "コンテンツ確認",
                "item": "コンテンツ品質確認",
                "required": False,
                "description": "変更されたコンテンツの品質と適切性を確認"
            })
        
        # Final approval
        checklist.append({
            "category": "最終確認",
            "item": "全体的な承認判断",
            "required": True,
            "description": "すべての確認項目を総合して最終的な承認判断を行う"
        })
        
        return checklist
    
    @staticmethod
    def calculate_workflow_metrics(queue: List[ApprovalQueue]) -> Dict[str, Any]:
        """Calculate workflow performance metrics"""
        if not queue:
            return {}
        
        total_items = len(queue)
        overdue_items = len([item for item in queue if item.is_overdue])
        urgent_items = len([item for item in queue if item.priority == "urgent"])
        
        # Calculate average days pending
        avg_days_pending = sum(item.days_pending for item in queue) / total_items
        
        # Calculate review time distribution
        review_times = [item.estimated_review_time for item in queue]
        avg_review_time = sum(review_times) / len(review_times)
        
        # Priority distribution
        priority_dist = {}
        for item in queue:
            priority_dist[item.priority] = priority_dist.get(item.priority, 0) + 1
        
        # Impact distribution
        impact_dist = {}
        for item in queue:
            impact_dist[item.impact_level] = impact_dist.get(item.impact_level, 0) + 1
        
        return {
            "total_items": total_items,
            "overdue_rate": (overdue_items / total_items) * 100,
            "urgent_rate": (urgent_items / total_items) * 100,
            "avg_days_pending": round(avg_days_pending, 1),
            "avg_review_time": round(avg_review_time, 1),
            "priority_distribution": priority_dist,
            "impact_distribution": impact_dist,
            "workflow_health": "good" if overdue_items < total_items * 0.1 else "needs_attention"
        }


# Create utility instance
approval_workflow_utils = ApprovalWorkflowUtils()