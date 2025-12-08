"""
Export service for generating reports and exporting data in various formats.
Supports CSV, JSON, and summary reports for items, teams, and analytics.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import csv
import json
import io
from collections import defaultdict

from app.models import Item, User, Team, Organization, Comment, ActivityLog, ItemStatus, PriorityLevel
from app.services import get_items, get_item_analytics


class ExportService:
    """Service for exporting data in various formats."""
    
    def export_items_to_csv(
        self,
        db: Session,
        org_id: int,
        team_id: Optional[int] = None,
        status: Optional[ItemStatus] = None,
        priority: Optional[PriorityLevel] = None
    ) -> str:
        """
        Export items to CSV format.
        
        Args:
            db: Database session
            org_id: Organization ID
            team_id: Optional team filter
            status: Optional status filter
            priority: Optional priority filter
            
        Returns:
            CSV string
        """
        items = get_items(db, org_id, team_id, status, priority, skip=0, limit=10000)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Title', 'Description', 'Status', 'Priority',
            'Team ID', 'Created By', 'Assignees', 'Tags',
            'Created At', 'Due Date', 'Completed At',
            'Estimated Hours', 'Actual Hours'
        ])
        
        # Write data
        for item in items:
            assignees = ', '.join([a.full_name for a in item.assignees])
            tags = ', '.join([t.name for t in item.tags])
            created_by = item.created_by.full_name if item.created_by else 'Unknown'
            
            writer.writerow([
                item.id,
                item.title,
                item.description,
                item.status.value,
                item.priority.value,
                item.team_id,
                created_by,
                assignees,
                tags,
                item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                item.due_date.strftime('%Y-%m-%d %H:%M:%S') if item.due_date else '',
                item.completed_at.strftime('%Y-%m-%d %H:%M:%S') if item.completed_at else '',
                item.estimated_hours,
                item.actual_hours
            ])
        
        return output.getvalue()
    
    def export_items_to_json(
        self,
        db: Session,
        org_id: int,
        team_id: Optional[int] = None,
        status: Optional[ItemStatus] = None,
        priority: Optional[PriorityLevel] = None,
        include_comments: bool = False
    ) -> str:
        """
        Export items to JSON format.
        
        Args:
            db: Database session
            org_id: Organization ID
            team_id: Optional team filter
            status: Optional status filter
            priority: Optional priority filter
            include_comments: Whether to include comments
            
        Returns:
            JSON string
        """
        items = get_items(db, org_id, team_id, status, priority, skip=0, limit=10000)
        
        items_data = []
        for item in items:
            item_dict = {
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'status': item.status.value,
                'priority': item.priority.value,
                'team_id': item.team_id,
                'parent_item_id': item.parent_item_id,
                'created_by': {
                    'id': item.created_by.id,
                    'name': item.created_by.full_name,
                    'email': item.created_by.email
                } if item.created_by else None,
                'assignees': [
                    {
                        'id': a.id,
                        'name': a.full_name,
                        'email': a.email
                    } for a in item.assignees
                ],
                'tags': [
                    {
                        'id': t.id,
                        'name': t.name,
                        'color': t.color
                    } for t in item.tags
                ],
                'created_at': item.created_at.isoformat(),
                'due_date': item.due_date.isoformat() if item.due_date else None,
                'completed_at': item.completed_at.isoformat() if item.completed_at else None,
                'estimated_hours': item.estimated_hours,
                'actual_hours': item.actual_hours
            }
            
            if include_comments:
                item_dict['comments'] = [
                    {
                        'id': c.id,
                        'content': c.content,
                        'author': {
                            'id': c.author.id,
                            'name': c.author.full_name
                        },
                        'created_at': c.created_at.isoformat()
                    } for c in item.comments
                ]
            
            items_data.append(item_dict)
        
        return json.dumps({
            'export_date': datetime.utcnow().isoformat(),
            'organization_id': org_id,
            'total_items': len(items_data),
            'items': items_data
        }, indent=2)
    
    def generate_team_report(self, db: Session, team_id: int) -> Dict[str, Any]:
        """
        Generate a comprehensive report for a team.
        
        Args:
            db: Database session
            team_id: Team ID
            
        Returns:
            Dictionary containing team report data
        """
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return {'error': 'Team not found'}
        
        items = db.query(Item).filter(Item.team_id == team_id).all()
        
        # Calculate statistics
        total_items = len(items)
        completed_items = sum(1 for item in items if item.status == ItemStatus.DONE)
        in_progress_items = sum(1 for item in items if item.status == ItemStatus.IN_PROGRESS)
        overdue_items = sum(1 for item in items if item.due_date and item.due_date < datetime.utcnow() and item.status != ItemStatus.DONE)
        
        # Status breakdown
        status_breakdown = defaultdict(int)
        for item in items:
            status_breakdown[item.status.value] += 1
        
        # Priority breakdown
        priority_breakdown = defaultdict(int)
        for item in items:
            priority_breakdown[item.priority.value] += 1
        
        # Member workload
        member_workload = defaultdict(lambda: {'assigned': 0, 'completed': 0})
        for item in items:
            for assignee in item.assignees:
                member_workload[assignee.full_name]['assigned'] += 1
                if item.status == ItemStatus.DONE:
                    member_workload[assignee.full_name]['completed'] += 1
        
        # Calculate completion rate
        completion_rate = (completed_items / total_items * 100) if total_items > 0 else 0
        
        return {
            'team': {
                'id': team.id,
                'name': team.name,
                'description': team.description,
                'member_count': len(team.members)
            },
            'summary': {
                'total_items': total_items,
                'completed_items': completed_items,
                'in_progress_items': in_progress_items,
                'overdue_items': overdue_items,
                'completion_rate': round(completion_rate, 2)
            },
            'status_breakdown': dict(status_breakdown),
            'priority_breakdown': dict(priority_breakdown),
            'member_workload': dict(member_workload),
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def generate_user_report(self, db: Session, user_id: int, org_id: int) -> Dict[str, Any]:
        """
        Generate a report for a specific user's activities and assignments.
        
        Args:
            db: Database session
            user_id: User ID
            org_id: Organization ID
            
        Returns:
            Dictionary containing user report data
        """
        user = db.query(User).filter(User.id == user_id, User.organization_id == org_id).first()
        if not user:
            return {'error': 'User not found'}
        
        # Get all items assigned to user
        assigned_items = db.query(Item).join(Item.assignees).filter(
            User.id == user_id,
            Item.organization_id == org_id
        ).all()
        
        # Get items created by user
        created_items = db.query(Item).filter(
            Item.created_by_id == user_id,
            Item.organization_id == org_id
        ).all()
        
        # Calculate statistics
        total_assigned = len(assigned_items)
        completed_assigned = sum(1 for item in assigned_items if item.status == ItemStatus.DONE)
        overdue_assigned = sum(1 for item in assigned_items if item.due_date and item.due_date < datetime.utcnow() and item.status != ItemStatus.DONE)
        
        # Priority breakdown for assigned items
        priority_breakdown = defaultdict(int)
        for item in assigned_items:
            priority_breakdown[item.priority.value] += 1
        
        # Get recent activity
        recent_activities = db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id
        ).order_by(ActivityLog.created_at.desc()).limit(10).all()
        
        # Calculate total hours
        total_estimated_hours = sum(item.estimated_hours or 0 for item in assigned_items)
        total_actual_hours = sum(item.actual_hours or 0 for item in assigned_items if item.actual_hours)
        
        return {
            'user': {
                'id': user.id,
                'name': user.full_name,
                'email': user.email,
                'role': user.role.value
            },
            'assigned_items': {
                'total': total_assigned,
                'completed': completed_assigned,
                'in_progress': sum(1 for item in assigned_items if item.status == ItemStatus.IN_PROGRESS),
                'overdue': overdue_assigned,
                'completion_rate': round((completed_assigned / total_assigned * 100) if total_assigned > 0 else 0, 2)
            },
            'created_items': {
                'total': len(created_items)
            },
            'priority_breakdown': dict(priority_breakdown),
            'hours': {
                'total_estimated': total_estimated_hours,
                'total_actual': total_actual_hours,
                'variance': total_actual_hours - total_estimated_hours if total_actual_hours > 0 else None
            },
            'recent_activities': [
                {
                    'action': activity.action,
                    'entity_type': activity.entity_type,
                    'created_at': activity.created_at.isoformat()
                } for activity in recent_activities
            ],
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def generate_organization_summary(self, db: Session, org_id: int) -> Dict[str, Any]:
        """
        Generate a comprehensive summary report for an organization.
        
        Args:
            db: Database session
            org_id: Organization ID
            
        Returns:
            Dictionary containing organization summary
        """
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return {'error': 'Organization not found'}
        
        # Get analytics
        analytics = get_item_analytics(db, org_id)
        
        # Get team count
        team_count = db.query(Team).filter(Team.organization_id == org_id).count()
        
        # Get user count
        user_count = db.query(User).filter(User.organization_id == org_id).count()
        
        # Get active users (users who created or were assigned items in last 30 days)
        thirty_days_ago = datetime.utcnow() - datetime.timedelta(days=30)
        active_users = db.query(User).join(Item.assignees).filter(
            User.organization_id == org_id,
            Item.created_at >= thirty_days_ago
        ).distinct().count()
        
        # Get top contributors (users who created most items)
        top_contributors = db.query(
            User.full_name,
            db.func.count(Item.id).label('items_created')
        ).join(Item, Item.created_by_id == User.id).filter(
            User.organization_id == org_id
        ).group_by(User.id, User.full_name).order_by(
            db.func.count(Item.id).desc()
        ).limit(5).all()
        
        return {
            'organization': {
                'id': org.id,
                'name': org.name,
                'created_at': org.created_at.isoformat()
            },
            'overview': {
                'total_teams': team_count,
                'total_users': user_count,
                'active_users_30d': active_users
            },
            'items': analytics,
            'top_contributors': [
                {
                    'name': name,
                    'items_created': count
                } for name, count in top_contributors
            ],
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def export_activity_log_to_csv(self, db: Session, org_id: int, limit: int = 1000) -> str:
        """
        Export activity logs to CSV format.
        
        Args:
            db: Database session
            org_id: Organization ID
            limit: Maximum number of records to export
            
        Returns:
            CSV string
        """
        activities = db.query(ActivityLog).join(User).filter(
            User.organization_id == org_id
        ).order_by(ActivityLog.created_at.desc()).limit(limit).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Action', 'Entity Type', 'Entity ID',
            'User', 'Item ID', 'Details', 'Created At'
        ])
        
        # Write data
        for activity in activities:
            user_name = activity.user.full_name if activity.user else 'System'
            
            writer.writerow([
                activity.id,
                activity.action,
                activity.entity_type,
                activity.entity_id,
                user_name,
                activity.item_id,
                activity.details,
                activity.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return output.getvalue()


# Singleton instance
export_service = ExportService()
