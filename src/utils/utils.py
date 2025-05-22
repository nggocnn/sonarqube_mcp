from typing import Optional, List

def join_string_list(value: Optional[List[str]], seperator: str = ",") -> Optional[str]:
    return seperator.join(value) if value else None