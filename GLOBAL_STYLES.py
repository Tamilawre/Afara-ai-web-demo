GLOBAL_STYLES = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        #MainMenu, footer, header[data-testid="stHeader"] {
            visibility: hidden;
            height: 0;
        }

        .stApp {
            background: radial-gradient(circle at 50% 0%, #f3f9f4 0%, #eef2ee 45%, #e9edf0 100%);
        }

        .block-container {
            max-width: 480px;
            padding-top: 2rem;
            padding-bottom: 6rem; /* room so content doesn't sit behind the fixed nav */
            padding-left: 1.25rem;
            padding-right: 1.25rem;
            margin: 0 auto;
        }

        .afara-header { text-align: center; margin-bottom: 0.2rem; }
        .afara-logo {
            font-family: 'Poppins', sans-serif;
            font-weight: 700 !important;
            font-size: 2.1rem !important;
            letter-spacing: -0.02em;
            background: linear-gradient(120deg, #1b5e20, #43a047 60%, #7cb342);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0 !important;
        }
        .afara-tagline {
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            color: #8a938a !important;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-top: 0.1rem !important;
        }
        .afara-pill { display: flex; justify-content: center; margin: 1.8rem auto 0.5rem auto; }
        .afara-pill span {
            background: #ffffff;
            border: 1px solid #e2e8e2;
            color: #2e7d32;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            padding: 0.4rem 1.1rem;
            border-radius: 999px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }

        .transcript-box {
            margin-top: 1.6rem;
            padding: 1.3rem 1.4rem;
            border-radius: 16px;
            background-color: #ffffff;
            border: 1px solid #e2e8e2;
            box-shadow: 0 4px 16px rgba(0,0,0,0.05);
            text-align: left;
            width: 100%;
            animation: fadeIn 0.35s ease-in-out;
        }
        .transcript-label {
            font-size: 0.75rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #43a047 !important;
            margin-bottom: 0.4rem !important;
        }
        .transcript-text { font-size: 1.1rem !important; color: #2b2b2b !important; line-height: 1.55 !important; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        .coming-soon {
            margin-top: 3rem;
            text-align: center;
            color: #8a938a;
        }
        .coming-soon .material-symbols-outlined {
            font-size: 2.5rem;
            color: #a9d5ab;
        }
        .coming-soon p {
            font-size: 1rem !important;
        }

        /* Hide the hidden bridge textarea used to pass audio data from JS to Python */
        div[data-testid="stTextArea"] {
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
        textarea[aria-label="afara_audio_payload"] {
            position: absolute !important;
            width: 1px !important;
            height: 1px !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* ── Translation result modal ──────────────────────────────── */
        div[data-testid="stDialog"] div[data-testid="stVerticalBlock"] {
            max-height: 55vh;
            overflow-y: auto;
        }

        /* ── Bottom nav bar ─────────────────────────────────────────── */
        .st-key-bottom_nav {
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            max-width: 480px;
            margin: 0 auto;
            background: #ffffff;
            border-top: 1px solid #e2e8e2;
            box-shadow: 0 -4px 16px rgba(0,0,0,0.06);
            padding: 0.6rem 0.8rem calc(0.6rem + env(safe-area-inset-bottom, 0px)) 0.8rem;
            z-index: 999;
        }
        .st-key-bottom_nav div[data-testid="stButton"] { display: flex; }
        .st-key-bottom_nav div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            gap: 0.4rem !important;
        }
        .st-key-bottom_nav div[data-testid="stColumn"] {
            width: auto !important;
            min-width: 0 !important;
            flex: 1 1 0 !important;
        }
        .st-key-bottom_nav button {
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            min-height: 48px !important; /* comfortable tap target on mobile */
        }
        .st-key-bottom_nav button p {
            font-size: 0.78rem !important;
            font-weight: 600 !important;
        }
        /* active tab */
        .st-key-bottom_nav div[data-testid="stButton"] button[kind="primary"] {
            background: #eaf4ea !important;
            color: #2e7d32 !important;
        }
        /* inactive tab */
        .st-key-bottom_nav div[data-testid="stButton"] button[kind="secondary"] {
            color: #9aa39a !important;
        }

        @media (max-width: 480px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1.2rem; }
            .afara-logo { font-size: 1.85rem !important; }
            .transcript-box { padding: 1rem 1.1rem; }
        }
    </style>
    """