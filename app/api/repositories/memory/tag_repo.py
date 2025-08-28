from dataclasses import dataclass

@dataclass
class Tag:
    id: int
    user_id: int
    name: str

_tags: dict[int, Tag] = {}
_next_id = 1

def reset():
    global _tags, _next_id
    _tags = {}
    _next_id = 1

def list_by_user(user_id: int) -> list[Tag]:
    return [t for t in _tags.values() if t.user_id == user_id]

def create(user_id: int, name: str) -> Tag:
    global _next_id
    tag = Tag(id=_next_id, user_id=user_id, name=name)
    _tags[_next_id] = tag
    _next_id += 1
    return tag

def delete(user_id: int, tag_id: int) -> bool:
    t = _tags.get(tag_id)
    if t and t.user_id == user_id:
        del _tags[tag_id]
        return True
    return False
