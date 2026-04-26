"""
app/agents — Agentic automation pipeline (Issue #4)

Components:
    graph.py        LangGraph state machine orchestrating the full pipeline
    pose_index.py   LlamaIndex semantic index over the poses table
    crew.py         CrewAI Analyst + Matcher + Writer agents
    geofence.py     Geofencing / Geo-conquesting proximity triggers
"""
