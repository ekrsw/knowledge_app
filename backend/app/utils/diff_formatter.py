"""
Utilities for formatting and visualizing diffs
"""
from typing import List, Dict, Any, Optional, Tuple
import re
import difflib
from datetime import datetime

from app.schemas.diff import FieldDiff, ChangeType


class DiffFormatter:
    """Utility class for formatting diff output"""
    
    @staticmethod
    def format_text_diff(old_text: str, new_text: str) -> Dict[str, Any]:
        """
        Generate a formatted text diff using difflib
        
        Args:
            old_text: Original text
            new_text: Modified text
            
        Returns:
            Dict containing formatted diff information
        """
        if not old_text:
            old_text = ""
        if not new_text:
            new_text = ""
        
        # Split into lines for better diff
        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)
        
        # Generate unified diff
        unified_diff = list(difflib.unified_diff(
            old_lines, new_lines,
            fromfile="変更前",
            tofile="変更後",
            lineterm=""
        ))
        
        # Generate HTML diff
        html_diff = difflib.HtmlDiff()
        html_output = html_diff.make_table(
            old_lines, new_lines,
            fromdesc="変更前",
            todesc="変更後",
            context=True,
            numlines=3
        )
        
        # Calculate change statistics
        stats = DiffFormatter._calculate_text_stats(old_text, new_text)
        
        return {
            "unified_diff": unified_diff,
            "html_diff": html_output,
            "stats": stats,
            "has_changes": old_text.strip() != new_text.strip()
        }
    
    @staticmethod
    def _calculate_text_stats(old_text: str, new_text: str) -> Dict[str, int]:
        """Calculate statistics about text changes"""
        old_words = len(old_text.split()) if old_text else 0
        new_words = len(new_text.split()) if new_text else 0
        old_chars = len(old_text) if old_text else 0
        new_chars = len(new_text) if new_text else 0
        
        return {
            "old_word_count": old_words,
            "new_word_count": new_words,
            "word_change": new_words - old_words,
            "old_char_count": old_chars,
            "new_char_count": new_chars,
            "char_change": new_chars - old_chars
        }
    
    @staticmethod
    def format_field_diff_for_display(field_diff: FieldDiff) -> Dict[str, Any]:
        """Format a field diff for display in UI"""
        display_info = {
            "field_name": field_diff.field_name,
            "field_label": field_diff.field_label,
            "change_type": field_diff.change_type.value,
            "is_critical": field_diff.is_critical,
            "description": field_diff.description,
            "css_class": DiffFormatter._get_css_class(field_diff.change_type, field_diff.is_critical)
        }
        
        # Handle different value types
        if field_diff.change_type == ChangeType.UNCHANGED:
            display_info["display_value"] = field_diff.formatted_old_value
            display_info["change_description"] = "変更なし"
        elif field_diff.change_type == ChangeType.ADDED:
            display_info["display_value"] = field_diff.formatted_new_value
            display_info["change_description"] = f"追加: {field_diff.formatted_new_value}"
        elif field_diff.change_type == ChangeType.DELETED:
            display_info["display_value"] = field_diff.formatted_old_value
            display_info["change_description"] = f"削除: {field_diff.formatted_old_value}"
        elif field_diff.change_type == ChangeType.MODIFIED:
            display_info["old_display_value"] = field_diff.formatted_old_value
            display_info["new_display_value"] = field_diff.formatted_new_value
            display_info["change_description"] = (
                f"{field_diff.formatted_old_value} → {field_diff.formatted_new_value}"
            )
            
            # For text fields, generate detailed diff
            if isinstance(field_diff.old_value, str) and isinstance(field_diff.new_value, str):
                if len(field_diff.old_value) > 50 or len(field_diff.new_value) > 50:
                    display_info["text_diff"] = DiffFormatter.format_text_diff(
                        field_diff.old_value, field_diff.new_value
                    )
        
        return display_info
    
    @staticmethod
    def _get_css_class(change_type: ChangeType, is_critical: bool) -> str:
        """Get CSS class for styling the diff"""
        base_class = f"diff-{change_type.value}"
        if is_critical:
            base_class += " diff-critical"
        return base_class
    
    @staticmethod
    def generate_diff_summary_text(field_diffs: List[FieldDiff]) -> str:
        """Generate a human-readable summary of changes"""
        if not field_diffs:
            return "変更はありません。"
        
        changes = [diff for diff in field_diffs if diff.change_type != ChangeType.UNCHANGED]
        if not changes:
            return "変更はありません。"
        
        summary_parts = []
        
        # Group changes by type
        added = [d for d in changes if d.change_type == ChangeType.ADDED]
        modified = [d for d in changes if d.change_type == ChangeType.MODIFIED]
        deleted = [d for d in changes if d.change_type == ChangeType.DELETED]
        
        if added:
            fields = [d.field_label for d in added]
            summary_parts.append(f"追加: {', '.join(fields)}")
        
        if modified:
            fields = [d.field_label for d in modified]
            summary_parts.append(f"変更: {', '.join(fields)}")
        
        if deleted:
            fields = [d.field_label for d in deleted]
            summary_parts.append(f"削除: {', '.join(fields)}")
        
        # Add critical change warning
        critical_changes = [d for d in changes if d.is_critical]
        if critical_changes:
            summary_parts.append(f"※重要な変更が{len(critical_changes)}件含まれています")
        
        return "。".join(summary_parts) + "。"
    
    @staticmethod
    def format_impact_level(impact_level: str) -> Dict[str, str]:
        """Format impact level for display"""
        impact_info = {
            "none": {"label": "影響なし", "color": "gray", "description": "変更による影響はありません"},
            "low": {"label": "軽微", "color": "green", "description": "軽微な変更です"},
            "medium": {"label": "中程度", "color": "yellow", "description": "注意が必要な変更です"},
            "high": {"label": "高", "color": "orange", "description": "重要な変更が含まれています"},
            "critical": {"label": "重大", "color": "red", "description": "システムに大きな影響を与える可能性があります"}
        }
        
        return impact_info.get(impact_level, impact_info["medium"])
    
    @staticmethod
    def generate_approval_checklist(field_diffs: List[FieldDiff]) -> List[Dict[str, Any]]:
        """Generate a checklist for approval review"""
        checklist = []
        
        # Standard checks
        checklist.append({
            "item": "変更理由の妥当性を確認",
            "category": "基本確認",
            "is_required": True,
            "description": "提案された変更の理由が適切かどうか確認してください"
        })
        
        # Check each changed field
        critical_changes = [d for d in field_diffs if d.is_critical and d.change_type != ChangeType.UNCHANGED]
        
        for diff in critical_changes:
            if diff.field_name == "title":
                checklist.append({
                    "item": "タイトル変更の影響確認",
                    "category": "重要確認",
                    "is_required": True,
                    "description": "タイトル変更がSEOや検索性に与える影響を確認"
                })
            elif diff.field_name == "info_category":
                checklist.append({
                    "item": "カテゴリ変更の妥当性確認",
                    "category": "重要確認",
                    "is_required": True,
                    "description": "カテゴリ変更が適切な分類になっているか確認"
                })
            elif diff.field_name == "importance":
                checklist.append({
                    "item": "重要度変更の影響確認",
                    "category": "重要確認",
                    "is_required": True,
                    "description": "重要度変更が表示順位に与える影響を確認"
                })
            elif diff.field_name in ["publish_start", "publish_end"]:
                checklist.append({
                    "item": "公開日程変更の妥当性確認",
                    "category": "重要確認",
                    "is_required": True,
                    "description": "公開日程の変更が適切かどうか確認"
                })
        
        # Final approval check
        checklist.append({
            "item": "全体的な変更内容の承認",
            "category": "最終確認",
            "is_required": True,
            "description": "すべての変更内容を総合的に判断して承認可否を決定"
        })
        
        return checklist
    
    @staticmethod
    def estimate_reading_time(field_diffs: List[FieldDiff]) -> int:
        """Estimate time needed to read through the changes (in seconds)"""
        base_time = 30  # 30 seconds base
        
        for diff in field_diffs:
            if diff.change_type == ChangeType.UNCHANGED:
                continue
            
            # Add time based on field type and content length
            if diff.field_name in ["question", "answer", "additional_comment"]:
                # Text fields take longer to review
                if diff.new_value:
                    char_count = len(str(diff.new_value))
                    # Rough estimate: 5 characters per second reading speed
                    base_time += char_count // 5
            elif diff.is_critical:
                # Critical fields take more time to review
                base_time += 15
            else:
                # Regular fields
                base_time += 5
        
        # Minimum 30 seconds, maximum 10 minutes
        return max(30, min(600, base_time))


# Create utility instance
diff_formatter = DiffFormatter()