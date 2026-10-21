import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="JSA SmartRisk | Demo",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Demo-only configuration
# -----------------------------
DEMO_NOTICE = (
    "نمونه نمایشی با داده‌های غیرواقعی است. این سامانه جایگزین دستورالعمل‌های مصوب، "
    "ارزیابی میدانی یا تأیید متخصص HSE نیست."
)

RISK_BANDS = [
    (1, 4, "پایین", "Low"),
    (5, 9, "متوسط", "Medium"),
    (10, 16, "بالا", "High"),
    (17, 25, "بحرانی", "Critical"),
]

SAMPLE_JOBS = [
    {
        "step": "۱",
        "activity": "آماده‌سازی محل کار",
        "hazard": "تردد هم‌زمان افراد و تجهیزات",
        "consequence": "برخورد یا آسیب فیزیکی",
        "controls": "محدوده‌بندی محل، نصب علائم و هماهنگی با مسئول محل",
        "likelihood": 3,
        "severity": 3,
        "res_likelihood": 1,
        "res_severity": 3,
        "owner": "سرپرست کار (نمونه)",
        "status": "پیش‌نویس",
    },
    {
        "step": "۲",
        "activity": "بازکردن اتصال فلنج (سناریوی آموزشی)",
        "hazard": "احتمال باقی‌ماندن فشار یا ماده در خط",
        "consequence": "رهاسازی ناخواسته و تماس با ماده",
        "controls": "تأیید ایزولاسیون، تخلیه فشار، بررسی شرایط ایمن و مجوزهای لازم طبق رویه مصوب",
        "likelihood": 4,
        "severity": 5,
        "res_likelihood": 2,
        "res_severity": 5,
        "owner": "مسئول عملیات (نمونه)",
        "status": "نیازمند بررسی HSE",
    },
    {
        "step": "۳",
        "activity": "جمع‌آوری ابزار و تحویل محل",
        "hazard": "باقی‌ماندن ابزار یا موانع در مسیر",
        "consequence": "لغزش، زمین‌خوردن یا اختلال در تردد",
        "controls": "بازرسی نهایی محل، جمع‌آوری ابزار و تحویل رسمی محل",
        "likelihood": 2,
        "severity": 2,
        "res_likelihood": 1,
        "res_severity": 2,
        "owner": "سرپرست کار (نمونه)",
        "status": "پیش‌نویس",
    },
]

def score(likelihood: int, severity: int) -> int:
    return int(likelihood) * int(severity)

def band(score_value: int):
    for low, high, fa, en in RISK_BANDS:
        if low <= score_value <= high:
            return fa, en
    return "تعریف‌نشده", "Unclassified"

def risk_color(level_en: str) -> str:
    return {
        "Low": "#2e7d32",
        "Medium": "#b26a00",
        "High": "#c62828",
        "Critical": "#6a1b9a",
    }.get(level_en, "#555555")

def make_df(rows):
    output = []
    for row in rows:
        initial = score(row["likelihood"], row["severity"])
        residual = score(row["res_likelihood"], row["res_severity"])
        initial_fa, initial_en = band(initial)
        residual_fa, residual_en = band(residual)
        output.append({
            "گام": row["step"],
            "فعالیت": row["activity"],
            "مخاطره": row["hazard"],
            "پیامد": row["consequence"],
            "اقدامات کنترلی پیشنهادی": row["controls"],
            "احتمال اولیه": row["likelihood"],
            "شدت اولیه": row["severity"],
            "ریسک اولیه": initial,
            "سطح اولیه": initial_fa,
            "احتمال باقیمانده": row["res_likelihood"],
            "شدت باقیمانده": row["res_severity"],
            "ریسک باقیمانده": residual,
            "سطح باقیمانده": residual_fa,
            "مسئول پیشنهادی": row["owner"],
            "وضعیت": row["status"],
        })
    return pd.DataFrame(output)

if "jobs" not in st.session_state:
    st.session_state.jobs = [dict(item) for item in SAMPLE_JOBS]

if "language" not in st.session_state:
    st.session_state.language = "فارسی"

with st.sidebar:
    st.title("🦺 JSA SmartRisk")
    st.caption("نسخه نمایشی اولیه")
    language = st.radio("زبان / Language", ["فارسی", "English"], horizontal=True)
    st.session_state.language = language
    st.divider()
    st.markdown("**محیط اجرا**")
    st.info("Demo mode · داده‌های ساختگی")
    st.markdown("**وضعیت الزامات داخلی**")
    st.warning("مستندات داخلی در دسترس نیست؛ آستانه‌ها و فرم‌ها باید بعداً با مدارک مصوب تطبیق داده شوند.")
    if st.button("بازنشانی داده‌های نمونه", use_container_width=True):
        st.session_state.jobs = [dict(item) for item in SAMPLE_JOBS]
        st.rerun()

is_en = language == "English"

if is_en:
    st.title("JSA SmartRisk")
    st.subheader("Job Safety Analysis & Risk Assessment")
    st.warning("DEMO ONLY — fictional data. Not an approved refinery procedure or authorization to perform work.")
else:
    st.title("JSA SmartRisk")
    st.subheader("سامانه تحلیل ایمنی شغل و ارزیابی ریسک")
    st.warning(DEMO_NOTICE)

tab_dashboard, tab_editor, tab_matrix, tab_about = st.tabs(
    ["داشبورد", "ثبت / ویرایش JSA", "ماتریس ریسک", "راهنما و معماری"]
)

with tab_dashboard:
    df = make_df(st.session_state.jobs)
    total = len(df)
    high_or_critical = int(df["سطح اولیه"].isin(["بالا", "بحرانی"]).sum())
    needs_review = sum(1 for job in st.session_state.jobs if job["status"] != "تأییدشده")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("گام‌های کاری", total)
    c2.metric("ریسک اولیه بالا/بحرانی", high_or_critical)
    c3.metric("موارد نیازمند بررسی", needs_review)
    c4.metric("وضعیت سامانه", "نمایشی")

    st.markdown("#### خلاصه ارزیابی")
    view_cols = ["گام", "فعالیت", "مخاطره", "ریسک اولیه", "سطح اولیه", "ریسک باقیمانده", "سطح باقیمانده", "وضعیت"]
    st.dataframe(df[view_cols], use_container_width=True, hide_index=True)

    st.markdown("#### نکات استفاده")
    st.markdown(
        "- امتیاز ریسک در این نمونه با فرمول **احتمال × شدت** محاسبه می‌شود.\n"
        "- امتیازها و باندهای ریسک صرفاً نمایشی هستند و باید با روش مصوب سازمان جایگزین شوند.\n"
        "- هوش مصنوعی در نسخه‌های بعدی می‌تواند پیش‌نویس پیشنهاد دهد؛ تصمیم نهایی و تأیید با متخصص مجاز است."
    )

with tab_editor:
    st.markdown("#### مشخصات فعالیت")
    with st.form("job_meta"):
        col1, col2 = st.columns(2)
        with col1:
            job_title = st.text_input("عنوان فعالیت", value="تعمیرات نمونه‌ای تجهیزات")
            work_area = st.text_input("واحد / محل کار", value="واحد فرضی A")
            work_date = st.date_input("تاریخ ارزیابی", value=date.today())
        with col2:
            assessor = st.text_input("تهیه‌کننده (نمونه)", value="کارشناس HSE - نمونه")
            permit = st.selectbox("وضعیت مجوز کار", ["نامشخص / نیازمند بررسی", "در حال بررسی", "تأییدشده (فقط نمونه)"])
            language_label = st.selectbox("زبان خروجی", ["فارسی", "English"])
        meta_saved = st.form_submit_button("ثبت مشخصات نمایشی")
    if meta_saved:
        st.session_state.job_meta = {
            "job_title": job_title, "work_area": work_area,
            "work_date": str(work_date), "assessor": assessor,
            "permit": permit, "language": language_label
        }
        st.success("مشخصات فقط در نشست فعلی نمونه ذخیره شد.")

    st.divider()
    st.markdown("#### افزودن گام جدید")
    with st.form("add_step", clear_on_submit=True):
        a, b = st.columns(2)
        with a:
            activity = st.text_input("شرح گام کاری", placeholder="مثلاً آماده‌سازی محل")
            hazard = st.text_input("مخاطره شناسایی‌شده")
            consequence = st.text_input("پیامد محتمل")
            controls = st.text_area("اقدامات کنترلی پیشنهادی")
        with b:
            owner = st.text_input("مسئول پیشنهادی", value="تعیین نشده")
            likelihood = st.slider("احتمال اولیه (۱ تا ۵)", 1, 5, 3)
            severity = st.slider("شدت اولیه (۱ تا ۵)", 1, 5, 3)
            res_likelihood = st.slider("احتمال باقیمانده (۱ تا ۵)", 1, 5, 2)
            res_severity = st.slider("شدت باقیمانده (۱ تا ۵)", 1, 5, 3)
        submitted = st.form_submit_button("افزودن گام به پیش‌نویس")
        if submitted:
            if not activity.strip() or not hazard.strip():
                st.error("شرح گام کاری و مخاطره را وارد کنید.")
            else:
                st.session_state.jobs.append({
                    "step": str(len(st.session_state.jobs) + 1),
                    "activity": activity.strip(),
                    "hazard": hazard.strip(),
                    "consequence": consequence.strip() or "نیازمند تعیین",
                    "controls": controls.strip() or "نیازمند تعیین توسط متخصص HSE",
                    "likelihood": likelihood,
                    "severity": severity,
                    "res_likelihood": res_likelihood,
                    "res_severity": res_severity,
                    "owner": owner.strip() or "تعیین نشده",
                    "status": "پیش‌نویس",
                })
                st.success("گام به پیش‌نویس افزوده شد.")
                st.rerun()

    st.divider()
    st.markdown("#### گام‌های ثبت‌شده")
    for idx, job in enumerate(st.session_state.jobs):
        with st.expander(f"گام {job['step']} — {job['activity']}"):
            st.write(f"**مخاطره:** {job['hazard']}")
            st.write(f"**پیامد:** {job['consequence']}")
            st.write(f"**کنترل‌ها:** {job['controls']}")
            initial = score(job["likelihood"], job["severity"])
            residual = score(job["res_likelihood"], job["res_severity"])
            i_fa, i_en = band(initial)
            r_fa, r_en = band(residual)
            x, y = st.columns(2)
            x.metric("ریسک اولیه", f"{initial} · {i_fa}")
            y.metric("ریسک باقیمانده", f"{residual} · {r_fa}")
            st.caption("سطوح ریسک و محاسبات صرفاً نمونه‌اند؛ کنترل‌ها باید برای شرایط واقعی کار بازبینی شوند.")
            status_options = ["پیش‌نویس", "نیازمند بررسی HSE", "بررسی‌شده (نمونه)", "تأییدشده (نمونه)"]
            current_status = job["status"] if job["status"] in status_options else status_options[0]
            new_status = st.selectbox("وضعیت گردش کار", status_options, index=status_options.index(current_status), key=f"status_{idx}")
            if new_status != job["status"]:
                st.session_state.jobs[idx]["status"] = new_status
            if st.button("حذف این گام", key=f"delete_{idx}"):
                st.session_state.jobs.pop(idx)
                for n, item in enumerate(st.session_state.jobs, start=1):
                    item["step"] = str(n)
                st.rerun()

    export_df = make_df(st.session_state.jobs)
    csv = export_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "دانلود جدول JSA (CSV)",
        data=csv,
        file_name="jsa_smartrisk_demo.csv",
        mime="text/csv",
    )

with tab_matrix:
    st.markdown("#### ماتریس نمونه ۵×۵")
    st.caption("این ماتریس فقط برای نمایش عملکرد نرم‌افزار است. باندها و معیارها قابل پیکربندی‌اند و تأییدشده از سوی پالایشگاه نیستند.")
    matrix_rows = []
    for sev in range(5, 0, -1):
        row = {"شدت ↓ / احتمال →": sev}
        for lik in range(1, 6):
            val = lik * sev
            fa, en = band(val)
            row[f"احتمال {lik}"] = f"{val} · {fa}"
        matrix_rows.append(row)
    st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)
    st.markdown("**تعریف نمونه احتمال و شدت**")
    st.write("۱ = کم، ۲ = نسبتاً کم، ۳ = متوسط، ۴ = زیاد، ۵ = بسیار زیاد. این تعاریف آموزشی و موقت‌اند.")
    st.markdown("**باندهای نمونه**")
    st.table(pd.DataFrame([
        {"امتیاز": "۱–۴", "سطح": "پایین / Low"},
        {"امتیاز": "۵–۹", "سطح": "متوسط / Medium"},
        {"امتیاز": "۱۰–۱۶", "سطح": "بالا / High"},
        {"امتیاز": "۱۷–۲۵", "سطح": "بحرانی / Critical"},
    ]))

with tab_about:
    st.markdown("#### معماری پیشنهادی")
    st.code(
        "Browser\n"
        "  └── Streamlit UI (prototype)\n"
        "        ├── JSA forms and workflow\n"
        "        ├── Deterministic risk calculation\n"
        "        └── CSV export\n\n"
        "Production evolution:\n"
        "  Streamlit or FastAPI + frontend\n"
        "  PostgreSQL + role-based access control\n"
        "  Audit log + approved risk matrix configuration\n"
        "  Optional AI draft suggestions behind an explicit review gate",
        language="text",
    )
    st.markdown("#### محدودیت‌های این نسخه")
    st.markdown(
        "- اطلاعات در حافظه نشست نگهداری می‌شوند؛ پایگاه داده دائمی، ورود کاربران و ثبت رویداد حسابرسی هنوز پیاده‌سازی نشده‌اند.\n"
        "- خروجی فعلی CSV است؛ قالب PDF رسمی در نسخه بعدی قابل افزودن است.\n"
        "- قابلیت اتصال به مدل هوش مصنوعی عمداً فعال نشده تا داده عملیاتی به سرویس بیرونی ارسال نشود.\n"
        "- تأیید وضعیت در این دمو فقط نمایشی است و معادل تأیید رسمی یا امضای دیجیتال نیست."
    )
    st.info("پیش از استفاده عملیاتی، باید فرم‌های مصوب، روش امتیازدهی، نقش‌ها، فرایند تأیید و الزامات امنیت اطلاعات توسط مسئولان مجاز مشخص شوند.")

st.caption("JSA SmartRisk · Prototype v0.1 · Fictional demo data only")
