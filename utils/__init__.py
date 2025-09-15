# Utils package for Student Management System

from .auth import hash_password, verify_password, create_access_token, get_current_user, get_current_active_user, require_role
from .database import db
from .helpers import serialize_doc, log_activity, send_sms, send_whatsapp, check_and_send_stock_alert

__all__ = [
    'hash_password',
    'verify_password', 
    'create_access_token',
    'get_current_user',
    'get_current_active_user',
    'require_role',
    'db',
    'serialize_doc',
    'log_activity',
    'send_sms',
    'send_whatsapp',
    'check_and_send_stock_alert'
]
