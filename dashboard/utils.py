from django.contrib.auth.models import User
from .models import AuditLog


def log_action(user, action, description, ip_address=None, related_model=None, related_id=None):
    """
    Create an audit log entry for important actions.
    
    Args:
        user: The user who performed the action
        action: The action type (from AuditLog.ACTION_CHOICES)
        description: Human-readable description of the action
        ip_address: Optional IP address of the user
        related_model: Optional name of the related model
        related_id: Optional ID of the related object
    """
    AuditLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip_address,
        related_model=related_model or '',
        related_id=related_id
    )