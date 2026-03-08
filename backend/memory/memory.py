import redis
from typing import Dict, Any
import json
import time

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)  

class MemoryManager:
    def __init__(self):
        pass

    async def get_session(self, session_id: str) -> Dict[str, Any]:
        data = r.hgetall(f"session:{session_id}")
        return {k: json.loads(v) for k, v in data.items()} if data else {}

    async def set_session(self, session_id: str, key: str, value: Any, ttl: int = 1800):
        r.hset(f"session:{session_id}", key, json.dumps(value))
        r.expire(f"session:{session_id}", ttl)

    async def get_persistent(self, patient_id: str) -> Dict[str, Any]:
        data = r.get(f"patient:{patient_id}")
        return json.loads(data) if data else {"preferred_lang": "en", "history": []}

    async def set_persistent(self, patient_id: str, data: Dict[str, Any]):
        r.set(f"patient:{patient_id}", json.dumps(data))  

    async def get_context(self, session_id: str, patient_id: str) -> Dict[str, Any]:
        session = await self.get_session(session_id)
        persistent = await self.get_persistent(patient_id)
        context = {**session, **persistent} 
        context["history"].append({"timestamp": time.time(), "input": session.get("last_input", "")})
        await self.set_persistent(patient_id, context)  
        return context