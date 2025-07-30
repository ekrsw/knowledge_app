"""
Proposal service for managing revision proposals
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revision import Revision
from app.models.user import User
from app.models.article import Article
from app.repositories.revision import revision_repository
from app.repositories.article import article_repository
from app.repositories.user import user_repository
from app.schemas.revision import RevisionCreate, RevisionUpdate
from app.core.exceptions import (
    ProposalNotFoundError,
    ProposalPermissionError,
    ProposalStatusError,
    ProposalValidationError,
    ArticleNotFoundError
)
from app.utils.validation import validate_proposal_changes, calculate_proposal_priority


class ProposalService:
    """Service for managing revision proposals"""
    
    async def create_proposal(
        self,
        db: AsyncSession,
        *,
        proposal_data: RevisionCreate,
        proposer: User
    ) -> Revision:
        """Create a new revision proposal"""
        # Verify that the target article exists
        target_article = await article_repository.get_by_id(
            db, article_id=proposal_data.target_article_id
        )
        if not target_article:
            raise ArticleNotFoundError(f"Target article {proposal_data.target_article_id} not found")
        
        # Create revision with proposer information
        revision_data = proposal_data.model_dump()
        revision_data["proposer_id"] = proposer.id
        revision_data["status"] = "draft"  # Start as draft
        
        # Create the revision
        revision = await revision_repository.create(db, obj_in=RevisionCreate(**revision_data))
        return revision
    
    async def submit_proposal(
        self,
        db: AsyncSession,
        *,
        revision_id: UUID,
        proposer: User
    ) -> Revision:
        """Submit a proposal for approval"""
        # Get the revision
        revision = await revision_repository.get(db, id=revision_id)
        if not revision:
            raise ProposalNotFoundError("Revision not found")
        
        # Verify proposer ownership
        if revision.proposer_id != proposer.id:
            raise ProposalPermissionError("Not authorized to submit this proposal")
        
        # Verify current status
        if revision.status != "draft":
            raise ProposalStatusError(f"Cannot submit proposal with status {revision.status}")
        
        # Update status to submitted
        update_data = RevisionUpdate(status="submitted")
        revision = await revision_repository.update(db, db_obj=revision, obj_in=update_data)
        
        # Notify approvers about the submission
        try:
            from app.services.notification_service import notification_service
            
            # Get potential approvers (simplified - would use approval groups)
            approvers = await user_repository.get_by_role(db, role="approver")
            admin_users = await user_repository.get_by_role(db, role="admin")
            all_approvers = approvers + admin_users
            
            await notification_service.notify_proposal_submitted(
                db, revision=revision, approvers=all_approvers
            )
        except Exception as e:
            # Don't fail the submission if notification fails
            print(f"Failed to send submission notifications: {e}")
        
        return revision
    
    async def withdraw_proposal(
        self,
        db: AsyncSession,
        *,
        revision_id: UUID,
        proposer: User
    ) -> Revision:
        """Withdraw a submitted proposal back to draft"""
        # Get the revision
        revision = await revision_repository.get(db, id=revision_id)
        if not revision:
            raise ProposalNotFoundError("Revision not found")
        
        # Verify proposer ownership
        if revision.proposer_id != proposer.id:
            raise ProposalPermissionError("Not authorized to withdraw this proposal")
        
        # Verify current status (can only withdraw submitted proposals)
        if revision.status != "submitted":
            raise ProposalStatusError(f"Cannot withdraw proposal with status {revision.status}")
        
        # Update status back to draft
        update_data = RevisionUpdate(status="draft")
        revision = await revision_repository.update(db, db_obj=revision, obj_in=update_data)
        
        return revision
    
    async def update_proposal(
        self,
        db: AsyncSession,
        *,
        revision_id: UUID,
        update_data: RevisionUpdate,
        proposer: User
    ) -> Revision:
        """Update a proposal (only allowed for draft proposals)"""
        # Get the revision
        revision = await revision_repository.get(db, id=revision_id)
        if not revision:
            raise ProposalNotFoundError("Revision not found")
        
        # Verify proposer ownership
        if revision.proposer_id != proposer.id:
            raise ProposalPermissionError("Not authorized to update this proposal")
        
        # Only allow updates on draft proposals
        if revision.status != "draft":
            raise ProposalStatusError(f"Cannot update proposal with status {revision.status}")
        
        # Ensure status cannot be changed through this method
        if update_data.status is not None:
            update_data.status = None
        
        # Update the revision
        revision = await revision_repository.update(db, db_obj=revision, obj_in=update_data)
        
        return revision
    
    async def delete_proposal(
        self,
        db: AsyncSession,
        *,
        revision_id: UUID,
        proposer: User
    ) -> None:
        """Delete a proposal (only allowed for draft proposals)"""
        # Get the revision
        revision = await revision_repository.get(db, id=revision_id)
        if not revision:
            raise ProposalNotFoundError("Revision not found")
        
        # Verify proposer ownership
        if revision.proposer_id != proposer.id:
            raise ProposalPermissionError("Not authorized to delete this proposal")
        
        # Only allow deletion of draft proposals
        if revision.status != "draft":
            raise ProposalStatusError(f"Cannot delete proposal with status {revision.status}")
        
        # Delete the revision
        await revision_repository.remove(db, id=revision_id)
    
    async def get_user_proposals(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get proposals created by a specific user"""
        if status:
            return await revision_repository.get_by_proposer_and_status(
                db, proposer_id=user_id, status=status, skip=skip, limit=limit
            )
        else:
            return await revision_repository.get_by_proposer(
                db, proposer_id=user_id, skip=skip, limit=limit
            )
    
    async def get_proposals_for_approval(
        self,
        db: AsyncSession,
        *,
        approver: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[Revision]:
        """Get proposals that need approval from a specific approver"""
        # Get submitted proposals
        submitted_proposals = await revision_repository.get_by_status(
            db, status="submitted", skip=skip, limit=limit
        )
        
        # Filter by approval group if approver has one
        if approver.approval_group_id:
            # Get articles that belong to the approver's group
            group_articles = await article_repository.get_by_approval_group(
                db, approval_group=approver.approval_group_id
            )
            group_article_ids = {article.article_id for article in group_articles}
            
            # Filter proposals for articles in the approver's group
            filtered_proposals = [
                proposal for proposal in submitted_proposals
                if proposal.target_article_id in group_article_ids
            ]
            
            return filtered_proposals
        
        # If no approval group, return all submitted proposals (for admin)
        return submitted_proposals
    
    async def get_proposal_statistics(
        self,
        db: AsyncSession,
        *,
        user_id: Optional[UUID] = None
    ) -> dict:
        """Get proposal statistics"""
        stats = {
            "draft": 0,
            "submitted": 0,
            "approved": 0,
            "rejected": 0,
            "deleted": 0,
            "total": 0
        }
        
        # Get proposals (all or by user)
        if user_id:
            proposals = await revision_repository.get_by_proposer(db, proposer_id=user_id)
        else:
            proposals = await revision_repository.get_multi(db, limit=10000)  # Get all
        
        # Count by status
        for proposal in proposals:
            if proposal.status in stats:
                stats[proposal.status] += 1
            stats["total"] += 1
        
        return stats
    
    async def validate_proposal_data(
        self,
        db: AsyncSession,
        *,
        proposal_data: RevisionCreate
    ) -> dict:
        """
        Validate proposal data before creation
        
        Returns:
            Dict with validation results including is_valid, errors, warnings
        """
        # Use validation utility
        validation_result = validate_proposal_changes(proposal_data)
        
        # Check if target article exists
        target_article = await article_repository.get_by_id(
            db, article_id=proposal_data.target_article_id
        )
        if not target_article:
            validation_result["errors"].append("Target article not found")
            validation_result["is_valid"] = False
        
        # Calculate priority
        validation_result["priority"] = calculate_proposal_priority(proposal_data)
        
        return validation_result


# Create singleton instance
proposal_service = ProposalService()