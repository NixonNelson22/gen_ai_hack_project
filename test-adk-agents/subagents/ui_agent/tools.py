from datetime import datetime

def get_current_time() -> dict:
    """
    Tool to get the current time.
    Returns:
        dict: A dictionary containing the current time in ISO 8601 format.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return {"timestamp": current_time}