"""
Analytics and reporting endpoints
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, get_current_active_user, get_current_approver_user, get_current_admin_user
from app.models.user import User

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get analytics overview for the current user"""
    from app.repositories.revision import revision_repository
    from app.repositories.notification import notification_repository
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get user's revisions
    if current_user.role == "admin":
        all_revisions = await revision_repository.get_multi(db, limit=10000)
    else:
        all_revisions = await revision_repository.get_by_proposer(
            db, proposer_id=current_user.id, limit=1000
        )
    
    # Filter by date range
    period_revisions = [
        r for r in all_revisions
        if start_date <= r.created_at <= end_date
    ]
    
    # Calculate proposal metrics
    proposal_metrics = {
        "total_created": len(period_revisions),
        "by_status": {},
        "daily_activity": {}
    }
    
    for revision in period_revisions:
        # Count by status
        status = revision.status
        proposal_metrics["by_status"][status] = proposal_metrics["by_status"].get(status, 0) + 1
        
        # Count by day
        day_key = revision.created_at.date().isoformat()
        proposal_metrics["daily_activity"][day_key] = proposal_metrics["daily_activity"].get(day_key, 0) + 1
    
    # Get notification metrics
    all_notifications = await notification_repository.get_by_user(
        db, user_id=current_user.id, limit=1000
    )
    
    period_notifications = [
        n for n in all_notifications
        if start_date <= n.created_at <= end_date
    ]
    
    notification_metrics = {
        "total_received": len(period_notifications),
        "unread_count": len([n for n in period_notifications if not n.is_read]),
        "by_type": {}
    }
    
    for notification in period_notifications:
        ntype = notification.type
        notification_metrics["by_type"][ntype] = notification_metrics["by_type"].get(ntype, 0) + 1
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "proposals": proposal_metrics,
        "notifications": notification_metrics,
        "user_role": current_user.role,
        "summary": {
            "most_active_day": max(proposal_metrics["daily_activity"].items(), key=lambda x: x[1])[0] if proposal_metrics["daily_activity"] else None,
            "avg_proposals_per_day": len(period_revisions) / days if days > 0 else 0,
            "approval_rate": (proposal_metrics["by_status"].get("approved", 0) / len(period_revisions) * 100) if period_revisions else 0
        }
    }


@router.get("/trends")
async def get_trend_analysis(
    metric: str = Query(default="proposals", pattern="^(proposals|approvals|notifications)$"),
    period: str = Query(default="weekly", pattern="^(daily|weekly|monthly)$"),
    weeks_back: int = Query(default=12, ge=1, le=52),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get trend analysis for various metrics"""
    from app.repositories.revision import revision_repository
    from app.repositories.notification import notification_repository
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(weeks=weeks_back)
    
    # Define period grouping
    if period == "daily":
        group_format = "%Y-%m-%d"
        delta = timedelta(days=1)
    elif period == "weekly":
        group_format = "%Y-W%U"
        delta = timedelta(weeks=1)
    else:  # monthly
        group_format = "%Y-%m"
        delta = timedelta(days=30)
    
    # Get data based on metric type
    trend_data = {}
    
    if metric == "proposals":
        # Get revisions data
        if current_user.role == "admin":
            revisions = await revision_repository.get_multi(db, limit=10000)
        else:
            revisions = await revision_repository.get_by_proposer(
                db, proposer_id=current_user.id, limit=1000
            )
        
        # Group by time period
        for revision in revisions:
            if start_date <= revision.created_at <= end_date:
                period_key = revision.created_at.strftime(group_format)
                if period_key not in trend_data:
                    trend_data[period_key] = {"created": 0, "submitted": 0, "approved": 0, "rejected": 0}
                
                trend_data[period_key]["created"] += 1
                if revision.status == "submitted":
                    trend_data[period_key]["submitted"] += 1
                elif revision.status == "approved":
                    trend_data[period_key]["approved"] += 1
                elif revision.status == "rejected":
                    trend_data[period_key]["rejected"] += 1
    
    elif metric == "notifications":
        # Get notifications data
        notifications = await notification_repository.get_by_user(
            db, user_id=current_user.id, limit=1000
        )
        
        # Group by time period
        for notification in notifications:
            if start_date <= notification.created_at <= end_date:
                period_key = notification.created_at.strftime(group_format)
                if period_key not in trend_data:
                    trend_data[period_key] = {"received": 0, "read": 0, "unread": 0}
                
                trend_data[period_key]["received"] += 1
                if notification.is_read:
                    trend_data[period_key]["read"] += 1
                else:
                    trend_data[period_key]["unread"] += 1
    
    # Calculate trend statistics
    data_points = list(trend_data.keys())
    data_points.sort()
    
    trend_stats = {
        "total_periods": len(data_points),
        "trend_direction": "stable",
        "growth_rate": 0
    }
    
    if len(data_points) >= 2:
        # Simple trend calculation
        first_half = data_points[:len(data_points)//2]
        second_half = data_points[len(data_points)//2:]
        
        first_avg = sum(trend_data[p].get("created", trend_data[p].get("received", 0)) for p in first_half) / len(first_half)
        second_avg = sum(trend_data[p].get("created", trend_data[p].get("received", 0)) for p in second_half) / len(second_half)
        
        if second_avg > first_avg * 1.1:
            trend_stats["trend_direction"] = "increasing"
        elif second_avg < first_avg * 0.9:
            trend_stats["trend_direction"] = "decreasing"
        
        trend_stats["growth_rate"] = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
    
    return {
        "metric": metric,
        "period": period,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "data": trend_data,
        "trend_stats": trend_stats,
        "periods": sorted(data_points)
    }


@router.get("/performance")
async def get_performance_metrics(
    days: int = Query(default=30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_approver_user)
):
    """Get performance metrics for approvers"""
    from app.repositories.revision import revision_repository
    from app.services.approval_service import approval_service
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get approver's workload
    workload = await approval_service.get_approver_workload(db, approver=current_user)
    
    # Get approval history (simplified - would normally query approval_history table)
    all_revisions = await revision_repository.get_multi(db, limit=1000)
    
    # Filter revisions processed by this approver
    processed_revisions = [
        r for r in all_revisions
        if (r.approver_id == current_user.id and 
            r.processed_at and
            start_date <= r.processed_at <= end_date)
    ]
    
    # Calculate performance metrics
    total_processed = len(processed_revisions)
    approved_count = len([r for r in processed_revisions if r.status == "approved"])
    rejected_count = len([r for r in processed_revisions if r.status == "rejected"])
    
    # Calculate average processing time
    total_processing_time = 0
    processing_times = []
    
    for revision in processed_revisions:
        if revision.created_at and revision.processed_at:
            processing_time = (revision.processed_at - revision.created_at).total_seconds() / 3600  # hours
            processing_times.append(processing_time)
            total_processing_time += processing_time
    
    avg_processing_time = total_processing_time / len(processing_times) if processing_times else 0
    
    # Calculate daily throughput
    daily_throughput = {}
    for revision in processed_revisions:
        day_key = revision.processed_at.date().isoformat()
        daily_throughput[day_key] = daily_throughput.get(day_key, 0) + 1
    
    avg_daily_throughput = total_processed / days if days > 0 else 0
    
    performance_metrics = {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        },
        "processing_stats": {
            "total_processed": total_processed,
            "approved": approved_count,
            "rejected": rejected_count,
            "approval_rate": (approved_count / total_processed * 100) if total_processed > 0 else 0,
            "rejection_rate": (rejected_count / total_processed * 100) if total_processed > 0 else 0
        },
        "timing_stats": {
            "average_processing_time_hours": round(avg_processing_time, 2),
            "fastest_processing_time_hours": round(min(processing_times), 2) if processing_times else 0,
            "slowest_processing_time_hours": round(max(processing_times), 2) if processing_times else 0,
            "median_processing_time_hours": round(sorted(processing_times)[len(processing_times)//2], 2) if processing_times else 0
        },
        "throughput_stats": {
            "average_daily_throughput": round(avg_daily_throughput, 2),
            "max_daily_throughput": max(daily_throughput.values()) if daily_throughput else 0,
            "daily_breakdown": daily_throughput
        },
        "current_workload": {
            "pending_count": workload.pending_count,
            "overdue_count": workload.overdue_count,
            "capacity_status": workload.current_capacity
        },
        "performance_indicators": {
            "efficiency_score": min(100, (total_processed / days * 10)) if days > 0 else 0,  # Simplified scoring
            "quality_score": approved_count / max(1, total_processed) * 100,
            "timeliness_score": max(0, 100 - (workload.overdue_count * 10))
        }
    }
    
    return performance_metrics


@router.get("/reports/summary")
async def get_summary_report(
    report_type: str = Query(default="weekly", pattern="^(daily|weekly|monthly)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate summary reports"""
    from app.services.proposal_service import proposal_service
    from app.services.approval_service import approval_service
    
    # Determine date range based on report type
    end_date = datetime.utcnow()
    if report_type == "daily":
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif report_type == "weekly":
        days_since_monday = end_date.weekday()
        start_date = end_date - timedelta(days=days_since_monday)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:  # monthly
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get proposal statistics
    proposal_stats = await proposal_service.get_proposal_statistics(
        db, user_id=current_user.id if current_user.role != "admin" else None
    )
    
    # Get system metrics (if admin or approver)
    approval_metrics = None
    if current_user.role in ["admin", "approver"]:
        try:
            approval_metrics = await approval_service.get_approval_metrics(
                db, days_back=(end_date - start_date).days
            )
        except Exception:
            approval_metrics = None
    
    # Generate report
    report = {
        "report_type": report_type,
        "generated_at": datetime.utcnow().isoformat(),
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "user_context": {
            "user_id": str(current_user.id),
            "role": current_user.role,
            "full_name": current_user.full_name
        },
        "proposal_summary": proposal_stats,
        "approval_summary": approval_metrics,
        "key_insights": []
    }
    
    # Generate insights
    insights = []
    
    if proposal_stats["total"] > 0:
        approval_rate = proposal_stats.get("approved", 0) / proposal_stats["total"] * 100
        if approval_rate > 80:
            insights.append("High approval rate indicates well-prepared proposals")
        elif approval_rate < 40:
            insights.append("Low approval rate suggests need for better proposal preparation")
    
    if approval_metrics and approval_metrics["total_overdue"] > 5:
        insights.append("High number of overdue approvals requires attention")
    
    if current_user.role == "admin" and approval_metrics:
        if approval_metrics["average_approval_time"] > 48:
            insights.append("Average approval time exceeds target of 48 hours")
    
    report["key_insights"] = insights
    
    return report


@router.get("/export/data")
async def export_analytics_data(
    format: str = Query(default="json", pattern="^(json|csv)$"),
    data_type: str = Query(default="proposals", pattern="^(proposals|approvals|notifications)$"),
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export analytics data in various formats"""
    from app.repositories.revision import revision_repository
    from app.repositories.notification import notification_repository
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    export_data = []
    
    if data_type == "proposals":
        # Get revisions data
        if current_user.role == "admin":
            revisions = await revision_repository.get_multi(db, limit=10000)
        else:
            revisions = await revision_repository.get_by_proposer(
                db, proposer_id=current_user.id, limit=1000
            )
        
        # Filter and format data
        for revision in revisions:
            if start_date <= revision.created_at <= end_date:
                export_data.append({
                    "revision_id": str(revision.revision_id),
                    "target_article_id": revision.target_article_id,
                    "status": revision.status,
                    "created_at": revision.created_at.isoformat(),
                    "processed_at": revision.processed_at.isoformat() if revision.processed_at else None,
                    "proposer_id": str(revision.proposer_id),
                    "approver_id": str(revision.approver_id) if revision.approver_id else None,
                    "reason": revision.reason
                })
    
    elif data_type == "notifications":
        # Get notifications data
        notifications = await notification_repository.get_by_user(
            db, user_id=current_user.id, limit=1000
        )
        
        # Filter and format data
        for notification in notifications:
            if start_date <= notification.created_at <= end_date:
                export_data.append({
                    "notification_id": str(notification.id),
                    "type": notification.type,
                    "message": notification.message,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat(),
                    "revision_id": str(notification.revision_id) if notification.revision_id else None
                })
    
    # Format response based on requested format
    if format == "json":
        return {
            "data_type": data_type,
            "format": format,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "record_count": len(export_data),
            "data": export_data
        }
    else:  # CSV format
        import csv
        import io
        
        if not export_data:
            return {"error": "No data available for export"}
        
        # Convert to CSV string
        output = io.StringIO()
        if export_data:
            writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
            writer.writeheader()
            writer.writerows(export_data)
        
        csv_content = output.getvalue()
        output.close()
        
        return {
            "data_type": data_type,
            "format": format,
            "record_count": len(export_data),
            "csv_data": csv_content
        }


@router.get("/dashboards/executive", dependencies=[Depends(get_current_admin_user)])
async def get_executive_dashboard(
    db: AsyncSession = Depends(get_db)
):
    """Get executive-level dashboard (admin only)"""
    from app.repositories.user import user_repository
    from app.repositories.revision import revision_repository
    from app.services.approval_service import approval_service
    
    # Get high-level metrics
    all_users = await user_repository.get_multi(db, limit=10000)
    all_revisions = await revision_repository.get_multi(db, limit=10000)
    
    # System health indicators
    total_users = len(all_users)
    active_users = len([u for u in all_users if u.is_active])
    total_proposals = len(all_revisions)
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_proposals = [r for r in all_revisions if r.created_at >= week_ago]
    
    # Approval metrics
    approval_metrics = await approval_service.get_approval_metrics(db, days_back=30)
    
    # Calculate key performance indicators
    system_health = {
        "overall_status": "healthy",
        "user_growth": len([u for u in all_users if u.created_at >= week_ago]),
        "proposal_velocity": len(recent_proposals),
        "approval_efficiency": 100 - (approval_metrics["total_overdue"] / max(1, approval_metrics["total_pending"]) * 100)
    }
    
    # Risk indicators
    risk_factors = []
    if approval_metrics["total_overdue"] > 20:
        risk_factors.append("High number of overdue approvals")
    if approval_metrics["average_approval_time"] > 72:
        risk_factors.append("Approval times exceeding target")
    if system_health["approval_efficiency"] < 70:
        risk_factors.append("Low approval efficiency")
    
    return {
        "dashboard_type": "executive",
        "generated_at": datetime.utcnow().isoformat(),
        "system_overview": {
            "total_users": total_users,
            "active_users": active_users,
            "total_proposals": total_proposals,
            "system_health": system_health
        },
        "key_metrics": {
            "weekly_proposals": len(recent_proposals),
            "approval_rate": approval_metrics["approval_rate"],
            "average_approval_time": approval_metrics["average_approval_time"],
            "pending_approvals": approval_metrics["total_pending"],
            "overdue_approvals": approval_metrics["total_overdue"]
        },
        "performance_indicators": approval_metrics["by_priority"],
        "risk_assessment": {
            "risk_level": "high" if len(risk_factors) > 2 else "medium" if risk_factors else "low",
            "risk_factors": risk_factors
        },
        "recommendations": approval_metrics["bottlenecks"][:3]  # Top 3 recommendations
    }