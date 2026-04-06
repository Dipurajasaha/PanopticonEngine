import logging
from sqlalchemy.orm import Session
import models.db_models as db_models

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_action(db: Session, user_id: int, action: str, resource: str, details: str = None):
    log_entry = db_models.AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        details=details
    )
    db.add(log_entry)
    
    # Log to server terminal
    logger.info(f"Audit Log - User ID: {user_id}, Action: {action}, Resource: {resource}, Details: {details}")
    
    db.commit()