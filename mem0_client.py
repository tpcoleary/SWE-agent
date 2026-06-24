"""Thin client for the local Mem0 REST API at http://localhost:8888.

Usage:
    import mem0_client as mem0
    context = mem0.search("SWE-agent repository myrepo bug fix")
    mem0.add("SWE-agent run on repository 'myrepo' succeeded.")

Environment overrides:
    MEM0_HOST      — default: http://localhost:8888
    MEM0_USER_ID   — default: tpcoleary
    MEM0_AGENT_ID  — default: swe-agent
"""
import json
import os
import urllib.request
import urllib.error


_HOST = os.environ.get("MEM0_HOST", "http://localhost:8888")
_DEFAULT_USER = os.environ.get("MEM0_USER_ID", "tpcoleary")
_DEFAULT_AGENT = os.environ.get("MEM0_AGENT_ID", "swe-agent")


def _request(endpoint, method="GET", data=None):
    url = f"{_HOST}{endpoint}"
    req = urllib.request.Request(url, method=method, headers={"Content-Type": "application/json"})
    if data is not None:
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            body = r.read().decode()
            return json.loads(body) if body else {}
    except Exception as e:
        return {"error": str(e)}


def search(query, *, user_id=_DEFAULT_USER, agent_id=_DEFAULT_AGENT, top_k=5, cross_agent=False):
    """Return relevant memory strings for the query.

    Set cross_agent=True to search across all agents (drops agent_id filter).
    """
    payload = {"query": query, "user_id": user_id, "top_k": top_k}
    if agent_id and not cross_agent:
        payload["agent_id"] = agent_id
    res = _request("/search", "POST", payload)
    results = res if isinstance(res, list) else res.get("results", [])
    return [r["memory"] for r in results if r.get("memory")]


def add(messages, *, user_id=_DEFAULT_USER, agent_id=_DEFAULT_AGENT, metadata=None):
    """Store a memory from a list of chat messages (or a plain string)."""
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    payload = {"messages": messages, "user_id": user_id, "agent_id": agent_id}
    if metadata:
        payload["metadata"] = metadata
    return _request("/memories", "POST", payload)


def healthy():
    """Return True if the local Mem0 instance is reachable."""
    return "error" not in _request("/health")
