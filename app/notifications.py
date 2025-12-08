"""
Notification service for sending emails and alerts to users.
Supports item assignments, comments, due date reminders, and status changes.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import User, Item, Organization, ItemStatus
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for handling all notification-related operations."""
    
    def __init__(self, smtp_host: str = "smtp.gmail.com", smtp_port: int = 587):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.from_email = "noreply@taskmanager.com"
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email notification.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Attach plain text
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # In production, you would actually send the email
            # For now, we'll just log it
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def notify_item_assigned(self, db: Session, item: Item, assignee: User) -> bool:
        """
        Notify a user when they are assigned to an item.
        
        Args:
            db: Database session
            item: The item being assigned
            assignee: User being assigned
            
        Returns:
            True if notification sent successfully
        """
        subject = f"You've been assigned to: {item.title}"
        
        body = f"""
Hello {assignee.full_name},

You have been assigned to a new item:

Title: {item.title}
Description: {item.description}
Priority: {item.priority.value}
Status: {item.status.value}
Due Date: {item.due_date.strftime('%Y-%m-%d') if item.due_date else 'Not set'}

Please review and take action as needed.

Best regards,
Task Manager Team
        """
        
        html_body = f"""
<html>
<body>
    <h2>New Assignment</h2>
    <p>Hello {assignee.full_name},</p>
    <p>You have been assigned to a new item:</p>
    <ul>
        <li><strong>Title:</strong> {item.title}</li>
        <li><strong>Description:</strong> {item.description}</li>
        <li><strong>Priority:</strong> {item.priority.value}</li>
        <li><strong>Status:</strong> {item.status.value}</li>
        <li><strong>Due Date:</strong> {item.due_date.strftime('%Y-%m-%d') if item.due_date else 'Not set'}</li>
    </ul>
    <p>Please review and take action as needed.</p>
    <p>Best regards,<br>Task Manager Team</p>
</body>
</html>
        """
        
        return self.send_email(assignee.email, subject, body, html_body)
    
    def notify_comment_added(self, db: Session, item: Item, commenter: User, comment_text: str) -> List[bool]:
        """
        Notify all assignees when a new comment is added to an item.
        
        Args:
            db: Database session
            item: The item that received a comment
            commenter: User who added the comment
            comment_text: The comment text
            
        Returns:
            List of success statuses for each notification sent
        """
        results = []
        
        for assignee in item.assignees:
            # Don't notify the commenter
            if assignee.id == commenter.id:
                continue
            
            subject = f"New comment on: {item.title}"
            
            body = f"""
Hello {assignee.full_name},

{commenter.full_name} added a comment to "{item.title}":

"{comment_text}"

Item Status: {item.status.value}
Priority: {item.priority.value}

Best regards,
Task Manager Team
            """
            
            html_body = f"""
<html>
<body>
    <h2>New Comment</h2>
    <p>Hello {assignee.full_name},</p>
    <p><strong>{commenter.full_name}</strong> added a comment to "{item.title}":</p>
    <blockquote style="border-left: 3px solid #ccc; padding-left: 10px; margin: 10px 0;">
        {comment_text}
    </blockquote>
    <p><strong>Item Status:</strong> {item.status.value}<br>
    <strong>Priority:</strong> {item.priority.value}</p>
    <p>Best regards,<br>Task Manager Team</p>
</body>
</html>
            """
            
            result = self.send_email(assignee.email, subject, body, html_body)
            results.append(result)
        
        return results
    
    def notify_status_changed(self, db: Session, item: Item, old_status: ItemStatus, new_status: ItemStatus, changed_by: User) -> List[bool]:
        """
        Notify assignees when item status changes.
        
        Args:
            db: Database session
            item: The item whose status changed
            old_status: Previous status
            new_status: New status
            changed_by: User who changed the status
            
        Returns:
            List of success statuses for each notification sent
        """
        results = []
        
        for assignee in item.assignees:
            subject = f"Status updated: {item.title}"
            
            body = f"""
Hello {assignee.full_name},

The status of "{item.title}" has been updated by {changed_by.full_name}:

From: {old_status.value}
To: {new_status.value}

Priority: {item.priority.value}
Due Date: {item.due_date.strftime('%Y-%m-%d') if item.due_date else 'Not set'}

Best regards,
Task Manager Team
            """
            
            html_body = f"""
<html>
<body>
    <h2>Status Update</h2>
    <p>Hello {assignee.full_name},</p>
    <p>The status of "<strong>{item.title}</strong>" has been updated by {changed_by.full_name}:</p>
    <p style="margin: 20px 0;">
        <span style="background-color: #f0f0f0; padding: 5px 10px; border-radius: 3px;">{old_status.value}</span>
        →
        <span style="background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 3px;">{new_status.value}</span>
    </p>
    <p><strong>Priority:</strong> {item.priority.value}<br>
    <strong>Due Date:</strong> {item.due_date.strftime('%Y-%m-%d') if item.due_date else 'Not set'}</p>
    <p>Best regards,<br>Task Manager Team</p>
</body>
</html>
            """
            
            result = self.send_email(assignee.email, subject, body, html_body)
            results.append(result)
        
        return results
    
    def send_due_date_reminders(self, db: Session, days_before: int = 1) -> Dict[str, Any]:
        """
        Send reminders for items due soon.
        
        Args:
            db: Database session
            days_before: Number of days before due date to send reminder
            
        Returns:
            Dictionary with statistics about reminders sent
        """
        target_date = datetime.utcnow() + timedelta(days=days_before)
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Find items due on target date that are not completed
        items = db.query(Item).filter(
            and_(
                Item.due_date >= start_of_day,
                Item.due_date <= end_of_day,
                Item.status != ItemStatus.DONE
            )
        ).all()
        
        total_items = len(items)
        total_notifications = 0
        successful_notifications = 0
        
        for item in items:
            for assignee in item.assignees:
                total_notifications += 1
                
                subject = f"Reminder: {item.title} due in {days_before} day(s)"
                
                body = f"""
Hello {assignee.full_name},

This is a reminder that the following item is due in {days_before} day(s):

Title: {item.title}
Description: {item.description}
Priority: {item.priority.value}
Status: {item.status.value}
Due Date: {item.due_date.strftime('%Y-%m-%d %H:%M')}

Please ensure timely completion.

Best regards,
Task Manager Team
                """
                
                html_body = f"""
<html>
<body>
    <h2>Due Date Reminder</h2>
    <p>Hello {assignee.full_name},</p>
    <p>This is a reminder that the following item is due in <strong>{days_before} day(s)</strong>:</p>
    <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
        <h3 style="margin-top: 0;">{item.title}</h3>
        <p><strong>Description:</strong> {item.description}</p>
        <p><strong>Priority:</strong> {item.priority.value}<br>
        <strong>Status:</strong> {item.status.value}<br>
        <strong>Due Date:</strong> {item.due_date.strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    <p>Please ensure timely completion.</p>
    <p>Best regards,<br>Task Manager Team</p>
</body>
</html>
                """
                
                if self.send_email(assignee.email, subject, body, html_body):
                    successful_notifications += 1
        
        return {
            "total_items": total_items,
            "total_notifications": total_notifications,
            "successful_notifications": successful_notifications,
            "failed_notifications": total_notifications - successful_notifications
        }
    
    def send_overdue_notifications(self, db: Session) -> Dict[str, Any]:
        """
        Send notifications for overdue items.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with statistics about notifications sent
        """
        now = datetime.utcnow()
        
        # Find overdue items that are not completed
        items = db.query(Item).filter(
            and_(
                Item.due_date < now,
                Item.status != ItemStatus.DONE
            )
        ).all()
        
        total_items = len(items)
        total_notifications = 0
        successful_notifications = 0
        
        for item in items:
            days_overdue = (now - item.due_date).days
            
            for assignee in item.assignees:
                total_notifications += 1
                
                subject = f"OVERDUE: {item.title}"
                
                body = f"""
Hello {assignee.full_name},

URGENT: The following item is OVERDUE by {days_overdue} day(s):

Title: {item.title}
Description: {item.description}
Priority: {item.priority.value}
Status: {item.status.value}
Due Date: {item.due_date.strftime('%Y-%m-%d %H:%M')}

Please take immediate action.

Best regards,
Task Manager Team
                """
                
                html_body = f"""
<html>
<body>
    <h2 style="color: #d32f2f;">OVERDUE ITEM</h2>
    <p>Hello {assignee.full_name},</p>
    <p><strong>URGENT:</strong> The following item is OVERDUE by <strong>{days_overdue} day(s)</strong>:</p>
    <div style="background-color: #ffebee; border-left: 4px solid #d32f2f; padding: 15px; margin: 20px 0;">
        <h3 style="margin-top: 0; color: #d32f2f;">{item.title}</h3>
        <p><strong>Description:</strong> {item.description}</p>
        <p><strong>Priority:</strong> {item.priority.value}<br>
        <strong>Status:</strong> {item.status.value}<br>
        <strong>Due Date:</strong> {item.due_date.strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    <p><strong>Please take immediate action.</strong></p>
    <p>Best regards,<br>Task Manager Team</p>
</body>
</html>
                """
                
                if self.send_email(assignee.email, subject, body, html_body):
                    successful_notifications += 1
        
        return {
            "total_items": total_items,
            "total_notifications": total_notifications,
            "successful_notifications": successful_notifications,
            "failed_notifications": total_notifications - successful_notifications
        }


# Singleton instance
notification_service = NotificationService()
