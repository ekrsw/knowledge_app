"""
Validation utilities for the Knowledge Revision System
"""
from typing import Dict, Any, List, Optional
from app.schemas.revision import RevisionCreate


def validate_proposal_changes(proposal_data: RevisionCreate) -> Dict[str, Any]:
    """
    Validate and analyze proposal changes
    
    Returns:
        Dict containing validation results and change analysis
    """
    result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "changes_count": 0,
        "change_types": []
    }
    
    # Check required fields
    if not proposal_data.target_article_id or not proposal_data.target_article_id.strip():
        result["errors"].append("Target article ID is required")
        result["is_valid"] = False
    
    if not proposal_data.target_article_pk or not proposal_data.target_article_pk.strip():
        result["errors"].append("Target article PK is required")
        result["is_valid"] = False
    
    if not proposal_data.reason or not proposal_data.reason.strip():
        result["errors"].append("Reason for change is required")
        result["is_valid"] = False
    
    # Count and categorize changes
    changes = []
    
    if proposal_data.after_title is not None:
        changes.append("title")
    if proposal_data.after_info_category is not None:
        changes.append("info_category")
    if proposal_data.after_keywords is not None:
        changes.append("keywords")
    if proposal_data.after_importance is not None:
        changes.append("importance")
    if proposal_data.after_publish_start is not None:
        changes.append("publish_start")
    if proposal_data.after_publish_end is not None:
        changes.append("publish_end")
    if proposal_data.after_target is not None:
        changes.append("target")
    if proposal_data.after_question is not None:
        changes.append("question")
    if proposal_data.after_answer is not None:
        changes.append("answer")
    if proposal_data.after_additional_comment is not None:
        changes.append("additional_comment")
    
    result["changes_count"] = len(changes)
    result["change_types"] = changes
    
    if result["changes_count"] == 0:
        result["errors"].append("At least one field change must be specified")
        result["is_valid"] = False
    
    # Add warnings for potentially problematic changes
    if proposal_data.after_importance is not None:
        result["warnings"].append("Importance level change may affect article visibility")
    
    if proposal_data.after_publish_start is not None or proposal_data.after_publish_end is not None:
        result["warnings"].append("Publication date changes may affect article availability")
    
    return result


def get_proposal_status_transitions() -> Dict[str, List[str]]:
    """
    Get valid status transitions for proposals
    
    Returns:
        Dict mapping current status to list of valid next statuses
    """
    return {
        "draft": ["submitted", "deleted"],
        "submitted": ["approved", "rejected", "draft"],  # draft = withdrawn
        "approved": [],  # Final state
        "rejected": [],  # Final state
        "deleted": []    # Final state
    }


def is_valid_status_transition(current_status: str, new_status: str) -> bool:
    """
    Check if a status transition is valid
    
    Args:
        current_status: Current proposal status
        new_status: Desired new status
        
    Returns:
        True if transition is valid, False otherwise
    """
    transitions = get_proposal_status_transitions()
    return new_status in transitions.get(current_status, [])


def get_required_permissions_for_status(status: str) -> List[str]:
    """
    Get required permissions for each proposal status
    
    Args:
        status: Proposal status
        
    Returns:
        List of required permissions/roles
    """
    permissions = {
        "draft": ["owner"],
        "submitted": ["owner"],  # Owner can withdraw
        "approved": ["approver", "admin"],
        "rejected": ["approver", "admin"],
        "deleted": ["owner", "admin"]
    }
    
    return permissions.get(status, [])


def calculate_proposal_priority(proposal_data: RevisionCreate) -> str:
    """
    Calculate proposal priority based on change types
    
    Args:
        proposal_data: Proposal data
        
    Returns:
        Priority level (low, medium, high, critical)
    """
    high_impact_changes = [
        proposal_data.after_importance,
        proposal_data.after_publish_start,
        proposal_data.after_publish_end
    ]
    
    medium_impact_changes = [
        proposal_data.after_title,
        proposal_data.after_info_category
    ]
    
    # Count non-None changes
    high_count = sum(1 for change in high_impact_changes if change is not None)
    medium_count = sum(1 for change in medium_impact_changes if change is not None)
    
    if high_count > 0:
        return "high"
    elif medium_count > 0:
        return "medium"
    else:
        return "low"