"""
Custom exceptions for the Knowledge Revision System
"""


class ProposalError(Exception):
    """Base exception for proposal-related errors"""
    pass


class ProposalNotFoundError(ProposalError):
    """Raised when a proposal is not found"""
    pass


class ProposalPermissionError(ProposalError):
    """Raised when user doesn't have permission for proposal operation"""
    pass


class ProposalStatusError(ProposalError):
    """Raised when proposal operation is not allowed for current status"""
    pass


class ProposalValidationError(ProposalError):
    """Raised when proposal data validation fails"""
    pass


class ArticleNotFoundError(Exception):
    """Raised when target article is not found"""
    pass


class ApprovalError(Exception):
    """Base exception for approval-related errors"""
    pass


class ApprovalPermissionError(ApprovalError):
    """Raised when user doesn't have permission for approval operation"""
    pass


class ApprovalStatusError(ApprovalError):
    """Raised when approval operation is not allowed for current status"""
    pass