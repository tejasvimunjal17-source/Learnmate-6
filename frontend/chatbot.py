"""
frontend/chatbot.py
----------------------
Floating "AI Mentor" chat assistant, rendered in the bottom-right corner on
every page (minimize/maximize, welcome message, suggested questions, chat
history, responsive).

This is a fully local, rule-based mentor grounded in the student's own
roadmap/profile session data. No external services, no components.html(),
no iframes — everything renders with native Streamlit widgets.
"""

from __future__ import annotations

import streamlit as st

SUGGESTED_QUESTIONS = [
    "What should I focus on this week?",
    "How do I close my biggest skill gap?",
    "Recommend a certification for my domain.",
    "How many hours until I finish my roadmap?",
]


def _no_roadmap_message() -> str:
    return (
        "I don't see a roadmap yet — head to **AI Roadmap** and fill out your "
        "profile first, then I can give you specific guidance!"
    )


def _reply_focus(roadmap: dict) -> str:
    milestones = roadmap.get("weekly_milestones", [])
    completed = st.session_state.get("completed_weeks", set())
    next_week = next((m for m in milestones if m.get("week") not in completed), None)
    if next_week:
        return f"Right now, focus on **Week {next_week.get('week')}: {next_week.get('title')}**."
    return "Looks like you've completed every milestone — great work! Consider a capstone project next."


def _reply_skill_gap(roadmap: dict) -> str:
    gaps = roadmap.get("skill_gap_analysis", [])
    high = [g for g in gaps if g.get("priority") == "High"]
    if high:
        names = ", ".join(g.get("skill", "") for g in high[:3])
        return f"Your highest-priority skill gaps are: **{names}**. Tackle those first."
    return "No high-priority gaps detected — you're in good shape!"


def _reply_certifications(profile) -> str:
    return (
        f"Check the **Courses & Certs** page for certifications curated for "
        f"**{profile.preferred_domain}**, with official links."
    )


def _reply_hours(roadmap: dict, profile) -> str:
    total_weeks = roadmap.get("estimated_duration_weeks", len(roadmap.get("weekly_milestones", [])))
    hours = total_weeks * profile.study_hours_per_week
    return (
        f"At {profile.study_hours_per_week} hrs/week, your roadmap totals about "
        f"**{hours} hours** over {total_weeks} weeks."
    )


def _reply_progress(roadmap: dict) -> str:
    milestones = roadmap.get("weekly_milestones", [])
    completed = st.session_state.get("completed_weeks", set())
    total = len(milestones)
    done = len(completed)
    if total == 0:
        return "I don't see any milestones logged yet — check your **AI Roadmap** page."
    pct = round((done / total) * 100)
    return f"You've completed **{done} of {total}** milestones (**{pct}%**). Keep the momentum going!"

def _reply_milestone(roadmap: dict) -> str:
    milestones = roadmap.get("weekly_milestones", [])
    if not milestones:
        return "I don't see any milestones on your roadmap yet."
    completed = st.session_state.get("completed_weeks", set())
    next_week = next((m for m in milestones if m.get("week") not in completed), None)
    if next_week:
        return (
            f"Your next milestone is **Week {next_week.get('week')}: {next_week.get('title')}**. "
            f"{next_week.get('description', '')}".strip()
        )
    return "All milestones are complete! Time to plan what comes after your roadmap."


def _reply_projects(profile) -> str:
    return (
        f"For **{profile.preferred_domain}**, try building 2-3 small portfolio projects that "
        "each demonstrate one skill from your gap list — a finished project beats a tutorial "
        "every time. Check the **Courses & Certs** page for project-style learning resources."
    )


def _reply_interview(profile) -> str:
    return (
        f"For interview prep in **{profile.preferred_domain}**: review your skill gaps first "
        "(those are the likely weak spots), practice explaining your projects out loud, and "
        "do a few timed mock questions. Consistency beats cramming — a little each day."
    )


def _reply_motivation(profile) -> str:
    return (
        f"You're working toward **{profile.career_goal}** — that's a real goal, not a wish. "
        "Progress on a roadmap is rarely a straight line, so don't judge today by how you feel; "
        "judge it by whether you showed up. One milestone at a time gets you there."
    )


def _reply_greeting() -> str:
    return (
        "I'm your AI Career Mentor! Ask me about your weekly focus, skill gaps, "
        "certifications, progress, remaining hours, project ideas, interview prep, "
        "or just say hi if you need a motivation boost."
    )


def _rule_based_reply(question: str) -> str:
    q = question.lower()
    roadmap = st.session_state.get("roadmap")
    profile = st.session_state.get("profile")

    if not roadmap or not profile:
        return _no_roadmap_message()

    if "motivat" in q or "discourag" in q or "stuck" in q or "give up" in q:
        return _reply_motivation(profile)

    if "interview" in q:
        return _reply_interview(profile)

    if "project" in q and "roadmap" not in q:
        return _reply_projects(profile)

    if "milestone" in q:
        return _reply_milestone(roadmap)

    if "progress" in q or "how am i doing" in q or "how far" in q:
        return _reply_progress(roadmap)

    if "week" in q or "focus" in q or "study" in q:
        return _reply_focus(roadmap)

    if "gap" in q or "skill" in q:
        return _reply_skill_gap(roadmap)

    if "cert" in q:
        return _reply_certifications(profile)

    if "hour" in q or "time" in q or "finish" in q or "remaining" in q:
        return _reply_hours(roadmap, profile)

    return _reply_greeting()


def _render_demo_chatbot() -> None:
    """Rule-based mentor grounded in the student's own roadmap/profile data."""
    if not st.session_state["chat_history"]:
        st.info("👋 Hi! I'm your AI Career Mentor. Ask me anything about your roadmap.")

    st.markdown("**Suggested questions:**")
    for i, sq in enumerate(SUGGESTED_QUESTIONS):
        if st.button(sq, key=f"suggest_q_{i}", use_container_width=True):
            reply = _rule_based_reply(sq)
            st.session_state["chat_history"].append((sq, reply))
            st.rerun()

    for q, a in st.session_state["chat_history"][-6:]:
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Mentor:** {a}")

    user_q = st.text_input("Type a question...", key="chat_input")
    if st.button("Send", key="chat_send_btn") and user_q.strip():
        reply = _rule_based_reply(user_q)
        st.session_state["chat_history"].append((user_q, reply))
        st.rerun()


def render_chatbot_widget() -> None:
    st.session_state.setdefault("chatbot_open", False)
    st.session_state.setdefault("chat_history", [])

    # Floating launcher + panel, pinned bottom-right via the "lm_chatbot"
    # container key (Streamlit auto-assigns a `.st-key-lm_chatbot` class,
    # which frontend/styles.py targets with position:fixed). z-index and a
    # bottom-margin keep it from ever overlapping the main UI.
    with st.container(key="lm_chatbot"):
        toggle_label = "✖️ Close AI Mentor" if st.session_state["chatbot_open"] else "💬 AI Mentor"
        if st.button(toggle_label, key="chat_toggle_btn"):
            st.session_state["chatbot_open"] = not st.session_state["chatbot_open"]
            st.rerun()

        if st.session_state["chatbot_open"]:
            st.markdown("#### 🧭 AI Career Mentor")
            st.caption("🟡 Demo mentor — grounded in your own roadmap data")
            _render_demo_chatbot()