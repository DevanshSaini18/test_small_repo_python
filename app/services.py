from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.models import (
    Organization, User, Team, Item, Tag, Comment, Attachment,
    ActivityLog, APIKey, Webhook, UsageLog,
    ItemStatus, PriorityLevel, UserRole
)
from app.schemas import (
    OrganizationCreate, UserCreate, TeamCreate, ItemCreate, ItemUpdate,
    CommentCreate, APIKeyCreate, WebhookCreate, TagCreate
)
from app.auth import get_password_hash, generate_api_key

# ============= Organization Services =============
def create_organization(db: Session, org: OrganizationCreate) -> Organization:
    """Create a new organization."""
    db_org = Organization(**org.dict())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def get_organization(db: Session, org_id: int) -> Optional[Organization]:
    """Get organization by ID."""
    return db.query(Organization).filter(Organization.id == org_id).first()

# ============= User Services =============
def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user with hashed password."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        organization_id=user.organization_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log activity
    log_activity(db, "created", "user", db_user.id, user_id=db_user.id)
    
    return db_user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()

def get_users_by_organization(db: Session, org_id: int) -> List[User]:
    """Get all users in an organization."""
    return db.query(User).filter(User.organization_id == org_id).all()

# ============= Team Services =============
def create_team(db: Session, team: TeamCreate, org_id: int, user: User) -> Team:
    """Create a new team."""
    db_team = Team(
        name=team.name,
        description=team.description,
        organization_id=org_id
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    
    log_activity(db, "created", "team", db_team.id, user_id=user.id)
    
    return db_team

def add_user_to_team(db: Session, team_id: int, user_id: int) -> Team:
    """Add a user to a team."""
    team = db.query(Team).filter(Team.id == team_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    
    if team and user:
        team.members.append(user)
        db.commit()
        db.refresh(team)
    
    return team

# ============= Item Services =============
def create_item(db: Session, item: ItemCreate, org_id: int, user: User) -> Item:
    """Create a new item."""
    db_item = Item(
        title=item.title,
        description=item.description,
        status=item.status,
        priority=item.priority,
        due_date=item.due_date,
        estimated_hours=item.estimated_hours,
        organization_id=org_id,
        team_id=item.team_id,
        parent_item_id=item.parent_item_id,
        created_by_id=user.id
    )
    db.add(db_item)
    db.flush()
    
    # Add assignees
    if item.assignee_ids:
        assignees = db.query(User).filter(User.id.in_(item.assignee_ids)).all()
        db_item.assignees.extend(assignees)
    
    # Add tags
    if item.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(item.tag_ids)).all()
        db_item.tags.extend(tags)
    
    db.commit()
    db.refresh(db_item)
    
    # Log activity
    log_activity(db, "created", "item", db_item.id, user_id=user.id, item_id=db_item.id)
    
    return db_item

def get_item(db: Session, item_id: int, org_id: int) -> Optional[Item]:
    """Get item by ID within organization."""
    return db.query(Item).filter(
        Item.id == item_id,
        Item.organization_id == org_id
    ).first()

def get_items(
    db: Session,
    org_id: int,
    team_id: Optional[int] = None,
    status: Optional[ItemStatus] = None,
    priority: Optional[PriorityLevel] = None,
    assigned_to: Optional[int] = None,
    search_text: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Item]:
    """Get items with filters."""
    query = db.query(Item).filter(Item.organization_id == org_id)
    
    if team_id:
        query = query.filter(Item.team_id == team_id)
    if status:
        query = query.filter(Item.status == status)
    if priority:
        query = query.filter(Item.priority == priority)
    if assigned_to:
        query = query.join(Item.assignees).filter(User.id == assigned_to)
    if search_text:
        search_pattern = f"%{search_text}%"
        query = query.filter(
            or_(
                Item.title.ilike(search_pattern),
                Item.description.ilike(search_pattern)
            )
        )
    
    return query.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()

def update_item(db: Session, item_id: int, item_update: ItemUpdate, org_id: int, user: User) -> Optional[Item]:
    """Update an item."""
    db_item = get_item(db, item_id, org_id)
    if not db_item:
        return None
    
    update_data = item_update.dict(exclude_unset=True)
    
    # Track changes for activity log
    changes = {}
    
    # Handle assignees separately
    if "assignee_ids" in update_data:
        assignee_ids = update_data.pop("assignee_ids")
        assignees = db.query(User).filter(User.id.in_(assignee_ids)).all()
        db_item.assignees = assignees
        changes["assignees"] = assignee_ids
    
    # Handle tags separately
    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        db_item.tags = tags
        changes["tags"] = tag_ids
    
    # Update other fields
    for field, value in update_data.items():
        if hasattr(db_item, field):
            old_value = getattr(db_item, field)
            if old_value != value:
                changes[field] = {"from": str(old_value), "to": str(value)}
                setattr(db_item, field, value)
    
    # Mark as completed if status changed to DONE
    if db_item.status == ItemStatus.DONE and not db_item.completed_at:
        db_item.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_item)
    
    # Log activity
    if changes:
        log_activity(
            db, "updated", "item", db_item.id,
            user_id=user.id,
            item_id=db_item.id,
            details=json.dumps(changes)
        )
    
    return db_item

def delete_item(db: Session, item_id: int, org_id: int, user: User) -> bool:
    """Delete an item."""
    db_item = get_item(db, item_id, org_id)
    if not db_item:
        return False
    
    log_activity(db, "deleted", "item", item_id, user_id=user.id)
    
    db.delete(db_item)
    db.commit()
    return True

# ============= Comment Services =============
def create_comment(db: Session, comment: CommentCreate, user: User, org_id: int) -> Optional[Comment]:
    """Create a comment on an item."""
    # Verify item belongs to organization
    item = get_item(db, comment.item_id, org_id)
    if not item:
        return None
    
    db_comment = Comment(
        content=comment.content,
        item_id=comment.item_id,
        author_id=user.id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    log_activity(db, "commented", "item", item.id, user_id=user.id, item_id=item.id)
    
    return db_comment

def get_comments_by_item(db: Session, item_id: int, org_id: int) -> List[Comment]:
    """Get all comments for an item."""
    item = get_item(db, item_id, org_id)
    if not item:
        return []
    
    return db.query(Comment).filter(Comment.item_id == item_id).order_by(Comment.created_at.desc()).all()

# ============= Tag Services =============
def create_tag(db: Session, tag: TagCreate) -> Tag:
    """Create a new tag."""
    db_tag = Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def get_tags(db: Session) -> List[Tag]:
    """Get all tags."""
    return db.query(Tag).all()

# ============= API Key Services =============
def create_api_key(db: Session, api_key_data: APIKeyCreate, org_id: int) -> APIKey:
    """Create a new API key."""
    key = generate_api_key()
    db_api_key = APIKey(
        key=key,
        name=api_key_data.name,
        organization_id=org_id,
        expires_at=api_key_data.expires_at
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

def get_api_keys(db: Session, org_id: int) -> List[APIKey]:
    """Get all API keys for an organization."""
    return db.query(APIKey).filter(APIKey.organization_id == org_id).all()

# ============= Webhook Services =============
def create_webhook(db: Session, webhook: WebhookCreate, org_id: int) -> Webhook:
    """Create a new webhook."""
    db_webhook = Webhook(
        url=webhook.url,
        events=webhook.events,
        secret=webhook.secret,
        organization_id=org_id
    )
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return db_webhook

def get_webhooks(db: Session, org_id: int) -> List[Webhook]:
    """Get all webhooks for an organization."""
    return db.query(Webhook).filter(Webhook.organization_id == org_id).all()

# ============= Activity Log Services =============
def log_activity(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: int,
    user_id: Optional[int] = None,
    item_id: Optional[int] = None,
    details: Optional[str] = None
):
    """Log an activity."""
    activity = ActivityLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        item_id=item_id,
        details=details
    )
    db.add(activity)
    db.commit()

def get_activity_logs(
    db: Session,
    org_id: int,
    item_id: Optional[int] = None,
    limit: int = 50
) -> List[ActivityLog]:
    """Get activity logs."""
    query = db.query(ActivityLog).join(User).filter(User.organization_id == org_id)
    
    if item_id:
        query = query.filter(ActivityLog.item_id == item_id)
    
    return query.order_by(ActivityLog.created_at.desc()).limit(limit).all()

# ============= Analytics Services =============
def get_item_analytics(db: Session, org_id: int):
    """Get item analytics for an organization."""
    total_items = db.query(func.count(Item.id)).filter(Item.organization_id == org_id).scalar()
    
    # By status
    by_status = {}
    for status in ItemStatus:
        count = db.query(func.count(Item.id)).filter(
            Item.organization_id == org_id,
            Item.status == status
        ).scalar()
        by_status[status.value] = count
    
    # By priority
    by_priority = {}
    for priority in PriorityLevel:
        count = db.query(func.count(Item.id)).filter(
            Item.organization_id == org_id,
            Item.priority == priority
        ).scalar()
        by_priority[priority.value] = count
    
    # Overdue items
    overdue = db.query(func.count(Item.id)).filter(
        Item.organization_id == org_id,
        Item.due_date < datetime.utcnow(),
        Item.status != ItemStatus.DONE
    ).scalar()
    
    # Completed this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    completed_week = db.query(func.count(Item.id)).filter(
        Item.organization_id == org_id,
        Item.completed_at >= week_ago
    ).scalar()
    
    # Average completion time
    avg_time = db.query(func.avg(Item.actual_hours)).filter(
        Item.organization_id == org_id,
        Item.actual_hours.isnot(None)
    ).scalar()
    
    return {
        "total_items": total_items,
        "by_status": by_status,
        "by_priority": by_priority,
        "overdue_items": overdue,
        "completed_this_week": completed_week,
        "avg_completion_time_hours": float(avg_time) if avg_time else None
    }

def log_usage(db: Session, org_id: int, endpoint: str, method: str, status_code: int, response_time_ms: int):
    """Log API usage."""
    usage = UsageLog(
        organization_id=org_id,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        response_time_ms=response_time_ms
    )
    db.add(usage)
    db.commit()

def get_usage_analytics(db: Session, org_id: int, days: int = 7):
    """Get usage analytics."""
    since = datetime.utcnow() - timedelta(days=days)
    
    logs = db.query(UsageLog).filter(
        UsageLog.organization_id == org_id,
        UsageLog.timestamp >= since
    ).all()
    
    total_requests = len(logs)
    
    # By endpoint
    by_endpoint = {}
    for log in logs:
        by_endpoint[log.endpoint] = by_endpoint.get(log.endpoint, 0) + 1
    
    # Average response time
    avg_response = sum(log.response_time_ms for log in logs) / total_requests if total_requests > 0 else 0
    
    # Error rate
    errors = sum(1 for log in logs if log.status_code >= 400)
    error_rate = (errors / total_requests * 100) if total_requests > 0 else 0
    
    return {
        "total_requests": total_requests,
        "requests_by_endpoint": by_endpoint,
        "avg_response_time_ms": avg_response,
        "error_rate": error_rate
    }
