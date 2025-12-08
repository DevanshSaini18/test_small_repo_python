from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import User, Organization, UserRole, ItemStatus, PriorityLevel
from app.schemas import (
    OrganizationCreate, OrganizationRead, OrganizationUpdate,
    UserCreate, UserRead, UserLogin, Token,
    TeamCreate, TeamRead, TeamUpdate,
    ItemCreate, ItemRead, ItemUpdate,
    CommentCreate, CommentRead,
    TagCreate, TagRead,
    APIKeyCreate, APIKeyRead,
    WebhookCreate, WebhookRead, WebhookUpdate,
    ActivityLogRead,
    ItemAnalytics, UsageAnalytics
)
from app.services import (
    create_organization, get_organization,
    create_user, get_user_by_email, get_users_by_organization,
    create_team, add_user_to_team,
    create_item, get_item, get_items, update_item, delete_item,
    create_comment, get_comments_by_item,
    create_tag, get_tags,
    create_api_key, get_api_keys,
    create_webhook, get_webhooks,
    get_activity_logs,
    get_item_analytics, get_usage_analytics
)
from app.dependencies import (
    get_current_active_user,
    get_current_organization,
    require_role,
    verify_api_key
)
from app.auth import verify_password, create_access_token
from app.notifications import notification_service
from app.export import export_service

router = APIRouter()

# ============= Authentication Routes =============
@router.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verify organization exists
    org = get_organization(db, user.organization_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return create_user(db, user)

@router.post("/auth/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token."""
    user = get_user_by_email(db, credentials.email)
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/me", response_model=UserRead)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

# ============= Organization Routes =============
@router.post("/organizations", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_new_organization(org: OrganizationCreate, db: Session = Depends(get_db)):
    """Create a new organization."""
    return create_organization(db, org)

@router.get("/organizations/current", response_model=OrganizationRead)
def get_my_organization(org: Organization = Depends(get_current_organization)):
    """Get current user's organization."""
    return org

@router.get("/organizations/{org_id}/users", response_model=List[UserRead])
def list_organization_users(
    org_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all users in the organization."""
    if current_user.organization_id != org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return get_users_by_organization(db, org_id)

# ============= Team Routes =============
@router.post("/teams", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_new_team(
    team: TeamCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Create a new team (Admin only)."""
    return create_team(db, team, org.id, current_user)

@router.post("/teams/{team_id}/members/{user_id}", response_model=TeamRead)
def add_team_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Add a user to a team (Admin only)."""
    return add_user_to_team(db, team_id, user_id)

# ============= Item Routes =============
@router.post("/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_new_item(
    item: ItemCreate,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Create a new item."""
    return create_item(db, item, org.id, current_user)

@router.get("/items/{item_id}", response_model=ItemRead)
def read_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Get an item by ID."""
    db_item = get_item(db, item_id, org.id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return db_item

@router.get("/items", response_model=List[ItemRead])
def list_items(
    team_id: Optional[int] = Query(None),
    status: Optional[ItemStatus] = Query(None),
    priority: Optional[PriorityLevel] = Query(None),
    assigned_to: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """List items with optional filters."""
    return get_items(db, org.id, team_id, status, priority, assigned_to, skip, limit)

@router.put("/items/{item_id}", response_model=ItemRead)
def update_existing_item(
    item_id: int,
    item: ItemUpdate,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Update an item."""
    updated_item = update_item(db, item_id, item, org.id, current_user)
    if not updated_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return updated_item

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Delete an item."""
    if not delete_item(db, item_id, org.id, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return None

# ============= Comment Routes =============
@router.post("/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_new_comment(
    comment: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Create a comment on an item."""
    db_comment = create_comment(db, comment, current_user, org.id)
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return db_comment

@router.get("/items/{item_id}/comments", response_model=List[CommentRead])
def list_item_comments(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Get all comments for an item."""
    return get_comments_by_item(db, item_id, org.id)

# ============= Tag Routes =============
@router.post("/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_new_tag(
    tag: TagCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new tag."""
    return create_tag(db, tag)

@router.get("/tags", response_model=List[TagRead])
def list_tags(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all tags."""
    return get_tags(db)

# ============= API Key Routes =============
@router.post("/api-keys", response_model=APIKeyRead, status_code=status.HTTP_201_CREATED)
def create_new_api_key(
    api_key: APIKeyCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Create a new API key (Admin only)."""
    return create_api_key(db, api_key, org.id)

@router.get("/api-keys", response_model=List[APIKeyRead])
def list_api_keys(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """List all API keys (Admin only)."""
    return get_api_keys(db, org.id)

# ============= Webhook Routes =============
@router.post("/webhooks", response_model=WebhookRead, status_code=status.HTTP_201_CREATED)
def create_new_webhook(
    webhook: WebhookCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Create a new webhook (Admin only)."""
    return create_webhook(db, webhook, org.id)

@router.get("/webhooks", response_model=List[WebhookRead])
def list_webhooks(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """List all webhooks (Admin only)."""
    return get_webhooks(db, org.id)

# ============= Activity Log Routes =============
@router.get("/activity", response_model=List[ActivityLogRead])
def list_activity_logs(
    item_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Get activity logs."""
    return get_activity_logs(db, org.id, item_id, limit)

# ============= Analytics Routes =============
@router.get("/analytics/items", response_model=ItemAnalytics)
def get_items_analytics(
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Get item analytics."""
    return get_item_analytics(db, org.id)

@router.get("/analytics/usage", response_model=UsageAnalytics)
def get_usage_stats(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Get usage analytics (Admin only)."""
    return get_usage_analytics(db, org.id, days)

# ============= Notification Routes =============
@router.post("/notifications/due-reminders")
def send_due_reminders(
    days_before: int = Query(1, ge=1, le=7),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Send due date reminders (Admin only)."""
    result = notification_service.send_due_date_reminders(db, days_before)
    return result

@router.post("/notifications/overdue")
def send_overdue_alerts(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Send overdue item notifications (Admin only)."""
    result = notification_service.send_overdue_notifications(db)
    return result

# ============= Export Routes =============
@router.get("/export/items/csv")
def export_items_csv(
    team_id: Optional[int] = Query(None),
    status: Optional[ItemStatus] = Query(None),
    priority: Optional[PriorityLevel] = Query(None),
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Export items to CSV format."""
    from fastapi.responses import Response
    
    csv_data = export_service.export_items_to_csv(db, org.id, team_id, status, priority)
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=items_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

@router.get("/export/items/json")
def export_items_json(
    team_id: Optional[int] = Query(None),
    status: Optional[ItemStatus] = Query(None),
    priority: Optional[PriorityLevel] = Query(None),
    include_comments: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Export items to JSON format."""
    from fastapi.responses import Response
    
    json_data = export_service.export_items_to_json(db, org.id, team_id, status, priority, include_comments)
    
    return Response(
        content=json_data,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=items_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
    )

@router.get("/export/activity-log/csv")
def export_activity_csv(
    limit: int = Query(1000, ge=1, le=10000),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Export activity logs to CSV (Admin only)."""
    from fastapi.responses import Response
    
    csv_data = export_service.export_activity_log_to_csv(db, org.id, limit)
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=activity_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

# ============= Report Routes =============
@router.get("/reports/team/{team_id}")
def get_team_report(
    team_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive team report."""
    return export_service.generate_team_report(db, team_id)

@router.get("/reports/user/{user_id}")
def get_user_report(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Get user activity report."""
    # Users can only view their own report unless they're admin
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return export_service.generate_user_report(db, user_id, org.id)

@router.get("/reports/organization")
def get_organization_report(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
):
    """Get organization summary report (Admin only)."""
    return export_service.generate_organization_summary(db, org.id)
