from __future__ import annotations

import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Social Media Assistant",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="expanded",
)

PLATFORMS = {
    "X / Twitter": {
        "key": "x",
        "icon": "𝕏",
        "guidance": "Write a concise post under 280 characters. Lead with a clear hook, keep one idea, and use at most two relevant hashtags.",
    },
    "LinkedIn": {
        "key": "linkedin",
        "icon": "in",
        "guidance": "Write a thoughtful professional post with a strong opening, short readable paragraphs, and a useful takeaway. End with a natural conversation prompt when appropriate. Avoid engagement bait.",
    },
    "Instagram": {
        "key": "instagram",
        "icon": "◎",
        "guidance": "Write a warm, visual-first caption with a memorable opening, short line breaks, and a clear call to action when appropriate. Add 3–5 specific, relevant hashtags at the end.",
    },
}

PROVIDERS = {
    "OpenAI": {
        "env_key": "OPENAI_API_KEY",
        "key_url": "https://platform.openai.com/api-keys",
    },
    "Anthropic": {
        "env_key": "ANTHROPIC_API_KEY",
        "key_url": "https://console.anthropic.com/settings/keys",
    },
    "Google Gemini": {
        "env_key": "GOOGLE_API_KEY",
        "key_url": "https://aistudio.google.com/app/apikey",
    },
}

MODEL_OPTIONS = {
    "OpenAI · GPT-4o mini": {
        "model": "openai/gpt-4o-mini",
        "provider": "OpenAI",
        "about": "Fast, affordable drafting. This remains the default model from your original brief.",
    },
    "OpenAI · GPT-6 Luna": {
        "model": "openai/gpt-6-luna",
        "provider": "OpenAI",
        "about": "Efficient option for focused, high-volume content generation.",
        "reasoning_effort": "medium",
    },
    "OpenAI · GPT-6.1 Sol": {
        "model": "openai/gpt-6.1-sol",
        "provider": "OpenAI",
        "about": "Higher-capability writing for nuanced positioning and more demanding briefs.",
        "reasoning_effort": "medium",
    },
    "Anthropic · Claude Haiku 5.5": {
        "model": "anthropic/claude-haiku-5-5",
        "provider": "Anthropic",
        "about": "A fast, cost-conscious Claude option for everyday content.",
        "max_tokens": 4096,
    },
    "Anthropic · Claude Sonnet 5.5": {
        "model": "anthropic/claude-sonnet-5-5",
        "provider": "Anthropic",
        "about": "Strong balance of writing quality, speed, and cost.",
        "max_tokens": 4096,
    },
    "Anthropic · Claude Opus 5.5": {
        "model": "anthropic/claude-opus-5-5",
        "provider": "Anthropic",
        "about": "Premium choice for high-stakes brand voice and careful editorial review.",
        "max_tokens": 4096,
    },
    "Google · Gemini 3.5 Flash-Lite": {
        "model": "gemini/gemini-3.5-flash-lite",
        "provider": "Google Gemini",
        "about": "Google's fast, cost-efficient choice for short-form content.",
    },
    "Google · Gemini 3.6 Flash": {
        "model": "gemini/gemini-3.6-flash",
        "provider": "Google Gemini",
        "about": "Balanced speed and capability for everyday social content.",
    },
    "Google · Gemini 3.8 Flash": {
        "model": "gemini/gemini-3.8-flash",
        "provider": "Google Gemini",
        "about": "Latest stable Gemini Flash model, designed for capable and efficient generation.",
    },
}

DEFAULT_MODEL = "OpenAI · GPT-4o mini"

st.markdown(
    """
    <style>
      :root { --ink: #1e2030; --muted: #74788b; --line: #e7e8f0; --accent: #6957df; }
      .stApp { background: #f5f5fa; color: var(--ink); }
      [data-testid="stHeader"] { background: transparent; }
      [data-testid="stSidebar"] { background: #fff; border-right: 1px solid var(--line); }
      [data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }
      .block-container { max-width: 1240px; padding-top: 1.5rem; padding-bottom: 4.5rem; }
      .hero-panel { color: white; background: linear-gradient(118deg, #21173e 0%, #443377 56%, #765ed0 100%); border-radius: 26px; padding: 2rem 2.25rem 2.15rem; margin-bottom: 1.55rem; box-shadow: 0 18px 55px rgba(57, 43, 105, .18); position: relative; overflow: hidden; }
      .hero-panel:after { content: ''; position: absolute; width: 280px; height: 280px; border-radius: 50%; right: -75px; top: -145px; background: rgba(255,255,255,.09); box-shadow: -125px 210px 0 -75px rgba(255,255,255,.08); }
      .hero-top { display: flex; align-items: center; gap: 10px; color: rgba(255,255,255,.72); font-size: .72rem; font-weight: 750; letter-spacing: .14em; text-transform: uppercase; position: relative; z-index: 1; }
      .brand-mark { width: 27px; height: 27px; display: inline-flex; align-items: center; justify-content: center; background: rgba(255,255,255,.15); border-radius: 9px; color: white; font-size: 1rem; }
      .hero-title { color: white; font-size: clamp(2.2rem, 4.5vw, 3.65rem); font-weight: 780; letter-spacing: -.055em; line-height: 1.03; margin: 1.1rem 0 .7rem; position: relative; z-index: 1; }
      .hero-copy { color: rgba(255,255,255,.77); font-size: 1rem; max-width: 670px; line-height: 1.65; margin: 0; position: relative; z-index: 1; }
      .hero-pills { display: flex; gap: 8px; margin-top: 1.25rem; position: relative; z-index: 1; }
      .hero-pill { border: 1px solid rgba(255,255,255,.2); border-radius: 999px; color: rgba(255,255,255,.88); padding: 5px 11px; font-size: .76rem; background: rgba(255,255,255,.08); }
      .section-title { color: #242437; font-size: 1.08rem; font-weight: 730; letter-spacing: -.02em; }
      .stButton > button[kind="primary"] { background: var(--accent); border: 0; border-radius: 11px; min-height: 3.15rem; font-weight: 720; box-shadow: 0 8px 20px rgba(105,87,223,.2); }
      .stButton > button[kind="primary"]:hover { background: #5948c9; border: 0; }
      div[data-testid="stForm"] { background: #fff; border: 1px solid var(--line); padding: 1.45rem 1.5rem 1.35rem; border-radius: 20px; box-shadow: 0 7px 25px rgba(28, 30, 50, .035); }
      div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input { border-radius: 11px; background: #fcfcfe; }
      div[data-testid="stSelectbox"] > div > div { border-radius: 10px; }
      div[data-testid="stCheckbox"] label p { font-weight: 620; }
      div[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 15px; background: #fff; }
      .stCaption { color: #828598; }
      [data-testid="stMetric"] { background: white; border: 1px solid var(--line); border-radius: 14px; padding: 12px 16px; }
      .result-label { display: inline-flex; gap: 7px; align-items: center; font-size: .73rem; letter-spacing: .08em; text-transform: uppercase; color: #7d8091; font-weight: 720; }
      @media (max-width: 700px) { .hero-panel { padding: 1.5rem; border-radius: 19px; } .hero-pills { flex-wrap: wrap; } div[data-testid="stForm"] { padding: 1rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def create_posts(
    *,
    topic: str,
    platforms: list[str],
    audience: str,
    objective: str,
    voice: str,
    call_to_action: str,
    api_keys: dict[str, str],
    writer_model_name: str,
    reviewer_model_name: str | None,
) -> dict[str, str]:
    """Draft one post per platform, optionally followed by a second-model review."""
    from crewai import Agent, Crew, LLM, Process, Task

    def make_llm(model_name: str) -> LLM:
        model_config = MODEL_OPTIONS[model_name]
        provider = model_config["provider"]
        options: dict[str, object] = {
            "model": model_config["model"],
            "api_key": api_keys[PROVIDERS[provider]["env_key"]],
            "timeout": 120,
            "max_retries": 2,
        }
        if model_config.get("max_tokens"):
            options["max_tokens"] = model_config["max_tokens"]
        if model_config.get("reasoning_effort"):
            options["reasoning_effort"] = model_config["reasoning_effort"]
        return LLM(**options)

    writer_llm = make_llm(writer_model_name)
    reviewer_llm = make_llm(reviewer_model_name) if reviewer_model_name else None

    agents: list[Agent] = []
    tasks: list[Task] = []
    task_keys: list[str] = []

    for platform in platforms:
        spec = PLATFORMS[platform]
        agent = Agent(
            role=f"{platform} Content Specialist",
            goal=f"Create original, audience-aware {platform} content that earns attention and supports the user's objective.",
            backstory=(
                f"You are an experienced social media editor specializing in {platform}. "
                "You understand the platform's reading habits and write with clarity, originality, and restraint. "
                "You never invent facts, statistics, customer stories, or links."
            ),
            llm=writer_llm,
            allow_delegation=False,
            verbose=False,
        )
        write_task = Task(
            name=f"write_{spec['key']}_post",
            description=(
                f"Create one ready-to-publish {platform} post using the brief below.\n\n"
                f"Topic or source material: {topic}\n"
                f"Target audience: {audience or 'A broad audience interested in this topic'}\n"
                f"Objective: {objective}\n"
                f"Brand voice: {voice or 'Clear, human, and useful'}\n"
                f"Call to action: {call_to_action or 'Choose a natural CTA only if it improves the post'}\n\n"
                f"Platform guidance: {spec['guidance']}\n\n"
                "Use only facts present in the supplied topic. Do not mention this brief or explain your choices. "
                "Return only the final post text."
            ),
            expected_output=f"One polished {platform} post, ready to paste and publish, with no surrounding explanation.",
            agent=agent,
            markdown=False,
        )
        agents.append(agent)
        tasks.append(write_task)
        task_keys.append(spec["key"])

        if reviewer_llm:
            reviewer = Agent(
                role=f"{platform} Senior Editor",
                goal=f"Improve the {platform} draft while preserving the brief, brand voice, and factual accuracy.",
                backstory=(
                    "You are a careful social editor. You tighten wording, improve clarity, and check platform fit. "
                    "Never add a factual claim, statistic, promise, or link that was not supplied in the original brief."
                ),
                llm=reviewer_llm,
                allow_delegation=False,
                verbose=False,
            )
            review_task = Task(
                name=f"review_{spec['key']}_post",
                description=(
                    f"Edit the supplied {platform} draft for clarity, originality, platform fit, and the stated goal. "
                    "Preserve all supported facts and the chosen brand voice. Do not add claims or explain the edits. "
                    "Return only the final ready-to-publish post."
                ),
                expected_output=f"One improved {platform} post, ready to publish, with no surrounding explanation.",
                agent=reviewer,
                context=[write_task],
                markdown=False,
            )
            agents.append(reviewer)
            tasks.append(review_task)
            task_keys.append(spec["key"])

    result = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=False,
        share_crew=False,
    ).kickoff()

    posts: dict[str, str] = {}
    task_outputs = getattr(result, "tasks_output", []) or []
    for key, task_output in zip(task_keys, task_outputs):
        text = str(getattr(task_output, "raw", task_output)).strip()
        if text.startswith("```") and text.endswith("```"):
            text = text.strip("`").split("\n", 1)[-1].strip()
        posts[key] = text

    if not posts and task_keys:
        posts[task_keys[-1]] = str(getattr(result, "raw", result)).strip()
    return posts


def export_markdown(posts: dict[str, str], topic: str) -> str:
    labels = {spec["key"]: label for label, spec in PLATFORMS.items()}
    sections = [f"# Social Media Assistant\n\n**Topic:** {topic.strip()}\n"]
    sections.extend(f"## {labels.get(key, key)}\n\n{text.strip()}\n" for key, text in posts.items())
    return "\n".join(sections)


with st.sidebar:
    st.markdown("### ✳  Social Studio")
    st.caption("A CrewAI-powered content workspace")
    st.divider()
    st.markdown("#### Model providers")
    st.caption("Deployment keys stay on the server. You can also enter your own key for this session.")
    api_keys: dict[str, str] = {}
    for provider, config in PROVIDERS.items():
        env_key = config["env_key"]
        saved_value = os.getenv(env_key, "")
        if saved_value:
            api_keys[env_key] = saved_value
            st.markdown(f"**{provider}** · ready")
            st.caption("Configured privately by the app owner")
        else:
            api_keys[env_key] = st.text_input(
                f"{provider} API key",
                type="password",
                placeholder="Paste your key for this session",
                key=f"provider_key_{provider}",
            ).strip()
        st.link_button(f"Get {provider} key ↗", config["key_url"], use_container_width=True)

    configured_count = sum(bool(api_keys[config["env_key"]]) for config in PROVIDERS.values())
    st.caption(f"{configured_count} of 3 providers ready in this session")
    st.caption("Keys entered here are used for this session and are never saved by the app.")
    if any(os.getenv(config["env_key"], "") for config in PROVIDERS.values()):
        st.caption("Generations use the app owner's provider quota and may incur charges.")
    st.divider()
    st.markdown("#### Your crew")
    st.markdown("**01**  Platform writers\n\n**02**  Optional AI editor\n\n**03**  CrewAI workflow")
    st.caption("Draft only. Nothing is published to your social accounts.")

st.markdown(
    """
    <div class="hero-panel">
      <div class="hero-top"><span class="brand-mark">✳</span> SOCIAL MEDIA ASSISTANT <span style="margin-left:auto">MULTI-MODEL STUDIO</span></div>
      <div class="hero-title">Show up everywhere.<br>Still sound like you.</div>
      <p class="hero-copy">Turn one clear brief into platform-native content. Choose a writing model, shape the brand voice, and add a second model when you want an editorial pass.</p>
      <div class="hero-pills"><span class="hero-pill">X / Twitter</span><span class="hero-pill">LinkedIn</span><span class="hero-pill">Instagram</span><span class="hero-pill">CrewAI agents</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("content_brief", clear_on_submit=False):
    st.markdown("### Build your next post")
    st.caption("Start with the message. Your AI team will adapt it for each channel.")
    topic = st.text_area(
        "Topic or source material",
        placeholder="What's the story? Share a launch, idea, product, point of view, or a few notes…",
        height=120,
    )

    st.markdown("#### Choose your channels")
    channel_cols = st.columns(3)
    selected_platforms: list[str] = []
    for col, platform in zip(channel_cols, PLATFORMS):
        with col:
            if st.checkbox(platform, value=True, key=f"platform_{PLATFORMS[platform]['key']}"):
                selected_platforms.append(platform)

    st.markdown("#### Make it yours")
    details_left, details_right = st.columns(2)
    with details_left:
        audience = st.text_input("Who are you speaking to?", placeholder="e.g. first-time founders")
        voice = st.text_input("Brand voice", placeholder="e.g. optimistic, practical, a little playful")
    with details_right:
        objective = st.selectbox(
            "What should this post do?",
            ["Build awareness", "Educate", "Start a conversation", "Drive sign-ups", "Promote a launch", "Share a point of view"],
        )
        call_to_action = st.text_input("Call to action (optional)", placeholder="e.g. Join the waitlist")

    st.markdown("#### Choose your AI team")
    model_col, review_col = st.columns(2)
    with model_col:
        writer_model_name = st.selectbox("Writing model", list(MODEL_OPTIONS), index=list(MODEL_OPTIONS).index(DEFAULT_MODEL))
        st.caption(MODEL_OPTIONS[writer_model_name]["about"])
    with review_col:
        review_enabled = st.checkbox("Add a second-model quality pass", value=False)
        reviewer_model_name = None
        if review_enabled:
            reviewer_default = "OpenAI · GPT-6.1 Sol"
            reviewer_model_name = st.selectbox(
                "Review with",
                list(MODEL_OPTIONS),
                index=list(MODEL_OPTIONS).index(reviewer_default),
            )
        else:
            st.caption("A second model can tighten the drafts while preserving your facts and voice.")

    submitted = st.form_submit_button("✳  Create platform-ready posts", type="primary", use_container_width=True)

if submitted:
    if not topic.strip():
        st.error("Add a topic or a short brief to get started.")
    elif not selected_platforms:
        st.error("Choose at least one platform.")
    else:
        required_models = [writer_model_name]
        if reviewer_model_name:
            required_models.append(reviewer_model_name)
        missing_providers = sorted(
            {
                MODEL_OPTIONS[name]["provider"]
                for name in required_models
                if not api_keys.get(PROVIDERS[MODEL_OPTIONS[name]["provider"]]["env_key"])
            }
        )
        if missing_providers:
            st.error("Add a key for " + ", ".join(missing_providers) + " in the sidebar to use the selected model(s).")
        else:
            try:
                with st.spinner("Your platform writers are drafting…" if not review_enabled else "Writers are drafting; your editor is reviewing…"):
                    generated = create_posts(
                        topic=topic,
                        platforms=selected_platforms,
                        audience=audience,
                        objective=objective,
                        voice=voice,
                        call_to_action=call_to_action,
                        api_keys=api_keys,
                        writer_model_name=writer_model_name,
                        reviewer_model_name=reviewer_model_name,
                    )
                st.session_state["generated_posts"] = generated
                st.session_state["generated_topic"] = topic.strip()
                st.session_state["generated_at"] = datetime.now().strftime("%b %d, %Y · %I:%M %p")
                st.session_state["generated_model"] = writer_model_name
                st.session_state["review_model"] = reviewer_model_name
                for key, post in generated.items():
                    st.session_state[f"draft_{key}"] = post
            except Exception as exc:
                st.error("The content crew could not finish this run.")
                st.caption(f"{type(exc).__name__}: check the selected provider key, model access, quota, and connection.")

posts = st.session_state.get("generated_posts", {})
if posts:
    st.divider()
    edited_posts = {
        key: st.session_state.get(f"draft_{key}", content)
        for key, content in posts.items()
    }
    result_head, result_action = st.columns([3, 1])
    with result_head:
        st.markdown("### Your drafts")
        model_used = st.session_state.get("generated_model", DEFAULT_MODEL)
        review_used = st.session_state.get("review_model")
        review_note = f" · Reviewed by {review_used}" if review_used else ""
        st.caption(f"{model_used}{review_note} · {st.session_state.get('generated_at', '')} · Review before publishing")
    with result_action:
        st.download_button(
            "↓  Download all",
            data=export_markdown(edited_posts, st.session_state.get("generated_topic", "")),
            file_name="social-media-drafts.md",
            mime="text/markdown",
            use_container_width=True,
        )

    result_cols = st.columns(min(len(posts), 3))
    labels = {spec["key"]: (label, spec["icon"]) for label, spec in PLATFORMS.items()}
    for index, (key, content) in enumerate(posts.items()):
        label, icon = labels.get(key, (key.title(), "✳"))
        with result_cols[index % len(result_cols)]:
            with st.container(border=True):
                st.markdown(f"**{icon}  {label}**")
                edited_content = st.text_area(
                    f"{label} draft",
                    value=content,
                    height=250,
                    key=f"draft_{key}",
                    label_visibility="collapsed",
                )
                st.download_button(
                    f"↓  Download {label}",
                    data=edited_content,
                    file_name=f"{key}-post.txt",
                    mime="text/plain",
                    key=f"download_{key}",
                    use_container_width=True,
                )

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
with st.expander("How this project works"):
    st.markdown(
        "The app creates one CrewAI agent and task for each selected platform. "
        "Those tasks run in a sequential crew. Choose OpenAI, Anthropic, or Google Gemini for drafting, "
        "then optionally use a different model for an editorial pass. Generated copy stays in your current browser session and can be edited or downloaded."
    )
