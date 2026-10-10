import streamlit as st
import sqlite3
import hashlib
import urllib.parse
import html
from datetime import datetime

# RAABTA — screen-matched interactive demo
# Run: python -m streamlit run raabta_demo.py

st.set_page_config(page_title="RAABTA | Safer. Stronger. Together.", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

DB_PATH = "raabta_users.db"
DEFAULT_MESSAGE = "I need your help. I am in a situation where I cannot text or call back. Please contact me or send help."

THEMES = {
    "Female": {"accent": "#ff2d78", "accent2": "#ff5ba5", "glow": "rgba(255,45,120,.35)", "panel": "#0b2033", "label": "FEMALE SAFETY MODE"},
    "Male": {"accent": "#1687ff", "accent2": "#22d8f0", "glow": "rgba(22,135,255,.35)", "panel": "#0b2033", "label": "PERSONAL SAFETY MODE"},
    "Transgender": {"accent": "#a855f7", "accent2": "#ff5bd6", "glow": "rgba(168,85,247,.35)", "panel": "#0b2033", "label": "PERSONAL SAFETY MODE"},
}
BASE = {"accent": "#ff2d78", "accent2": "#21d8c7", "glow": "rgba(255,45,120,.35)", "panel": "#0b2033", "label": "SAFETY SETUP"}

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY, name TEXT NOT NULL, phone TEXT NOT NULL, address TEXT,
            gender TEXT NOT NULL, blood_group TEXT, allergies TEXT, emergency_name TEXT,
            emergency_phone TEXT, emergency_relation TEXT, sos_message TEXT,
            password_hash TEXT, updated_at TEXT)""")

def save_user(d):
    pw_hash = hashlib.sha256(d.get("password", "").encode()).hexdigest() if d.get("password") else ""
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""INSERT INTO users
        (email,name,phone,address,gender,blood_group,allergies,emergency_name,emergency_phone,emergency_relation,sos_message,password_hash,updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(email) DO UPDATE SET name=excluded.name,phone=excluded.phone,address=excluded.address,
        gender=excluded.gender,blood_group=excluded.blood_group,allergies=excluded.allergies,
        emergency_name=excluded.emergency_name,emergency_phone=excluded.emergency_phone,
        emergency_relation=excluded.emergency_relation,sos_message=excluded.sos_message,
        password_hash=CASE WHEN excluded.password_hash='' THEN users.password_hash ELSE excluded.password_hash END,
        updated_at=excluded.updated_at""",
        (d["email"].strip().lower(),d["name"].strip(),d["phone"].strip(),d.get("address","").strip(),
         d["gender"],d.get("blood_group","Not specified"),d.get("allergies","").strip(),
         d.get("emergency_name","").strip(),d.get("emergency_phone","").strip(),
         d.get("emergency_relation","").strip(),d.get("sos_message",DEFAULT_MESSAGE).strip(),
         pw_hash,datetime.now().isoformat(timespec="seconds")))

def load_user(email):
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        row = con.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
        return dict(row) if row else None

init_db()

defaults = {
    "screen":"welcome", "profile":{"name":"","phone":"","email":"","address":"","gender":"Female",
    "blood_group":"Not specified","allergies":"","emergency_name":"","emergency_phone":"",
    "emergency_relation":"","sos_message":DEFAULT_MESSAGE,"password":""},
    "logged_in":False, "rating":0, "features":[], "feedback":"", "sos_active":False,
    "alarm_on":False, "battery_demo":100, "demo_alert":"", "history":[], "nav":"Home"
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v.copy() if isinstance(v, dict) else v

p = st.session_state.profile
theme = THEMES.get(p.get("gender","Female"), THEMES["Female"]) if st.session_state.screen in ("home","sos","loud_help","battery","review","trusted","profile_view") else BASE
A, A2, G, PANEL = theme["accent"], theme["accent2"], theme["glow"], theme["panel"]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
:root{{--a:{A};--a2:{A2};--panel:{PANEL};}}
.stApp{{background:radial-gradient(ellipse at 50% -10%,#12314a 0%,#061524 42%,#020914 100%);color:#eef7ff;font-family:Inter,Arial,sans-serif;}}
[data-testid="stHeader"]{{background:transparent;}}
[data-testid="stToolbar"]{{right:1rem;}}
.block-container{{max-width:1100px;padding-top:1.1rem;padding-bottom:3.4rem;}}
h1,h2,h3,h4,p,span,label,div{{font-family:Inter,Arial,sans-serif;}}
h1,h2,h3,h4,p,label{{color:#eef7ff;}}
.brand{{display:flex;align-items:center;gap:12px;border-bottom:1px solid #173950;padding:6px 0 17px;margin-bottom:20px;}}
.brand-shield{{width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,#0fddce22,#ff2d7822);border:1px solid #25cfc877;display:flex;align-items:center;justify-content:center;font-size:23px;box-shadow:0 0 24px #20d8c622;}}
.brand-name{{font-size:20px;font-weight:900;letter-spacing:5px;color:#fff;line-height:1.1;}}
.brand-tag{{font-size:10px;letter-spacing:1.6px;color:#8ca9bf;margin-top:5px;}}
.top-status{{margin-left:auto;font-size:10px;letter-spacing:1.5px;color:#28dfc9;border:1px solid #1b766e;border-radius:30px;padding:9px 13px;background:#092a31;}}
.eyebrow{{font-size:10px;letter-spacing:2.2px;color:#2be1cf;font-weight:800;text-transform:uppercase;}}
.hero-title{{font-size:clamp(30px,5vw,53px);font-weight:900;letter-spacing:-1.6px;line-height:1.08;margin:9px 0 10px;color:#fff;}}
.subtle{{color:#8da8be;font-size:13px;line-height:1.65;}}
.panel{{background:linear-gradient(145deg,#0b2033,#071827);border:1px solid #183b52;border-radius:20px;padding:20px;box-shadow:0 10px 35px #0003;margin:8px 0;}}
.panel-title{{font-weight:800;font-size:15px;color:#f5f9ff;margin-bottom:5px;}}
.panel-sub{{font-size:11px;color:#88a6bc;line-height:1.55;}}
.pill{{display:inline-block;border:1px solid color-mix(in srgb,var(--a) 65%,#183b52);border-radius:30px;padding:7px 12px;color:var(--a2);font-size:10px;letter-spacing:1px;font-weight:800;background:#091a29;}}
.metric{{font-size:21px;font-weight:900;color:#fff;}}
.orb-wrap{{display:flex;justify-content:center;margin:25px 0 14px;}}
.orb{{height:190px;width:190px;border-radius:50%;border:2px solid var(--a);display:flex;align-items:center;justify-content:center;flex-direction:column;background:radial-gradient(circle at 50% 40%,color-mix(in srgb,var(--a) 27%,#0b2033),#071522 72%);box-shadow:0 0 0 10px color-mix(in srgb,var(--a) 8%,transparent),0 0 48px var(--glow),inset 0 0 30px color-mix(in srgb,var(--a) 14%,transparent);}}
.orb-icon{{font-size:54px;filter:drop-shadow(0 0 12px var(--a));}}
.orb-label{{font-size:10px;letter-spacing:2px;font-weight:900;color:#fff;margin-top:5px;}}
.feature{{display:flex;align-items:center;gap:12px;padding:13px 0;border-bottom:1px solid #173246;}}
.feature:last-child{{border-bottom:0;}}
.feature-icon{{width:38px;height:38px;border-radius:12px;background:#102b3d;border:1px solid #21445a;display:flex;align-items:center;justify-content:center;font-size:18px;}}
.feature-name{{font-size:12px;font-weight:800;color:#f3f7ff;}}
.feature-desc{{font-size:10px;color:#88a6bc;margin-top:3px;}}
div.stButton>button,div.stFormSubmitButton>button{{width:100%;min-height:44px;border-radius:13px;border:1px solid #246078;background:linear-gradient(100deg,var(--a),var(--a2));color:#fff;font-weight:800;letter-spacing:.2px;box-shadow:0 6px 22px var(--glow);transition:transform .15s ease,filter .15s ease;}}
div.stButton>button:hover,div.stFormSubmitButton>button:hover{{border-color:#fff;color:#fff;filter:brightness(1.08);transform:translateY(-1px);}}
div.stButton>button[kind="secondary"]{{background:#0a1b2b;border:1px solid #21455c;color:#dceafa;box-shadow:none;}}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stSelectbox"] div[data-baseweb="select"]{{background:#071827;color:#f4f8ff;border-color:#21455c;border-radius:10px;}}
[data-testid="stTextInput"] label,[data-testid="stTextArea"] label,[data-testid="stSelectbox"] label,[data-testid="stRadio"] label,[data-testid="stCheckbox"] label{{color:#b5c8d8!important;}}
[data-testid="stRadio"] div[role="radiogroup"]{{gap:10px;}}
hr{{border-color:#17384d;}}
div[data-testid="stAlert"]{{border-radius:14px;}}
.stCaption{{color:#7f9bb2;}}
.footer{{text-align:center;color:#537087;font-size:10px;letter-spacing:1.3px;padding-top:22px;}}
@media(max-width:700px){{.top-status{{display:none}}.block-container{{padding-left:1rem;padding-right:1rem}}.orb{{width:160px;height:160px}}}}
</style>
""", unsafe_allow_html=True)

def header(status="SILENT DISPATCH READY"):
    st.markdown(f"""<div class="brand"><div class="brand-shield">🛡️</div>
    <div><div class="brand-name">RAABTA</div><div class="brand-tag">SAFER. STRONGER. TOGETHER.</div></div>
    <div class="top-status">● {status}</div></div>""", unsafe_allow_html=True)

def panel(title, subtitle="", icon="✦", body=""):
    st.markdown(f"""<div class="panel"><div class="feature"><div class="feature-icon">{icon}</div><div>
    <div class="panel-title">{title}</div><div class="panel-sub">{subtitle}</div></div></div>{body}</div>""", unsafe_allow_html=True)

def go(screen):
    st.session_state.screen = screen
    st.rerun()

def footer():
    st.markdown('<div class="footer">RAABTA • YOUR SAFETY, CONNECTED • DEMO MODE</div>', unsafe_allow_html=True)

def sms_link(phone, message):
    return "sms:" + urllib.parse.quote(phone or "") + "?&body=" + urllib.parse.quote(message)

def safety_message():
    name = p.get("name") or "Your contact"
    return f"RAABTA SOS ALERT: {name} may need help. {p.get('sos_message', DEFAULT_MESSAGE)} Location sharing is available only if your device/browser supports it. Please call them now."

# WELCOME
if st.session_state.screen == "welcome":
    header("YOUR SAFETY STARTS HERE")
    st.markdown('<div style="text-align:center;padding:34px 8px 12px"><div class="eyebrow">A PERSONAL SAFETY COMPANION</div><div class="hero-title" style="font-size:clamp(42px,8vw,76px);letter-spacing:5px;margin-top:15px">RA<span style="color:#27dfcf">◆</span>BTA</div><div style="font-size:15px;letter-spacing:3px;color:#c4d7e7">Safer. Stronger. Together.</div><div class="orb-wrap"><div class="orb"><div class="orb-icon">🫶</div><div class="orb-label">YOU ARE NOT ALONE</div></div></div><p class="subtle" style="max-width:560px;margin:0 auto">A little reassurance can make a big difference. Set up your trusted circle and keep help a tap away.</p></div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1: panel("Instant SOS","Quick access to your trusted people.","🚨")
    with c2: panel("Live location","Request location sharing when supported.","📍")
    with c3: panel("Trusted circle","Keep important contacts close.","🛡️")
    st.write("")
    if st.button("GET STARTED  →", use_container_width=True): go("profile")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("I ALREADY HAVE AN ACCOUNT", type="secondary"): go("login")
    with c2:
        if st.button("EXPLORE DEMO DASHBOARD", type="secondary"):
            st.session_state.profile["name"] = st.session_state.profile.get("name") or "Aditi"
            st.session_state.logged_in = True
            go("home")
    footer()

# PROFILE
elif st.session_state.screen == "profile":
    header("STEP 01 / YOUR PROFILE")
    st.markdown('<div class="eyebrow">LET’S GET TO KNOW YOU</div><div class="hero-title">Set up your Raabta Profile</div><p class="subtle">Your details help personalise your safety experience. Use demo details for a presentation.</p>', unsafe_allow_html=True)
    with st.form("profile_form"):
        a,b = st.columns(2)
        with a:
            name = st.text_input("Full name *", value=p.get("name",""), placeholder="e.g. Aditi Sharma")
            email = st.text_input("Email address *", value=p.get("email",""), placeholder="you@example.com")
            phone = st.text_input("Mobile number *", value=p.get("phone",""), placeholder="+91 98765 43210")
        with b:
            gender = st.selectbox("Choose your theme *", ["Female","Male","Transgender"], index=["Female","Male","Transgender"].index(p.get("gender","Female")))
            address = st.text_input("City / address", value=p.get("address",""), placeholder="Your area or city")
            blood = st.selectbox("Blood group", ["Not specified","A+","A-","B+","B-","AB+","AB-","O+","O-"], index=["Not specified","A+","A-","B+","B-","AB+","AB-","O+","O-"].index(p.get("blood_group","Not specified")))
        allergies = st.text_input("Medical notes / allergies (optional)", value=p.get("allergies",""), placeholder="Anything emergency contacts should know")
        password = st.text_input("Create demo password (optional)", type="password", value="", help="For local demo only.")
        submitted = st.form_submit_button("SAVE PROFILE & CONTINUE  →")
    if submitted:
        if not name.strip() or not email.strip() or not phone.strip():
            st.error("Please fill in your name, email and mobile number.")
        elif "@" not in email or "." not in email.split("@")[-1]:
            st.error("Please enter a valid email address.")
        else:
            p.update({"name":name.strip(),"email":email.strip().lower(),"phone":phone.strip(),"gender":gender,"address":address,"blood_group":blood,"allergies":allergies,"password":password})
            go("protection")
    if st.button("← BACK"): go("welcome")
    footer()

# PROTECTION / CONTACTS
elif st.session_state.screen == "protection":
    header("STEP 02 / PROTECTION")
    st.markdown('<div class="eyebrow">YOUR PEOPLE, ONE TAP AWAY</div><div class="hero-title">Set Up Your Raabta Protection</div><p class="subtle">Add at least one trusted person for your demo. You can edit these details later.</p>', unsafe_allow_html=True)
    with st.form("protection_form"):
        st.markdown("#### 🛡️ Trusted Circle")
        a,b = st.columns(2)
        with a:
            ename = st.text_input("Trusted contact name *", value=p.get("emergency_name",""), placeholder="Parent / friend")
            ephone = st.text_input("Trusted contact phone *", value=p.get("emergency_phone",""), placeholder="+91 98765 43210")
        with b:
            relation = st.selectbox("Relationship", ["Parent","Sibling","Friend","Partner","Guardian","Other"], index=["Parent","Sibling","Friend","Partner","Guardian","Other"].index(p.get("emergency_relation","Parent")) if p.get("emergency_relation","Parent") in ["Parent","Sibling","Friend","Partner","Guardian","Other"] else 0)
            sosmsg = st.text_area("Emergency message", value=p.get("sos_message",DEFAULT_MESSAGE), height=90)
        st.markdown("#### 🔔 Safety preferences")
        share = st.checkbox("Allow location request during SOS (browser permission required)", value=True)
        sound = st.checkbox("Enable loud help screen in demo", value=True)
        submitted = st.form_submit_button("SAVE PROTECTION SETTINGS  →")
    if submitted:
        if not ename.strip() or not ephone.strip():
            st.error("Please add a trusted contact name and phone number.")
        else:
            p.update({"emergency_name":ename.strip(),"emergency_phone":ephone.strip(),"emergency_relation":relation,"sos_message":sosmsg.strip() or DEFAULT_MESSAGE,"share_location":share,"sound_enabled":sound})
            try:
                save_user(p)
            except Exception as e:
                st.warning(f"Profile saved for this session. Local database note: {e}")
            st.session_state.logged_in = True
            go("home")
    if st.button("← BACK TO PROFILE"): go("profile")
    footer()

# LOGIN
elif st.session_state.screen == "login":
    header("WELCOME BACK")
    st.markdown('<div class="eyebrow">YOUR TRUSTED CIRCLE IS WAITING</div><div class="hero-title">Log in to Raabta</div><p class="subtle">Use the email address saved on this device.</p>', unsafe_allow_html=True)
    with st.form("login_form"):
        email = st.text_input("Email address", value=p.get("email",""))
        submit = st.form_submit_button("CONTINUE  →")
    if submit:
        found = load_user(email) if email else None
        if found:
            p.update({k:found.get(k,p.get(k,"")) for k in ["name","phone","email","address","gender","blood_group","allergies","emergency_name","emergency_phone","emergency_relation","sos_message"]})
            st.session_state.logged_in = True
            go("home")
        else:
            st.error("No saved profile found for that email on this device. Choose Get Started to create one.")
    if st.button("← BACK"): go("welcome")
    footer()

# HOME DASHBOARD
elif st.session_state.screen == "home":
    header()
    c1,c2 = st.columns([1.45,1])
    with c1:
        st.markdown(f'<div class="eyebrow">GOOD TO HAVE YOU HERE</div><div class="hero-title" style="font-size:clamp(30px,4vw,44px)">Hi, {html.escape(p.get("name") or "Aditi")} 👋</div><span class="pill">{theme["label"]}</span><p class="subtle" style="margin-top:12px">Your safety circle is one tap away. If you feel unsafe, activate SOS.</p>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="panel"><div class="eyebrow">SAFETY STATUS</div><div class="metric" style="margin-top:10px">● Ready</div><div class="panel-sub">Silent dispatch prepared · Demo mode</div><hr><div class="panel-sub">Trusted contact</div><div class="panel-title">{html.escape(p.get("emergency_name") or "Not added yet")}</div><div class="panel-sub">{html.escape(p.get("emergency_phone") or "Add a contact in setup")}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="orb-wrap"><div class="orb"><div class="orb-icon">🫶</div><div class="orb-label">INSTANT SOS</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center" class="subtle">Press the button below to start the SOS demo. Real emergency calls and SMS are not sent automatically.</div>', unsafe_allow_html=True)
    if st.button("🚨  ACTIVATE SOS", use_container_width=True):
        st.session_state.sos_active = False
        go("sos")
    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1:
        panel("Current location","Request browser location access.","📍")
        if st.button("GET MY LOCATION", key="get_location"): go("location")
    with c2:
        panel("Trusted Circle", "Review your emergency contact.","🛡️")
        if st.button("VIEW CONTACT", key="view_contact"): go("trusted")
    with c3:
        panel("Loud Help","Open the alarm screen.","🔊")
        if st.button("OPEN LOUD HELP", key="open_loud"): go("loud_help")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("🔋 LOW BATTERY DEMO"): go("battery")
    with c2:
        if st.button("⭐ REVIEW YOUR EXPERIENCE"): go("review")
    st.markdown('<div class="panel"><div class="panel-title">Emergency contacts</div><div class="panel-sub">Your selected trusted contact is saved locally for this demo. Use the SOS screen to open your device’s SMS app with a prepared message.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">HOME　 •　 TRUSTED CIRCLE　 •　 EMERGENCY　 •　 PROFILE</div>', unsafe_allow_html=True)

# SOS ACTIVATED
elif st.session_state.screen == "sos":
    header("SOS FLOW / CONFIRMATION")
    st.markdown('<div class="eyebrow">EMERGENCY MODE</div><div class="hero-title">SOS is ready to activate</div><p class="subtle">This is the confirmation screen. In this web demo, tap the confirm button to simulate an SOS activation.</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel" style="border-color:{A};box-shadow:0 0 35px {G}"><div class="eyebrow">SOS ACTIVATION</div><div class="hero-title" style="font-size:30px">Your safety matters.</div><p class="subtle">A prepared alert will be shown, and you can open your SMS app to send it to your trusted contact.</p><div class="feature"><div class="feature-icon">📍</div><div><div class="feature-name">Location</div><div class="feature-desc">Browser permission needed; location is not silently tracked.</div></div></div><div class="feature"><div class="feature-icon">🛡️</div><div><div class="feature-name">{html.escape(p.get("emergency_name") or "Trusted contact")}</div><div class="feature-desc">{html.escape(p.get("emergency_phone") or "No phone added")}</div></div></div></div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        if st.button("CONFIRM SOS ACTIVATION", use_container_width=True):
            st.session_state.sos_active = True
            st.session_state.history.append(f"SOS demo activated at {datetime.now().strftime('%H:%M:%S')}")
            go("sos_active")
    with c2:
        if st.button("CANCEL & RETURN HOME", type="secondary"): go("home")
    footer()

elif st.session_state.screen == "sos_active":
    header("SOS ACTIVE · DEMO")
    st.markdown('<div class="eyebrow">SOS ACTIVATED</div><div class="hero-title">Help is being prepared.</div><p class="subtle">Demo status only — no police or emergency service has been contacted automatically.</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel" style="border-color:{A};box-shadow:0 0 30px {G}"><div class="eyebrow">EMERGENCY ALERT</div><div class="hero-title" style="font-size:27px">Your SOS alert</div><p class="subtle">{html.escape(safety_message())}</p><div class="feature"><div class="feature-icon">👤</div><div><div class="feature-name">Trusted contact</div><div class="feature-desc">{html.escape(p.get("emergency_name") or "Not set")} · {html.escape(p.get("emergency_phone") or "No number")}</div></div></div><div class="feature"><div class="feature-icon">📍</div><div><div class="feature-name">Location status</div><div class="feature-desc">Not acquired yet. Use “Request location” and allow browser access if prompted.</div></div></div></div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.link_button("OPEN SMS APP WITH ALERT", sms_link(p.get("emergency_phone",""), safety_message()), use_container_width=True)
    with c2:
        if st.button("OPEN LOUD HELP", use_container_width=True): go("loud_help")
    c1,c2 = st.columns(2)
    with c1:
        if st.button("REQUEST LOCATION"): go("location")
    with c2:
        if st.button("I AM SAFE — END DEMO", type="secondary"):
            st.session_state.sos_active = False
            go("home")
    footer()

# LOCATION
elif st.session_state.screen == "location":
    header("LOCATION REQUEST")
    st.markdown('<div class="eyebrow">LOCATION SHARING</div><div class="hero-title">Request your location</div><p class="subtle">Your browser will ask permission. Location access depends on browser settings and a secure/local connection.</p>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-title">📍 Location permission</div><div class="panel-sub">Tap the button below. If the browser supports geolocation, it will display the coordinates here. Nothing is sent automatically.</div></div>', unsafe_allow_html=True)
    import streamlit.components.v1 as components
    components.html("""
    <div style="font-family:Arial;background:#081a2b;border:1px solid #21455c;border-radius:14px;padding:18px;color:#eef7ff">
      <button id="locbtn" style="width:100%;padding:14px;border:0;border-radius:10px;background:linear-gradient(90deg,#ff2d78,#21d8c7);color:white;font-weight:bold;cursor:pointer">📍 REQUEST MY LOCATION</button>
      <p id="locresult" style="color:#9bb4c9;font-size:13px;line-height:1.6">Location not requested yet.</p>
    </div>
    <script>
    const b=document.getElementById('locbtn'),r=document.getElementById('locresult');
    b.onclick=()=>{if(!navigator.geolocation){r.textContent='This browser does not support geolocation.';return;}
    r.textContent='Waiting for permission…';navigator.geolocation.getCurrentPosition(
    p=>{r.textContent='Location received: latitude '+p.coords.latitude.toFixed(5)+', longitude '+p.coords.longitude.toFixed(5)+'. This demo does not send it to anyone.';},
    e=>{r.textContent='Could not get location: '+e.message+'. Check browser permission and try again.';},{enableHighAccuracy:true,timeout:10000});};
    </script>""", height=160)
    if st.button("← BACK TO DASHBOARD"): go("home")
    footer()

# TRUSTED CIRCLE
elif st.session_state.screen == "trusted":
    header("YOUR TRUSTED CIRCLE")
    st.markdown('<div class="eyebrow">PEOPLE WHO MATTER</div><div class="hero-title">Trusted Circle</div><p class="subtle">Check the contact saved in your local demo profile.</p>', unsafe_allow_html=True)
    panel(p.get("emergency_name") or "No trusted contact", f'{p.get("emergency_relation") or "Relationship not set"} · {p.get("emergency_phone") or "No phone number"}', "🛡️")
    st.markdown(f'<div class="panel"><div class="panel-title">Your emergency message</div><div class="panel-sub">{html.escape(p.get("sos_message") or DEFAULT_MESSAGE)}</div></div>', unsafe_allow_html=True)
    if p.get("emergency_phone"):
        st.link_button("MESSAGE TRUSTED CONTACT", sms_link(p.get("emergency_phone",""), safety_message()), use_container_width=True)
    if st.button("EDIT CONTACT / PROTECTION SETTINGS"): go("protection")
    if st.button("← BACK TO DASHBOARD", type="secondary"): go("home")
    footer()

# LOUD HELP
elif st.session_state.screen == "loud_help":
    header("LOUD HELP")
    st.markdown('<div class="eyebrow">MAKE SOME NOISE</div><div class="hero-title">LOUD HELP</div><p class="subtle">Use the sound control below to start or stop an alarm in this browser tab. Keep the tab open.</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel" style="text-align:center;border-color:{A};box-shadow:0 0 30px {G}"><div style="font-size:52px">🔊</div><div class="hero-title" style="font-size:28px">HELP! HELP! HELP!</div><p class="subtle">If you are in immediate danger, contact local emergency services directly.</p></div>', unsafe_allow_html=True)
    import streamlit.components.v1 as components
    components.html(f"""
    <div style="font-family:Arial;background:#081a2b;border:1px solid #21455c;border-radius:14px;padding:18px;text-align:center;color:white">
      <button id="alarm" style="padding:14px 22px;width:100%;border:0;border-radius:12px;background:linear-gradient(90deg,{A},{A2});color:white;font-weight:bold;cursor:pointer">▶ START / STOP LOUD ALARM</button>
      <p id="alarmstate" style="color:#a9c0d2;font-size:12px">Alarm is off. Click to enable sound.</p>
    </div>
    <script>
    let ctx=null,osc=null,gain=null,on=false,timer=null;
    const btn=document.getElementById('alarm'),state=document.getElementById('alarmstate');
    function stop(){{if(osc){{try{{osc.stop()}}catch(e){{}}osc=null}}if(gain){{gain.gain.value=0;gain=null}}on=false;clearInterval(timer);state.textContent='Alarm is off.';btn.textContent='▶ START LOUD ALARM';}}
    function start(){{try{{ctx=ctx||new (window.AudioContext||window.webkitAudioContext)();ctx.resume();osc=ctx.createOscillator();gain=ctx.createGain();osc.type='sawtooth';osc.frequency.value=880;gain.gain.value=.14;osc.connect(gain);gain.connect(ctx.destination);osc.start();on=true;let high=false;timer=setInterval(()=>{{if(!osc)return;high=!high;osc.frequency.setTargetAtTime(high?1050:650,ctx.currentTime,.05)}},350);state.textContent='Alarm is playing in this tab. Click again to stop.';btn.textContent='■ STOP LOUD ALARM';}}catch(e){{state.textContent='Audio could not start. Check browser sound permissions.';}}}}
    btn.onclick=()=>{{if(on)stop();else start();}};
    </script>""", height=140)
    c1,c2 = st.columns(2)
    with c1:
        if st.button("OPEN SMS ALERT"): go("sos_active")
    with c2:
        if st.button("I AM SAFE — RETURN HOME", type="secondary"):
            st.session_state.alarm_on = False
            go("home")
    footer()

# LOW BATTERY / PHONE SHUTDOWN SIMULATION
elif st.session_state.screen == "battery":
    header("LOW BATTERY SAFETY MODE")
    st.markdown('<div class="eyebrow">LOW POWER CHECK-IN</div><div class="hero-title">Your phone is about to shut down.</div><p class="subtle">This is a manual demo simulation. A normal web app cannot reliably run in the background or detect 2% battery on every device.</p>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-title">Choose your status</div><div class="panel-sub">Select the option that represents the user’s situation.</div></div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    with a:
        if st.button("🟢 I'M SAFE", use_container_width=True):
            st.session_state.demo_alert = "SAFE"
            st.success("Demo status saved: I’m Safe.")
    with b:
        if st.button("🟠 I NEED HELP", use_container_width=True):
            st.session_state.demo_alert = "NEED HELP"
            st.warning("Demo status saved: I Need Help.")
    with c:
        if st.button("🔴 I'M IN DANGER", use_container_width=True):
            st.session_state.demo_alert = "IN DANGER"
            st.error("Demo status saved: I’m in Danger.")
    if st.session_state.demo_alert:
        st.markdown(f'<div class="panel"><div class="panel-title">Selected status: {html.escape(st.session_state.demo_alert)}</div><div class="panel-sub">This choice is displayed locally. It has not been sent to contacts automatically.</div></div>', unsafe_allow_html=True)
        if st.session_state.demo_alert != "SAFE" and p.get("emergency_phone"):
            st.link_button("OPEN SMS WITH STATUS", sms_link(p.get("emergency_phone",""), f"RAABTA CHECK-IN: {st.session_state.demo_alert}. {safety_message()}"), use_container_width=True)
    st.markdown("#### Battery demo control")
    st.slider("Simulated battery percentage", 0, 100, key="battery_demo")
    st.caption(f"Demo battery: {st.session_state.battery_demo}%")
    if st.button("← BACK TO DASHBOARD"): go("home")
    footer()

# REVIEW
elif st.session_state.screen == "review":
    header("YOUR FEEDBACK MATTERS")
    st.markdown('<div class="eyebrow">HELP US MAKE RAABTA BETTER</div><div class="hero-title">Review Your Experience</div><p class="subtle">Tell us what felt helpful and what we can improve.</p>', unsafe_allow_html=True)
    with st.form("review_form"):
        rating = st.radio("How would you rate your experience?", [1,2,3,4,5], horizontal=True, format_func=lambda x: "★" * x + "☆" * (5-x), index=4 if st.session_state.rating == 0 else st.session_state.rating-1)
        features = st.multiselect("Which features did you find useful?", ["Instant SOS","Trusted Circle","Location sharing","Loud Help","Low battery check-in","Theme personalisation"], default=st.session_state.features)
        feedback = st.text_area("Your feedback", value=st.session_state.feedback, height=130, placeholder="Share your thoughts…")
        submit = st.form_submit_button("SUBMIT FEEDBACK  →")
    if submit:
        st.session_state.rating = rating
        st.session_state.features = features
        st.session_state.feedback = feedback
        st.success("Thank you! Your feedback is saved for this session.")
        st.session_state.history.append(f"Feedback submitted: {rating}/5 at {datetime.now().strftime('%H:%M:%S')}")
    if st.button("← BACK TO DASHBOARD"): go("home")
    footer()

# PROFILE VIEW
elif st.session_state.screen == "profile_view":
    header("YOUR PROFILE")
    st.markdown('<div class="eyebrow">ACCOUNT DETAILS</div><div class="hero-title">Your Raabta Profile</div>', unsafe_allow_html=True)
    panel(p.get("name") or "Demo User", f'{p.get("email") or "No email"} · {p.get("phone") or "No phone"}', "👤")
    panel("Theme", p.get("gender","Female"), "🎨")
    panel("Medical notes", p.get("allergies") or "None added", "➕")
    if st.button("EDIT PROFILE"): go("profile")
    if st.button("← BACK TO DASHBOARD", type="secondary"): go("home")
    footer()

else:
    st.session_state.screen = "welcome"
    st.rerun()
