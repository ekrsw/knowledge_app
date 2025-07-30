"""
Approval service for managing revision proposal approvals
"""
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revision import Revision
from app.models.user import User
from app.models.article import Article
from app.repositories.revision import revision_repository
from app.repositories.article import article_repository
from app.repositories.user import user_repository
from app.schemas.revision import RevisionUpdate
from app.schemas.approval import (
    ApprovalAction,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalHistory,
    ApprovalSummary,
    ApprovalQueue,
    ApprovalWorkload,
    ApprovalMetrics,
    BulkApprovalRequest
)
from app.core.exceptions import (
    ApprovalError,
    ApprovalPermissionError,
    ApprovalStatusError,
    ProposalNotFoundError,
    ArticleNotFoundError
)
from app.utils.approval_workflow import approval_workflow_utils


class ApprovalService:
    """Service for managing approval processes"""
    
    # Approval priorities and their urgency levels
    PRIORITY_URGENCY = {
        "low": {"days_threshold": 7, "escalation_days": 14},
        "medium": {"days_threshold": 3, "escalation_days": 7},
        "high": {"days_threshold": 1, "escalation_days": 3},
        "urgent": {"days_threshold": 0.5, "escalation_days": 1}
    }
    
    async def process_approval_decision(
        self,
        db: AsyncSession,
        *,
        revision_id: UUID,
        approver: User,
        decision: ApprovalDecision
    ) -> Revision:
        """Process an approval decision"""
        # Get the revision
        revision = await revision_repository.get(db, id=revision_id)
        if not revision:
            raise ProposalNotFoundError("Revision not found")
        
        # Verify current status
        if revision.status != "submitted":
            raise ApprovalStatusError(f"Cannot approve revision with status {revision.status}")
        
        # Verify approver permissions
        await self._verify_approval_permissions(db, revision=revision, approver=approver)
        
        # Process the decision
        if decision.action == ApprovalAction.APPROVE:
            new_status = "approved"
        elif decision.action == ApprovalAction.REJECT:
            new_status = "rejected"
        elif decision.action == ApprovalAction.REQUEST_CHANGES:
            new_status = "draft"  # Send back to proposer for changes
        else:  # DEFER
            # Keep as submitted but record the deferral
            new_status = "submitted"
        
        # Update revision
        update_data = RevisionUpdate(
            status=new_status,
            approver_id=approver.id,
            processed_at=datetime.utcnow()
        )
        
        revision = await revision_repository.update(db, db_obj=revision, obj_in=update_data)
        
        # Record approval history (this would typically go to a separate approval_history table)
        await self._record_approval_history(
            db, revision=revision, approver=approver, decision=decision
        )
        
        # If approved, apply changes to the article
        if decision.action == ApprovalAction.APPROVE:
            await self._apply_approved_changes(db, revision=revision)
        
        # Notify proposer about the decision
        try:
            from app.services.notification_service import notification_service
            await notification_service.notify_proposal_decision(
                db, revision=revision, approver=approver, decision=decision.action.value, comment=decision.comment
            )
        except Exception as e:
            # Don't fail the approval if notification fails
            print(f"Failed to send approval notification: {e}")
        
        return revision
    
    async def _verify_approval_permissions(
        self,
        db: AsyncSession,
        *,
        revision: Revision,
        approver: User
    ) -> None:
        """Verify that the approver has permission to approve this revision"""
        # Admin can approve anything
        if approver.role == "admin":
            return
        
        # Must be an approver
        if approver.role not in ["approver", "admin"]:
            raise ApprovalPermissionError("User does not have approval permissions")
        
        # Check approval group permissions
        if approver.approval_group_id:
            # Get the target article
            article = await article_repository.get_by_id(
                db, article_id=revision.target_article_id
            )
            if not article:
                raise ArticleNotFoundError("Target article not found")
            
            # Check if article belongs to approver's group
            if article.approval_group != approver.approval_group_id:
                raise ApprovalPermissionError(
                    "Approver does not have permission for this article's approval group"
                )
        
        # Cannot approve own proposals
        if revision.proposer_id == approver.id:
            raise ApprovalPermissionError("Cannot approve your own proposal")
    
    async def _record_approval_history(
        self,
        db: AsyncSession,
        *,
        revision: Revision,
        approver: User,
        decision: ApprovalDecision
    ) -> None:
        """Record approval decision in history"""
        # This would typically insert into an approval_history table
        # For now, we'll simulate this functionality
        pass
    
    async def _apply_approved_changes(
        self,
        db: AsyncSession,
        *,
        revision: Revision
    ) -> None:
        """Apply approved changes to the target article"""
        # Get the target article
        article = await article_repository.get_by_id(
            db, article_id=revision.target_article_id
        )
        if not article:
            raise ArticleNotFoundError("Target article not found")
        
        # Apply changes from revision to article
        changes_applied = False
        
        if revision.after_title is not None:
            article.title = revision.after_title
            changes_applied = True
        
        if revision.after_info_category is not None:
            article.info_category = revision.after_info_category
            changes_applied = True
        
        if revision.after_keywords is not None:
            article.keywords = revision.after_keywords
            changes_applied = True
        
        if revision.after_importance is not None:
            article.importance = revision.after_importance
            changes_applied = True
        
        if revision.after_publish_start is not None:
            article.publish_start = revision.after_publish_start
            changes_applied = True
        
        if revision.after_publish_end is not None:
            article.publish_end = revision.after_publish_end
            changes_applied = True
        
        if revision.after_target is not None:
            article.target = revision.after_target
            changes_applied = True
        
        if revision.after_question is not None:
            article.question = revision.after_question
            changes_applied = True
        
        if revision.after_answer is not None:
            article.answer = revision.after_answer
            changes_applied = True
        
        if revision.after_additional_comment is not None:
            article.additional_comment = revision.after_additional_comment
            changes_applied = True
        
        if changes_applied:
            # Update the article's updated_at timestamp
            article.updated_at = datetime.utcnow()
            
            # Save changes
            db.add(article)
            await db.commit()
            await db.refresh(article)
    
    async def get_approval_queue(
        self,
        db: AsyncSession,
        *,
        approver: User,
        priority_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[ApprovalQueue]:
        """Get approval queue for an approver"""
        # Get submitted revisions that the approver can approve
        submitted_revisions = await revision_repository.get_by_status(
            db, status="submitted", limit=limit
        )
        
        queue_items = []
        
        for revision in submitted_revisions:
            try:
                # Check if approver can approve this revision
                await self._verify_approval_permissions(
                    db, revision=revision, approver=approver
                )
                
                # Get additional info for queue display
                proposer = await user_repository.get(db, id=revision.proposer_id)
                proposer_name = proposer.full_name if proposer else "Unknown"
                
                # Calculate days pending
                days_pending = (datetime.utcnow() - revision.created_at).days
                
                # Determine if overdue based on impact level
                from app.services.diff_service import diff_service
                try:
                    diff_summary = await diff_service.generate_diff_summary(
                        db, revision_id=str(revision.revision_id)
                    )
                    
                    priority = self._determine_priority(diff_summary.impact_level, days_pending)
                    is_overdue = self._is_overdue(priority, days_pending)
                    
                    # Apply priority filter if specified
                    if priority_filter and priority != priority_filter:
                        continue
                    
                    queue_item = ApprovalQueue(
                        revision_id=str(revision.revision_id),
                        target_article_id=revision.target_article_id,
                        target_article_pk=revision.target_article_pk,
                        proposer_name=proposer_name,
                        reason=revision.reason[:100] + "..." if len(revision.reason) > 100 else revision.reason,
                        priority=priority,
                        impact_level=diff_summary.impact_level,
                        total_changes=diff_summary.total_changes,
                        critical_changes=diff_summary.critical_changes,
                        estimated_review_time=diff_summary.estimated_review_time,
                        submitted_at=revision.created_at,
                        days_pending=days_pending,
                        is_overdue=is_overdue
                    )
                    
                    queue_items.append(queue_item)
                    
                except Exception:
                    # Skip revisions that can't be analyzed
                    continue
                    
            except ApprovalPermissionError:
                # Skip revisions the approver can't approve
                continue
        
        # Sort using workflow utilities
        queue_items = approval_workflow_utils.sort_approval_queue(queue_items)
        
        return queue_items
    
    def _determine_priority(self, impact_level: str, days_pending: int) -> str:
        """Determine priority based on impact level and time pending"""
        if impact_level == "critical":
            return "urgent" if days_pending >= 1 else "high"
        elif impact_level == "high":
            return "high" if days_pending >= 2 else "medium"
        elif impact_level == "medium":
            return "medium" if days_pending >= 3 else "low"
        else:
            return "low"
    
    def _is_overdue(self, priority: str, days_pending: int) -> bool:
        """Check if a revision is overdue based on priority"""
        thresholds = self.PRIORITY_URGENCY.get(priority, {"days_threshold": 7})
        return days_pending > thresholds["days_threshold"]
    
    async def get_approver_workload(
        self,
        db: AsyncSession,
        *,
        approver: User
    ) -> ApprovalWorkload:
        """Get workload information for an approver"""
        # Get pending approvals
        queue = await self.get_approval_queue(db, approver=approver, limit=1000)
        pending_count = len(queue)
        overdue_count = len([item for item in queue if item.is_overdue])
        
        # Get completed approvals (would typically query approval_history table)
        # For now, estimate based on recently approved revisions
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        
        # This would typically be a more sophisticated query
        completed_today = 0  # Placeholder
        completed_this_week = 0  # Placeholder
        average_review_time = 30  # Placeholder: 30 minutes
        
        # Determine current capacity using workflow utilities
        capacity = approval_workflow_utils.calculate_approver_capacity(
            pending_count, overdue_count, completed_today
        )
        
        return ApprovalWorkload(
            approver_id=str(approver.id),
            approver_name=approver.full_name,
            pending_count=pending_count,
            overdue_count=overdue_count,
            completed_today=completed_today,
            completed_this_week=completed_this_week,
            average_review_time=average_review_time,
            current_capacity=capacity
        )
    
    async def get_approval_metrics(
        self,
        db: AsyncSession,
        *,
        days_back: int = 30
    ) -> ApprovalMetrics:
        """Get approval process metrics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get all revisions from the period
        all_revisions = await revision_repository.get_multi(db, limit=1000)
        recent_revisions = [r for r in all_revisions if r.created_at >= cutoff_date]
        
        # Calculate metrics
        total_pending = len([r for r in recent_revisions if r.status == "submitted"])
        total_processed = len([r for r in recent_revisions if r.status in ["approved", "rejected"]])
        approved_count = len([r for r in recent_revisions if r.status == "approved"])
        rejected_count = len([r for r in recent_revisions if r.status == "rejected"])
        
        # Calculate rates
        approval_rate = (approved_count / total_processed * 100) if total_processed > 0 else 0
        rejection_rate = (rejected_count / total_processed * 100) if total_processed > 0 else 0
        
        # Calculate average approval time (placeholder)
        average_approval_time = 24.0  # 24 hours placeholder
        
        # Count overdue items
        queue_all = []
        try:
            # This is a simplified version - in practice you'd need to check all approvers
            admin_users = await user_repository.get_by_role(db, role="admin")
            if admin_users:
                admin_user = admin_users[0]
                queue_all = await self.get_approval_queue(db, approver=admin_user, limit=1000)
        except Exception:
            pass
        
        total_overdue = len([item for item in queue_all if item.is_overdue])
        
        # Group by priority and impact level
        by_priority = {"low": 0, "medium": 0, "high": 0, "urgent": 0}
        by_impact_level = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for item in queue_all:
            by_priority[item.priority] = by_priority.get(item.priority, 0) + 1
            by_impact_level[item.impact_level] = by_impact_level.get(item.impact_level, 0) + 1
        
        # Identify bottlenecks
        bottlenecks = []
        if total_overdue > 5:
            bottlenecks.append("Large number of overdue approvals")
        if by_priority.get("urgent", 0) > 3:
            bottlenecks.append("Multiple urgent approvals pending")
        if average_approval_time > 48:
            bottlenecks.append("Long average approval time")
        
        return ApprovalMetrics(
            total_pending=total_pending,
            total_overdue=total_overdue,
            average_approval_time=average_approval_time,
            approval_rate=approval_rate,
            rejection_rate=rejection_rate,
            by_priority=by_priority,
            by_impact_level=by_impact_level,
            bottlenecks=bottlenecks,
            performance_trends={}  # Placeholder for trend data
        )
    
    async def process_bulk_approval(
        self,
        db: AsyncSession,
        *,
        approver: User,
        bulk_request: BulkApprovalRequest
    ) -> Dict[str, Any]:
        """Process multiple approvals at once"""
        results = {
            "successful": [],
            "failed": [],
            "total_processed": 0,
            "errors": []
        }
        
        for revision_id_str in bulk_request.revision_ids:
            try:
                revision_id = UUID(revision_id_str)
                
                # Process individual approval
                revised = await self.process_approval_decision(
                    db,
                    revision_id=revision_id,
                    approver=approver,
                    decision=bulk_request.decision
                )
                
                results["successful"].append({
                    "revision_id": revision_id_str,
                    "new_status": revised.status
                })
                
            except Exception as e:
                results["failed"].append({
                    "revision_id": revision_id_str,
                    "error": str(e)
                })
                results["errors"].append(f"Revision {revision_id_str}: {str(e)}")
        
        results["total_processed"] = len(bulk_request.revision_ids)
        
        return results
    
    async def can_approve_revision(
        self,
        db: AsyncSession,
        *,
        revision_id: UUID,
        approver: User
    ) -> bool:
        """Check if an approver can approve a specific revision"""
        try:
            revision = await revision_repository.get(db, id=revision_id)
            if not revision or revision.status != "submitted":
                return False
            
            await self._verify_approval_permissions(
                db, revision=revision, approver=approver
            )
            return True
            
        except (ApprovalPermissionError, ProposalNotFoundError):
            return False
    
    async def get_approval_history(
        self,
        db: AsyncSession,
        *,
        revision_id: Optional[UUID] = None,
        approver_id: Optional[UUID] = None,
        limit: int = 50
    ) -> List[ApprovalHistory]:
        """Get approval history"""
        # This would typically query an approval_history table
        # For now, return empty list as placeholder
        return []


# Create singleton instance
approval_service = ApprovalService()