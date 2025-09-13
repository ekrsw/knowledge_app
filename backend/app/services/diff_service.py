"""
Diff service for analyzing and visualizing changes in revision proposals
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revision import Revision
from app.models.article import Article
from app.models.user import User
from app.repositories.revision import revision_repository
from app.repositories.article import article_repository
from app.repositories.user import user_repository
from app.schemas.diff import (
    RevisionDiff,
    FieldDiff,
    ChangeType,
    DiffSummary,
    ArticleSnapshot,
    ComparisonRequest
)
from app.core.exceptions import ProposalNotFoundError, ArticleNotFoundError
from app.utils.diff_formatter import diff_formatter


class DiffService:
    """Service for managing revision diffs and comparisons"""
    
    # Field metadata for better diff display
    FIELD_METADATA = {
        "title": {
            "label": "タイトル",
            "category": "content",
            "is_critical": True,
            "description": "記事のタイトル"
        },
        "info_category": {
            "label": "情報カテゴリ",
            "category": "metadata",
            "is_critical": True,
            "description": "記事の分類カテゴリ"
        },
        "keywords": {
            "label": "キーワード",
            "category": "content",
            "is_critical": False,
            "description": "検索用キーワード"
        },
        "importance": {
            "label": "重要度",
            "category": "metadata",
            "is_critical": True,
            "description": "記事の重要度レベル"
        },
        "publish_start": {
            "label": "公開開始日",
            "category": "scheduling",
            "is_critical": True,
            "description": "記事の公開開始日時"
        },
        "publish_end": {
            "label": "公開終了日",
            "category": "scheduling",
            "is_critical": True,
            "description": "記事の公開終了日時"
        },
        "target": {
            "label": "対象者",
            "category": "content",
            "is_critical": False,
            "description": "記事の対象読者"
        },
        "question": {
            "label": "質問",
            "category": "content",
            "is_critical": False,
            "description": "記事の質問内容"
        },
        "answer": {
            "label": "回答",
            "category": "content",
            "is_critical": False,
            "description": "記事の回答内容"
        },
        "additional_comment": {
            "label": "追加コメント",
            "category": "content",
            "is_critical": False,
            "description": "記事への追加コメント"
        }
    }
    
    async def generate_revision_diff(
        self,
        db: AsyncSession,
        *,
        revision_id: str
    ) -> RevisionDiff:
        """Generate complete diff for a revision proposal"""
        # Get the revision - convert string ID to UUID
        revision_uuid = UUID(revision_id) if isinstance(revision_id, str) else revision_id
        revision = await revision_repository.get(db, id=revision_uuid)
        if not revision:
            raise ProposalNotFoundError("Revision not found")
        
        # Get the target article
        article = await article_repository.get_by_id(
            db, article_id=revision.target_article_id
        )
        if not article:
            raise ArticleNotFoundError("Target article not found")
        
        # Get proposer information
        proposer = await user_repository.get(db, id=revision.proposer_id)
        proposer_name = proposer.full_name if proposer else "Unknown"
        
        # Generate field diffs
        field_diffs = await self._generate_field_diffs(article, revision)
        
        # Calculate summary information
        total_changes = len([diff for diff in field_diffs if diff.change_type != ChangeType.UNCHANGED])
        critical_changes = len([diff for diff in field_diffs if diff.is_critical and diff.change_type != ChangeType.UNCHANGED])
        change_categories = list(set([
            self.FIELD_METADATA.get(diff.field_name, {}).get("category", "other")
            for diff in field_diffs
            if diff.change_type != ChangeType.UNCHANGED
        ]))
        
        # Determine impact level
        impact_level = self._calculate_impact_level(field_diffs)
        
        return RevisionDiff(
            revision_id=str(revision.revision_id),
            target_article_id=revision.target_article_id,
            target_article_pk=article.article_id if article else revision.target_article_id,
            proposer_name=proposer_name,
            reason=revision.reason,
            status=revision.status,
            created_at=revision.created_at,
            field_diffs=field_diffs,
            total_changes=total_changes,
            critical_changes=critical_changes,
            change_categories=change_categories,
            impact_level=impact_level
        )
    
    async def _generate_field_diffs(
        self,
        article: Article,
        revision: Revision
    ) -> List[FieldDiff]:
        """Generate field-by-field diffs"""
        field_diffs = []
        
        # Compare each field
        fields_to_compare = [
            ("title", article.title, revision.after_title),
            ("info_category", article.info_category, revision.after_info_category),
            ("keywords", article.keywords, revision.after_keywords),
            ("importance", article.importance, revision.after_importance),
            ("publish_start", article.publish_start, revision.after_publish_start),
            ("publish_end", article.publish_end, revision.after_publish_end),
            ("target", article.target, revision.after_target),
            ("question", article.question, revision.after_question),
            ("answer", article.answer, revision.after_answer),
            ("additional_comment", article.additional_comment, revision.after_additional_comment)
        ]
        
        for field_name, old_value, new_value in fields_to_compare:
            field_metadata = self.FIELD_METADATA.get(field_name, {})
            
            # Determine change type
            if new_value is None:
                # No change proposed for this field
                change_type = ChangeType.UNCHANGED
            elif old_value is None and new_value is not None:
                change_type = ChangeType.ADDED
            elif old_value is not None and new_value is None:
                change_type = ChangeType.DELETED
            elif old_value != new_value:
                change_type = ChangeType.MODIFIED
            else:
                change_type = ChangeType.UNCHANGED
            
            # Format values for display
            formatted_old = self._format_value(field_name, old_value)
            formatted_new = self._format_value(field_name, new_value) if new_value is not None else formatted_old
            
            field_diff = FieldDiff(
                field_name=field_name,
                field_label=field_metadata.get("label", field_name),
                change_type=change_type,
                old_value=old_value,
                new_value=new_value if new_value is not None else old_value,
                formatted_old_value=formatted_old,
                formatted_new_value=formatted_new,
                is_critical=field_metadata.get("is_critical", False),
                description=field_metadata.get("description", "")
            )
            
            field_diffs.append(field_diff)
        
        return field_diffs
    
    def _format_value(self, field_name: str, value: Any) -> str:
        """Format a field value for display"""
        if value is None:
            return "未設定"
        
        if field_name == "importance":
            return "重要" if value else "通常"
        elif field_name in ["publish_start", "publish_end"]:
            if isinstance(value, datetime):
                return value.strftime("%Y年%m月%d日 %H:%M")
            return str(value)
        elif isinstance(value, bool):
            return "はい" if value else "いいえ"
        else:
            return str(value) if value else "未設定"
    
    def _calculate_impact_level(self, field_diffs: List[FieldDiff]) -> str:
        """Calculate the overall impact level of changes"""
        critical_changes = sum(1 for diff in field_diffs 
                             if diff.is_critical and diff.change_type != ChangeType.UNCHANGED)
        total_changes = sum(1 for diff in field_diffs 
                          if diff.change_type != ChangeType.UNCHANGED)
        
        if critical_changes >= 3:
            return "critical"
        elif critical_changes >= 2:
            return "high"
        elif critical_changes >= 1:
            return "medium"
        elif total_changes >= 3:
            return "medium"
        elif total_changes >= 1:
            return "low"
        else:
            return "none"
    
    async def generate_diff_summary(
        self,
        db: AsyncSession,
        *,
        revision_id: str
    ) -> DiffSummary:
        """Generate a summary of changes"""
        diff = await self.generate_revision_diff(db, revision_id=revision_id)
        
        # Count changes by type
        changes_by_type = {
            "added": 0,
            "modified": 0,
            "deleted": 0
        }
        
        # Count changes by category
        changes_by_category = {}
        
        for field_diff in diff.field_diffs:
            if field_diff.change_type != ChangeType.UNCHANGED:
                changes_by_type[field_diff.change_type.value] += 1
                
                category = self.FIELD_METADATA.get(field_diff.field_name, {}).get("category", "other")
                changes_by_category[category] = changes_by_category.get(category, 0) + 1
        
        # Estimate review time based on complexity
        estimated_time = self._estimate_review_time(diff.total_changes, diff.critical_changes, diff.impact_level)
        
        return DiffSummary(
            total_changes=diff.total_changes,
            changes_by_type=changes_by_type,
            changes_by_category=changes_by_category,
            critical_changes=diff.critical_changes,
            impact_level=diff.impact_level,
            estimated_review_time=estimated_time
        )
    
    def _estimate_review_time(self, total_changes: int, critical_changes: int, impact_level: str) -> int:
        """Estimate review time in minutes"""
        base_time = 5  # Base 5 minutes
        
        # Add time per change
        time_per_change = 3
        time_per_critical = 5
        
        estimated = base_time + (total_changes * time_per_change) + (critical_changes * time_per_critical)
        
        # Adjust by impact level
        multipliers = {
            "critical": 1.5,
            "high": 1.3,
            "medium": 1.1,
            "low": 1.0,
            "none": 0.5
        }
        
        estimated = int(estimated * multipliers.get(impact_level, 1.0))
        
        # Minimum 5 minutes, maximum 60 minutes
        return max(5, min(60, estimated))
    
    async def create_article_snapshot(
        self,
        db: AsyncSession,
        *,
        article_id: str
    ) -> ArticleSnapshot:
        """Create a snapshot of current article state"""
        article = await article_repository.get_by_id(db, article_id=article_id)
        if not article:
            raise ArticleNotFoundError("Article not found")
        
        return ArticleSnapshot(
            article_id=article.article_id,
            article_pk=article.article_id,
            title=article.title,
            info_category=article.info_category,
            keywords=article.keywords,
            importance=article.importance,
            publish_start=article.publish_start,
            publish_end=article.publish_end,
            target=article.target,
            question=article.question,
            answer=article.answer,
            additional_comment=article.additional_comment,
            snapshot_time=datetime.utcnow()
        )
    
    async def compare_revisions(
        self,
        db: AsyncSession,
        *,
        revision_id_1: str,
        revision_id_2: str
    ) -> Dict[str, Any]:
        """Compare two revisions of the same article"""
        # Get both revisions - convert string IDs to UUID
        revision1_uuid = UUID(revision_id_1) if isinstance(revision_id_1, str) else revision_id_1
        revision2_uuid = UUID(revision_id_2) if isinstance(revision_id_2, str) else revision_id_2
        revision1 = await revision_repository.get(db, id=revision1_uuid)
        revision2 = await revision_repository.get(db, id=revision2_uuid)
        
        if not revision1 or not revision2:
            raise ProposalNotFoundError("One or both revisions not found")
        
        if revision1.target_article_id != revision2.target_article_id:
            raise ValueError("Revisions must target the same article")
        
        # Generate diffs for both
        diff1 = await self.generate_revision_diff(db, revision_id=revision_id_1)
        diff2 = await self.generate_revision_diff(db, revision_id=revision_id_2)
        
        # Compare the diffs
        comparison = {
            "revision_1": diff1,
            "revision_2": diff2,
            "conflicts": self._find_conflicts(diff1.field_diffs, diff2.field_diffs),
            "combined_impact": self._calculate_combined_impact(diff1, diff2)
        }
        
        return comparison
    
    def _find_conflicts(self, diffs1: List[FieldDiff], diffs2: List[FieldDiff]) -> List[Dict[str, Any]]:
        """Find conflicts between two sets of field diffs"""
        conflicts = []
        
        # Create lookup maps
        changes1 = {diff.field_name: diff for diff in diffs1 if diff.change_type != ChangeType.UNCHANGED}
        changes2 = {diff.field_name: diff for diff in diffs2 if diff.change_type != ChangeType.UNCHANGED}
        
        # Find fields changed in both revisions
        common_fields = set(changes1.keys()) & set(changes2.keys())
        
        for field_name in common_fields:
            diff1 = changes1[field_name]
            diff2 = changes2[field_name]
            
            # Check if they propose different values
            if diff1.new_value != diff2.new_value:
                conflicts.append({
                    "field_name": field_name,
                    "field_label": diff1.field_label,
                    "revision_1_value": diff1.new_value,
                    "revision_2_value": diff2.new_value,
                    "conflict_type": "value_mismatch",
                    "is_critical": diff1.is_critical
                })
        
        return conflicts
    
    def _calculate_combined_impact(self, diff1: RevisionDiff, diff2: RevisionDiff) -> str:
        """Calculate the combined impact level of two revisions"""
        impact_scores = {
            "none": 0,
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4
        }
        
        score1 = impact_scores.get(diff1.impact_level, 0)
        score2 = impact_scores.get(diff2.impact_level, 0)
        
        combined_score = min(4, score1 + score2)  # Cap at critical
        
        score_to_level = {0: "none", 1: "low", 2: "medium", 3: "high", 4: "critical"}
        return score_to_level[combined_score]
    
    async def get_revision_history_diff(
        self,
        db: AsyncSession,
        *,
        article_id: str,
        limit: int = 10
    ) -> List[RevisionDiff]:
        """Get diff history for an article"""
        # Get revisions for the article
        revisions = await revision_repository.get_by_target_article(
            db, target_article_id=article_id
        )
        
        # Limit results
        revisions = revisions[:limit]
        
        # Generate diffs for each revision
        diffs = []
        for revision in revisions:
            try:
                diff = await self.generate_revision_diff(db, revision_id=str(revision.revision_id))
                diffs.append(diff)
            except Exception:
                # Skip revisions that can't be processed
                continue
        
        return diffs
    
    async def generate_formatted_diff(
        self,
        db: AsyncSession,
        *,
        revision_id: str,
        include_formatting: bool = True
    ) -> Dict[str, Any]:
        """Generate a formatted diff with display-ready information"""
        # Get the basic diff
        diff = await self.generate_revision_diff(db, revision_id=revision_id)
        
        # Format for display
        formatted_diff = {
            "basic_info": {
                "revision_id": diff.revision_id,
                "target_article_id": diff.target_article_id,
                "proposer_name": diff.proposer_name,
                "reason": diff.reason,
                "status": diff.status,
                "created_at": diff.created_at.isoformat(),
                "impact_level": diff_formatter.format_impact_level(diff.impact_level),
                "summary_text": diff_formatter.generate_diff_summary_text(diff.field_diffs)
            },
            "field_changes": [],
            "statistics": {
                "total_changes": diff.total_changes,
                "critical_changes": diff.critical_changes,
                "change_categories": diff.change_categories,
                "estimated_reading_time": diff_formatter.estimate_reading_time(diff.field_diffs)
            }
        }
        
        # Format each field diff
        if include_formatting:
            for field_diff in diff.field_diffs:
                formatted_field = diff_formatter.format_field_diff_for_display(field_diff)
                formatted_diff["field_changes"].append(formatted_field)
        else:
            formatted_diff["field_changes"] = diff.field_diffs
        
        # Generate approval checklist
        formatted_diff["approval_checklist"] = diff_formatter.generate_approval_checklist(diff.field_diffs)
        
        return formatted_diff
    
    async def get_bulk_diff_summaries(
        self,
        db: AsyncSession,
        *,
        revision_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """Get summary information for multiple revisions efficiently"""
        summaries = []
        
        for revision_id in revision_ids:
            try:
                summary = await self.generate_diff_summary(db, revision_id=revision_id)
                diff = await self.generate_revision_diff(db, revision_id=revision_id)
                
                bulk_summary = {
                    "revision_id": revision_id,
                    "target_article_id": diff.target_article_id,
                    "proposer_name": diff.proposer_name,
                    "status": diff.status,
                    "created_at": diff.created_at.isoformat(),
                    "total_changes": summary.total_changes,
                    "critical_changes": summary.critical_changes,
                    "impact_level": summary.impact_level,
                    "estimated_review_time": summary.estimated_review_time,
                    "summary_text": diff_formatter.generate_diff_summary_text(diff.field_diffs)[:100] + "..."
                }
                
                summaries.append(bulk_summary)
            except Exception:
                # Skip revisions that can't be processed
                continue
        
        return summaries


# Create singleton instance
diff_service = DiffService()