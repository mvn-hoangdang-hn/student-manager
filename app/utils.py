from typing import Any, Optional

def success_response(data: Any = None, message: Optional[str] = None):
    return {
        "success": True,
        "message": message or "success",
        "data": data,
    }

def error_response(error: str, details: Any = None):
    return {
        "success": False,
        "error": error,
        "details": details,
    }
