import json
from difflib import get_close_matches
from pydantic import BaseModel

FUZZY_CUTOFF = 0.6

class TechnologyInfo(BaseModel):
    name: str
    category: str
    description: str
    architecture_role: str
    documentation_url: str
    related: list[str] | None = None

def _load_knowledge(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def explain_technology(name: str, path: str) -> TechnologyInfo:
    db = _load_knowledge(path)
    matches = get_close_matches(name.lower(), db.keys(), n=1, cutoff=FUZZY_CUTOFF)
    entry = db[matches[0]] if matches else None
    
    if entry:
        return TechnologyInfo(name=name, **entry)
    
    return TechnologyInfo(
        name=name,
        category="unknown",
        description="Not found in common technologies",
        architecture_role="unknown",
        documentation_url="unknown"
    )
        
        