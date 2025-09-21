import logging
import json
from datetime import datetime

logger = logging.getLogger("redaction_audit")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("redaction_audit.log")
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

def log_redaction(item_type, content, box):
    """
    Log redaction event.
    item_type: e.g. 'signature', 'email', 'phone'
    content: redacted text or description
    box: bounding box coordinates
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "item_type": item_type,
        "content": content,
        "box": box
    }
    logger.info(json.dumps(log_entry))
