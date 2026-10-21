from __future__ import annotations

import os
import mimetypes
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Social Media Assistant",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="collapsed",
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
MAX_MEDIA_BYTES = 14 * 1024 * 1024
MEDIA_FILE_TYPES = ["jpg", "jpeg", "png", "webp", "mp4", "mov", "webm", "avi"]

PLATFORM_LOGOS = {
    "X / Twitter": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.64 7.584H.47l8.6-9.83L0 1.153h7.594l5.243 6.932zm-1.29 19.493h2.04L6.486 3.24H4.298z"/></svg>',
    "LinkedIn": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.35V9h3.414v1.561h.049c.476-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 1 1 0-4.124 2.062 2.062 0 0 1 0 4.124zM3.56 9h3.554v11.452H3.56z"/></svg>',
    "Instagram": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.7" cy="6.5" r="1.15" fill="currentColor"/></svg>',
}
PLATFORM_COLORS = {"X / Twitter": "#f2f3f6", "LinkedIn": "#56a9ff", "Instagram": "#ff76b8"}

st.markdown(
    """
    <style>
      :root { color-scheme: dark; --ink:#f4f5f7; --muted:#9aa3b2; --line:#252b36; --panel:#11151d; --accent:#b7f36b; --accent-ink:#10150b; }
      .stApp { background: radial-gradient(ellipse at 82% 0%, rgba(105,87,223,.14), transparent 33rem), #090b10; color:var(--ink); }
      [data-testid="stHeader"] { background:transparent; }
      [data-testid="stSidebar"] { display:none; }
      [data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { display:none; }
      [data-testid="stToolbar"] { right:1rem; }
      .block-container { max-width:1120px; padding:1.35rem 2.2rem 4.5rem; }
      .brand-row { display:flex; align-items:center; justify-content:space-between; margin:.25rem 0 1rem; color:#dfe3e9; }
      .brand-name { display:flex; align-items:center; gap:.7rem; font-weight:800; letter-spacing:.08em; font-size:.78rem; }
      .brand-symbol { display:inline-flex; align-items:center; justify-content:center; width:2rem; height:2rem; border-radius:10px; color:#11150c; background:var(--accent); font-size:1.1rem; }
      .brand-meta { color:#778091; font-size:.72rem; letter-spacing:.12em; text-transform:uppercase; }
      .hero-panel { position:relative; overflow:hidden; padding:2.1rem 2.3rem 2rem; margin:.45rem 0 1.15rem; border:1px solid #2a2c40; border-radius:24px; background:linear-gradient(118deg,#151821 0%,#191827 60%,#211d36 100%); box-shadow:0 24px 65px rgba(0,0,0,.25); }
      .hero-panel:after { content:''; position:absolute; width:300px; height:300px; border-radius:50%; right:-110px; top:-205px; background:rgba(183,243,107,.12); box-shadow:-145px 245px 0 -92px rgba(119,99,235,.16); pointer-events:none; }
      .hero-eyebrow { color:var(--accent); font-size:.72rem; font-weight:760; letter-spacing:.14em; text-transform:uppercase; position:relative; z-index:1; }
      .hero-title { color:#f6f4ff; font-size:clamp(2.2rem,5vw,4rem); font-weight:790; letter-spacing:-.06em; line-height:1.02; margin:.8rem 0 .75rem; position:relative; z-index:1; }
      .hero-copy { color:#b1b4c2; font-size:1rem; max-width:620px; line-height:1.65; margin:0; position:relative; z-index:1; }
      .hero-badges { display:flex; flex-wrap:wrap; gap:.55rem; margin-top:1.35rem; position:relative; z-index:1; }
      .hero-badge { border:1px solid #343243; border-radius:999px; color:#d1d0dd; padding:.42rem .75rem; font-size:.74rem; background:rgba(255,255,255,.035); }
      .section-heading { color:#f0f1f5; font-size:1.08rem; font-weight:740; letter-spacing:-.025em; margin-bottom:.15rem; }
      .step-label { color:#8992a2; font-size:.69rem; font-weight:750; letter-spacing:.14em; text-transform:uppercase; margin:1.25rem 0 .55rem; }
      div[data-testid="stForm"] { background:rgba(17,21,29,.84); border:1px solid var(--line); padding:1.4rem 1.5rem 1.3rem; border-radius:21px; box-shadow:0 12px 35px rgba(0,0,0,.12); }
      div[data-testid="stVerticalBlockBorderWrapper"] { background:#10141c; border-color:#282e39; border-radius:17px; }
      .platform-heading { display:flex; align-items:center; gap:.75rem; padding:.35rem 0 .6rem; color:#f2f3f6; font-weight:720; }
      .platform-logo { width:2.55rem; height:2.55rem; border-radius:13px; display:inline-flex; align-items:center; justify-content:center; background:#1b202a; }
      .platform-logo svg { width:1.25rem; height:1.25rem; }
      .platform-name { font-size:.92rem; }
      div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input { border-radius:12px; background:#0d1118; border-color:#2b313c; }
      div[data-testid="stSelectbox"] > div > div { border-radius:11px; background:#0d1118; }
      div[data-testid="stCheckbox"] label p { color:#dfe2e8; font-weight:600; }
      div[data-testid="stExpander"] { border:1px solid #282e39; border-radius:15px; background:#10141c; }
      [data-testid="stFileUploaderDropzone"] { background:#0d1118; border:1px dashed #3a4250; border-radius:15px; }
      .stCaption { color:#929bab; }
      .stButton > button[kind="primary"] { background:var(--accent); color:var(--accent-ink); border:0; border-radius:12px; min-height:3.2rem; font-weight:780; box-shadow:0 8px 25px rgba(183,243,107,.12); }
      .stButton > button[kind="primary"]:hover { background:#c8ff86; border:0; color:#10150b; }
      .stDownloadButton > button { border-radius:11px; border-color:#343a46; color:#edf0f4; background:#141923; }
      [data-testid="stMetric"] { background:#11151d; border:1px solid var(--line); border-radius:14px; padding:12px 16px; }
      @media (max-width:640px) {
        .block-container { padding:.8rem .8rem 3rem; }
        .brand-row { margin:.1rem .15rem .65rem; }
        .brand-meta { display:none; }
        .hero-panel { padding:1.35rem 1.25rem 1.45rem; border-radius:19px; margin:.35rem 0 .8rem; }
        .hero-title { font-size:2.25rem; }
        .hero-copy { font-size:.91rem; }
        .hero-badges { gap:.4rem; margin-top:1rem; }
        .hero-badge { font-size:.68rem; padding:.38rem .6rem; }
        div[data-testid="stForm"] { padding:1rem .9rem; border-radius:17px; }
        div[data-testid="stHorizontalBlock"] { gap:.55rem; }
        div[data-testid="stHorizontalBlock"] { flex-direction:column !important; align-items:stretch !important; }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { width:100% !important; min-width:100% !important; flex:1 1 100% !important; }
        .platform-logo { width:2.2rem; height:2.2rem; }
        .platform-name { font-size:.82rem; }
      }
      @media (min-width:641px) and (max-width:1024px) {
        .block-container { max-width:940px; padding:1.15rem 1.45rem 3.5rem; }
        .hero-panel { padding:1.8rem 1.9rem; }
      }
      @media (min-width:1025px) and (max-width:1440px) {
        .block-container { max-width:1120px; padding-top:1.35rem; }
      }
      @media (min-width:1441px) {
        .block-container { max-width:1240px; }
      }
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
    media_context: str | None,
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
                f"Visual or video observations: {media_context or 'No media provided'}\n"
                f"Target audience: {audience or 'A broad audience interested in this topic'}\n"
                f"Objective: {objective}\n"
                f"Brand voice: {voice or 'Clear, human, and useful'}\n"
                f"Call to action: {call_to_action or 'Choose a natural CTA only if it improves the post'}\n\n"
                f"Platform guidance: {spec['guidance']}\n\n"
                "Use only facts present in the supplied topic and visual observations. Do not infer identities, locations, dates, "
                "or unsupported details from the media. Do not mention this brief or explain your choices. "
                "When visual or video observations are provided, return exactly this format:\n"
                "Caption:\n[platform-ready caption]\n\nHashtag suggestions:\n[relevant hashtags]\n"
                "Keep hashtags separate from the caption. Use at most 2 for X / Twitter, 3–5 for Instagram, and 2–4 for LinkedIn. "
                "Without media, return only the final post text."
            ),
            expected_output=(
                f"One polished {platform} post. For media-based posts, include a caption followed by separate hashtag suggestions; "
                "otherwise return the post text only."
            ),
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
                    "If the draft has Caption and Hashtag suggestions sections, preserve both headings and keep hashtags separate. "
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


def analyze_media(*, media_bytes: bytes, mime_type: str, api_key: str) -> str:
    """Create concise, factual visual notes from an image or short video using Gemini."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    prompt = (
        "Analyze this uploaded social-media asset and return concise visual notes for a caption writer. "
        "Describe the main visible subjects, setting, actions or movement, mood, colors, and any readable text. "
        "For video, summarize the meaningful moments and any clearly audible speech or sound. "
        "Do not identify people, infer a location, or invent context, dates, claims, or facts that are not clearly present. "
        "Return factual observations only, in a few short sentences."
    )
    if mime_type.startswith("video/"):
        media_part = types.Part(
            inline_data=types.Blob(data=media_bytes, mime_type=mime_type)
        )
    else:
        media_part = types.Part.from_bytes(data=media_bytes, mime_type=mime_type)

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=[prompt, media_part],
        )
    finally:
        client.close()

    analysis = (response.text or "").strip()
    if not analysis:
        raise ValueError("Gemini did not return any media observations.")
    return analysis


def export_markdown(posts: dict[str, str], topic: str) -> str:
    labels = {spec["key"]: label for label, spec in PLATFORMS.items()}
    sections = [f"# Social Media Assistant\n\n**Topic:** {topic.strip()}\n"]
    sections.extend(f"## {labels.get(key, key)}\n\n{text.strip()}\n" for key, text in posts.items())
    return "\n".join(sections)


st.markdown(
    '<div class="brand-row"><div class="brand-name"><span class="brand-symbol">✳</span> SOCIAL STUDIO</div><div class="brand-meta">CREWAI · MULTI-MODEL CONTENT</div></div>',
    unsafe_allow_html=True,
)

components.html(
    """
    <style>
      html,body{margin:0;padding:0;background:transparent;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
      .hello{height:42px;display:flex;align-items:center;justify-content:space-between;color:#f0f2f5;font-size:14px}
      .hello strong{font-size:15px;font-weight:720;letter-spacing:-.02em}
      .hello span{color:#8e98a8;font-size:12px}
      @media(max-width:520px){.hello{height:38px}.hello span{font-size:10px}.hello strong{font-size:14px}}
    </style>
    <div class="hello"><strong id="salutation">Welcome to Social Studio</strong><span id="local-time"></span></div>
    <script>
      function updateLocalGreeting(){
        const now=new Date();
        const hour=now.getHours();
        const greeting=hour>=5&&hour<12?"Good morning":hour>=12&&hour<17?"Good afternoon":hour>=17&&hour<21?"Good evening":"Good night";
        const zone=Intl.DateTimeFormat().resolvedOptions().timeZone||"your local time";
        const time=new Intl.DateTimeFormat(undefined,{hour:"numeric",minute:"2-digit"}).format(now);
        document.getElementById("salutation").textContent=greeting;
        document.getElementById("local-time").textContent=`${time} · ${zone}`;
      }
      updateLocalGreeting();
      setInterval(updateLocalGreeting,60000);
    </script>
    """,
    height=46,
    scrolling=False,
)

st.markdown(
    """
    <div class="hero-panel">
      <div class="hero-eyebrow">Your social content, in sync</div>
      <div class="hero-title">One idea.<br>Three native posts.</div>
      <p class="hero-copy">Shape one clear message into content that feels at home on every platform. Set your voice, choose your AI team, and make every post count.</p>
      <div class="hero-badges"><span class="hero-badge">X / Twitter</span><span class="hero-badge">LinkedIn</span><span class="hero-badge">Instagram</span><span class="hero-badge">CrewAI agents</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

server_api_keys = {
    config["env_key"]: os.getenv(config["env_key"], "").strip()
    for config in PROVIDERS.values()
}
api_keys: dict[str, str] = dict(server_api_keys)
server_provider_count = sum(bool(value) for value in server_api_keys.values())

with st.expander(
    f"AI connections · {server_provider_count}/3 server keys",
    expanded=server_provider_count == 0,
):
    st.caption("Deployment keys are used on the server and never shown here. Keys entered below are session-only and are not saved by this app.")
    for provider, config in PROVIDERS.items():
        env_key = config["env_key"]
        if server_api_keys[env_key]:
            st.markdown(f"**{provider}** · connected securely")
        else:
            api_keys[env_key] = st.text_input(
                f"{provider} API key",
                type="password",
                placeholder="Paste your key for this session",
                key=f"provider_key_{provider}",
            ).strip()
        st.link_button(f"Get {provider} key ↗", config["key_url"])
    if server_provider_count:
        st.caption("Generations using app-managed keys count toward the app owner's provider usage.")

with st.container(border=True):
    upload_left, upload_right = st.columns([1.35, 1])
    with upload_left:
        st.markdown("### Add a photo or video")
        st.caption("Get a visual read, then turn it into a caption and hashtag ideas.")
        uploaded_media = st.file_uploader(
            "Choose an image or short video",
            type=MEDIA_FILE_TYPES,
            key="social_media_upload",
            help="Images and short clips up to 14 MB. Supported: JPG, PNG, WebP, MP4, MOV, WebM, AVI.",
        )
    with upload_right:
        st.markdown("**Visual-first writing**")
        st.caption("Gemini analyzes the media. Your selected writing model creates each platform caption and separates hashtag suggestions.")
        st.caption("Media is sent to Google Gemini for analysis and is not saved by this app.")

media_bytes = uploaded_media.getvalue() if uploaded_media else None
media_mime_type = (
    mimetypes.guess_type(uploaded_media.name)[0] or uploaded_media.type or ""
    if uploaded_media
    else ""
)
media_is_valid = True
if uploaded_media:
    if len(media_bytes) > MAX_MEDIA_BYTES:
        media_is_valid = False
        st.error("This file is larger than 14 MB. Choose a smaller image or compress the video and try again.")
    elif media_mime_type.startswith("image/"):
        st.image(media_bytes, caption=uploaded_media.name, use_container_width=True)
    elif media_mime_type.startswith("video/"):
        st.video(media_bytes, format=media_mime_type)
        st.caption(uploaded_media.name)
    else:
        media_is_valid = False
        st.error("That file type could not be read as an image or video. Try JPG, PNG, WebP, MP4, MOV, WebM, or AVI.")

with st.form("content_brief", clear_on_submit=False):
    st.markdown("### Create your next post")
    st.caption("Add a topic, or let your uploaded media lead the way. Your AI team adapts the result for each channel.")
    topic = st.text_area(
        "Topic or source material",
        placeholder="Optional with a photo/video. Add a launch, idea, product, point of view, or a few notes…",
        height=125,
    )

    st.markdown('<div class="step-label">01 · Choose your channels</div>', unsafe_allow_html=True)
    channel_cols = st.columns(3)
    selected_platforms: list[str] = []
    for col, platform in zip(channel_cols, PLATFORMS):
        with col:
            with st.container(border=True):
                st.markdown(
                    f'<div class="platform-heading"><span class="platform-logo" style="color:{PLATFORM_COLORS[platform]}">{PLATFORM_LOGOS[platform]}</span><span class="platform-name">{platform}</span></div>',
                    unsafe_allow_html=True,
                )
                if st.checkbox("Create a post", value=True, key=f"platform_{PLATFORMS[platform]['key']}"):
                    selected_platforms.append(platform)

    st.markdown('<div class="step-label">02 · Make it yours</div>', unsafe_allow_html=True)
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

    st.markdown('<div class="step-label">03 · Choose your AI team</div>', unsafe_allow_html=True)
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
            st.caption("Add an editor to tighten the drafts while preserving your facts and voice.")

    submitted = st.form_submit_button("✳  Create platform-ready posts", type="primary", use_container_width=True)

if submitted:
    if not topic.strip() and not uploaded_media:
        st.error("Add a short topic or upload a photo or video to get started.")
    elif not selected_platforms:
        st.error("Choose at least one platform.")
    elif uploaded_media and not media_is_valid:
        st.error("Choose a supported image or video under 14 MB before creating posts.")
    else:
        required_models = [writer_model_name]
        if reviewer_model_name:
            required_models.append(reviewer_model_name)
        missing_providers = {
                MODEL_OPTIONS[name]["provider"]
                for name in required_models
                if not api_keys.get(PROVIDERS[MODEL_OPTIONS[name]["provider"]]["env_key"])
        }
        if uploaded_media and not api_keys.get(PROVIDERS["Google Gemini"]["env_key"]):
            missing_providers.add("Google Gemini (media analysis)")
        missing_providers = sorted(missing_providers)
        if missing_providers:
            st.error("Add a key for " + ", ".join(missing_providers) + " under AI connections to use the selected model(s) and media analysis.")
        else:
            try:
                media_context = None
                if media_bytes:
                    with st.spinner("Gemini is reading your photo or video…"):
                        media_context = analyze_media(
                            media_bytes=media_bytes,
                            mime_type=media_mime_type,
                            api_key=api_keys[PROVIDERS["Google Gemini"]["env_key"]],
                        )
                with st.spinner("Your platform writers are drafting…" if not review_enabled else "Writers are drafting; your editor is reviewing…"):
                    generated = create_posts(
                        topic=topic,
                        platforms=selected_platforms,
                        audience=audience,
                        objective=objective,
                        voice=voice,
                        call_to_action=call_to_action,
                        media_context=media_context,
                        api_keys=api_keys,
                        writer_model_name=writer_model_name,
                        reviewer_model_name=reviewer_model_name,
                    )
                st.session_state["generated_posts"] = generated
                st.session_state["generated_topic"] = topic.strip()
                st.session_state["generated_at"] = datetime.now().strftime("%b %d, %Y · %I:%M %p")
                st.session_state["generated_model"] = writer_model_name
                st.session_state["review_model"] = reviewer_model_name
                st.session_state["media_context"] = media_context
                st.session_state["media_name"] = uploaded_media.name if uploaded_media else None
                for key, post in generated.items():
                    st.session_state[f"draft_{key}"] = post
            except Exception as exc:
                st.error("The content crew could not finish this run.")
                st.caption(f"{type(exc).__name__}: check the selected provider key, model access, quota, and connection.")

posts = st.session_state.get("generated_posts", {})
if posts:
    st.markdown('<div class="step-label">Your workspace</div>', unsafe_allow_html=True)
    if st.session_state.get("media_context"):
        with st.expander(f"What Gemini noticed · {st.session_state.get('media_name', 'uploaded media')}"):
            st.write(st.session_state["media_context"])
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
    labels = {spec["key"]: label for label, spec in PLATFORMS.items()}
    for index, (key, content) in enumerate(posts.items()):
        label = labels.get(key, key.title())
        with result_cols[index % len(result_cols)]:
            with st.container(border=True):
                logo = PLATFORM_LOGOS.get(label, "✳")
                color = PLATFORM_COLORS.get(label, "#b7f36b")
                st.markdown(
                    f'<div class="platform-heading"><span class="platform-logo" style="color:{color}">{logo}</span><span class="platform-name">{label}</span></div>',
                    unsafe_allow_html=True,
                )
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

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
with st.expander("How your content is created"):
    st.markdown(
        "The app creates one CrewAI agent and task for each selected platform. "
        "Those tasks run in a sequential crew. Choose OpenAI, Anthropic, or Google Gemini for drafting, "
        "then optionally use a different model for an editorial pass. Generated copy stays in your current browser session and can be edited or downloaded. "
        "Nothing is published to your social accounts."
    )
