# Social Media Assistant

A polished, responsive content studio with a dark theme that turns a topic, photo, or short video into platform-specific posts for X/Twitter, LinkedIn, and Instagram. Gemini analyzes media; each selected channel gets its own CrewAI writing agent using your chosen writer model. Optionally add a second-model editing pass. The greeting follows the visitor's device time zone.

## Run locally

Requires Python 3.10–3.13. Install the project dependencies and start the app:

```powershell
cd social-media-assistant
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

The app opens in your browser. You can enter provider keys in the main-page **AI connections** panel for the current session, or put them into `.env` for private local configuration:

```text
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_API_KEY=your-google-api-key
```

When a provider key is loaded from `.env` or the deployment environment, the app uses it on the server without displaying it in a field. Keys entered under **AI connections** are session-only and are not saved by the app. Provider API keys are issued by the providers and cannot be created by this app.

Photo and video analysis requires a Google Gemini API key, even when a different provider is selected for writing. Uploads are limited to 14 MB and are sent inline to Gemini; this app does not save uploaded media. With an upload, generated drafts show a caption and separate hashtag suggestions for each selected platform.

## Deploy publicly on Streamlit Community Cloud

1. Push this folder to a GitHub repository. Do not commit `.env` or `.streamlit/secrets.toml`.
2. Create an app at [share.streamlit.io](https://share.streamlit.io) and select this repository, branch, and `app.py` entrypoint.
3. In the deployment's **Advanced settings → Secrets**, add only the provider keys you want the app to use:

   ```toml
   OPENAI_API_KEY = "your-openai-key"
   ANTHROPIC_API_KEY = "your-anthropic-key"
   GOOGLE_API_KEY = "your-google-key"
   ```

4. Deploy the app and set its visibility to public in the app's **Settings → Sharing**.

The app reads root-level Streamlit secrets as server-side environment variables. Visitors do not see those values, but they can trigger generations using the app owner's configured provider accounts. Public use can consume your quota and incur charges, so configure provider usage limits and monitor usage before sharing the URL widely.

## Available models

- **OpenAI:** GPT-4o mini, GPT-6 Luna, GPT-6.1 Sol
- **Anthropic:** Claude Haiku 5.5, Claude Sonnet 5.5, Claude Opus 5.5
- **Google Gemini:** Gemini 3.5 Flash-Lite, Gemini 3.6 Flash, Gemini 3.8 Flash

Model availability, account access, and billing are managed by each provider. The original GPT-4o-mini choice remains the default. The optional review pass runs after the writing tasks and can use a different provider/model to refine the drafts while preserving facts and brand voice.

## Troubleshooting provider limits

If a generation is rate-limited, check the selected provider's usage and billing page from the app's error panel. A provider may limit requests per minute, or the account may have run out of quota or credits. Wait for a temporary limit to reset, disable the optional second-model review, or generate one platform at a time to reduce the number of calls. Confirm that the selected model is available to the API account. Provider response details are shown in the app with common API-key formats redacted.

## Project files

- `app.py` — Streamlit interface, provider settings, and CrewAI workflow
- `.streamlit/config.toml` — dark Streamlit theme
- `requirements.txt` — CrewAI provider integrations, Streamlit, and dotenv
- `.env.example` — blank environment-variable template
- `.gitignore` — excludes local secrets and Python environment files

The app drafts content only. It does not connect to social accounts or publish posts. Drafts can be edited in the browser and downloaded individually or as one Markdown file.
