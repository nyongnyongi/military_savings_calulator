import base64
import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP, getcontext
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta

getcontext().prec = 28
ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
D = Decimal

st.set_page_config(
    page_title="헌신의 대가",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@dataclass(frozen=True)
class Service:
    key: str
    name: str
    english: str
    months: int
    motto: str
    primary: str
    primary_dark: str
    primary_soft: str
    border: str
    background_file: str
    logo_file: str


SERVICES: Dict[str, Service] = {
    "육군": Service("army", "대한민국 육군", "REPUBLIC OF KOREA ARMY", 18, "강한 육군, 자랑스러운 육군", "#52631f", "#26340d", "#eef1e5", "#8d9861", "army_bg.png", "army_logo.png"),
    "해군": Service("navy", "대한민국 해군", "REPUBLIC OF KOREA NAVY", 20, "필승해군, 정예해군", "#0e3d69", "#031f3d", "#edf4fa", "#557b9f", "navy_bg.png", "navy_logo.png"),
    "공군": Service("airforce", "대한민국 공군", "REPUBLIC OF KOREA AIR FORCE", 21, "대한민국을 지키는 가장 높은 힘", "#287eb5", "#0b4c79", "#edf7fc", "#76a9c9", "airforce_bg.png", "airforce_logo.png"),
    "해병대": Service("marines", "대한민국 해병대", "REPUBLIC OF KOREA MARINE CORPS", 18, "한번 해병은 영원한 해병", "#b2151b", "#72080c", "#fff1ed", "#c96961", "marines_bg.png", "marines_logo.png"),
}

DEFAULT_SALARY = {"이병": 750_000, "일병": 900_000, "상병": 1_200_000, "병장": 1_500_000}
RANK_MONTHS = (2, 6, 6)


def data_uri(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    mime = "image/jpeg" if suffix in {"jpg", "jpeg"} else f"image/{suffix}"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def won(value) -> str:
    value = Decimal(value).quantize(D("1"), rounding=ROUND_HALF_UP)
    return f"{int(value):,}원"


def calc_discharge_date(enlistment: date, months: int) -> date:
    return enlistment + relativedelta(months=months) - timedelta(days=1)


def rank_periods(enlistment: date, discharge: date) -> List[Tuple[str, date, date]]:
    bounds = [
        enlistment,
        enlistment + relativedelta(months=2),
        enlistment + relativedelta(months=8),
        enlistment + relativedelta(months=14),
        discharge + timedelta(days=1),
    ]
    result = []
    for i, rank in enumerate(["이병", "일병", "상병", "병장"]):
        start = bounds[i]
        end = min(bounds[i + 1] - timedelta(days=1), discharge)
        if start <= end:
            result.append((rank, start, end))
    return result


def truncate_unit(value: Decimal, unit: int) -> Decimal:
    u = D(unit)
    return (value / u).quantize(D("1"), rounding=ROUND_DOWN) * u


def salary_ledger(enlistment: date, discharge: date, salaries: Dict[str, int], daily_unit: int) -> pd.DataFrame:
    rows = []
    periods = rank_periods(enlistment, discharge)
    cursor = enlistment.replace(day=1)
    while cursor <= discharge:
        dim = calendar.monthrange(cursor.year, cursor.month)[1]
        month_end = date(cursor.year, cursor.month, dim)
        service_start, service_end = max(cursor, enlistment), min(month_end, discharge)
        for rank, rank_start, rank_end in periods:
            start, end = max(service_start, rank_start), min(service_end, rank_end)
            if start > end:
                continue
            served = (end - start).days + 1
            monthly = D(salaries[rank])
            # If the service covered the full month, pay the full monthly salary.
            # Otherwise, compute by prorated (daily) amount with truncation.
            if served == dim:
                amount = monthly
                daily = truncate_unit(monthly / D(dim), daily_unit)
            else:
                daily = truncate_unit(monthly / D(dim), daily_unit)
                amount = daily * D(served)
            rows.append({
                "지급월": f"{cursor.year}-{cursor.month:02d}", "계급": rank,
                "적용 시작일": start.isoformat(), "적용 종료일": end.isoformat(),
                "월 일수": dim, "복무일수": served, "월 봉급": int(monthly),
                "계산 일급": int(daily), "지급 봉급": int(amount),
            })
        cursor += relativedelta(months=1)
    return pd.DataFrame(rows)


def deposit_dates(start: date, maturity: date, day: int) -> List[date]:
    result = []
    cursor = start.replace(day=1)
    while cursor <= maturity:
        dim = calendar.monthrange(cursor.year, cursor.month)[1]
        current = date(cursor.year, cursor.month, min(day, dim))
        if start <= current <= maturity:
            result.append(current)
        cursor += relativedelta(months=1)
    return result


def savings_ledger(start: date, maturity: date, payment: int, annual_rate: float, payment_day: int, method: str) -> pd.DataFrame:
    rows = []
    principal = D(payment)
    rate = D(str(annual_rate)) / D("100")
    for idx, deposit in enumerate(deposit_dates(start, maturity, payment_day), 1):
        if method == "실제 예치일수 ÷ 365":
            days = max(0, (maturity - deposit).days)
            interest = principal * rate * D(days) / D("365")
            period = f"{days}일"
        else:
            months = max(0, (maturity.year - deposit.year) * 12 + maturity.month - deposit.month)
            interest = principal * rate * D(months) / D("12")
            period = f"{months}개월"
        rows.append({
            "회차": idx, "납입일": deposit.isoformat(), "납입원금": int(principal),
            "이자 적용기간": period, "예상이자": int(interest.quantize(D("1"), rounding=ROUND_DOWN)),
        })
    return pd.DataFrame(rows)


def total(df: pd.DataFrame, col: str) -> Decimal:
    return D(0) if df.empty else D(int(df[col].sum()))


def inject_css(service: Service):
    bg = data_uri(ASSETS / service.background_file)
    logo = data_uri(ASSETS / service.logo_file)
    css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');
:root{--p:%s;--pd:%s;--ps:%s;--bd:%s;--logo:url('%s');}
html,body,[class*="css"]{font-family:'Noto Sans KR',sans-serif;}
.stApp{background:#d7d7d0 url('%s') center top/100%% 100%% fixed no-repeat; color:#15202b;}
.stApp:before{content:"";position:fixed;inset:0;background:rgba(255,255,255,.05);pointer-events:none;z-index:0;}
#MainMenu,footer{visibility:hidden;} header[data-testid="stHeader"]{background:transparent;height:0;}
.block-container{max-width:1320px;padding:7.2rem 2.7rem 5.2rem;position:relative;z-index:1;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,var(--pd),var(--p));border-right:1px solid rgba(255,255,255,.28);box-shadow:10px 0 30px rgba(0,0,0,.17);}
section[data-testid="stSidebar"]>div{padding-top:1.5rem;}
/* Sidebar: make form labels readable, keep brand white */
section[data-testid="stSidebar"]{color:#18202a!important;background:linear-gradient(180deg,var(--pd),var(--p));}
section[data-testid="stSidebar"] .brand, section[data-testid="stSidebar"] .nav-label {color:white!important;}
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] [role="group"] label, section[data-testid="stSidebar"] .stMarkdown p, section[data-testid="stSidebar"] .stText {color:#18202a!important;}
/* Force dark color on common inline/text elements in sidebar to override Streamlit defaults */
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] small, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] div, section[data-testid="stSidebar"] li, section[data-testid="stSidebar"] strong {color:#18202a!important;opacity:1!important}
section[data-testid="stSidebar"] [data-testid="stCaption"], section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {color:#4a5560!important}
/* Sidebar buttons: opaque white with dark text */
section[data-testid="stSidebar"] .stButton>button{background:#ffffff!important;color:#18202a!important;border:1px solid rgba(0,0,0,.08)!important;box-shadow:0 6px 14px rgba(0,0,0,.06)!important}
/* Make input controls in sidebar high-contrast and readable */
section[data-testid="stSidebar"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-baseweb="select"]>div,
section[data-testid="stSidebar"] input[type="number"],
section[data-testid="stSidebar"] input[type="text"],
section[data-testid="stSidebar"] input[type="date"] {
    background:#fff!important;
    color:#18202a!important;
    border-radius:7px!important;
}
section[data-testid="stSidebar"] [data-testid="stDateInput"] input{background:#fff!important;color:#18202a!important}
.brand{display:flex;align-items:center;gap:18px;padding:0 4px 18px;border-bottom:1px solid rgba(255,255,255,.24);}
.brand img{width:auto;max-width:74px;height:74px;object-fit:contain;filter:drop-shadow(0 4px 5px rgba(0,0,0,.25));}
.brand h1{font-size:1.55rem;margin:0;font-weight:900;letter-spacing:-.02em;font-family:'Noto Sans KR',sans-serif;}
.brand h1{font-size:1.55rem;margin:0;font-weight:900;letter-spacing:-.02em;font-family:'Noto Sans KR',sans-serif;}
.brand p{font-size:.68rem;margin:.25rem 0 0;opacity:.67;letter-spacing:.08em;}
.top-title{display:flex;align-items:center;gap:14px;margin-bottom:1.1rem;padding:1.2rem 1.6rem;border-radius:14px;background:rgba(255,255,255,.65);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.8);color:var(--pd);box-shadow:inset 0 1px 0 rgba(255,255,255,.5),0 8px 24px rgba(0,0,0,.1);position:relative;z-index:60;}
.top-title::before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,255,255,.3),rgba(255,255,255,.08));border-radius:14px;pointer-events:none;z-index:-1;}
.top-title img{width:auto;max-width:68px;height:68px;object-fit:contain;margin-right:8px;filter:drop-shadow(0 2px 4px rgba(0,0,0,.1));}
.top-title h2{font-size:1.5rem;margin:0;font-weight:800;letter-spacing:-.01em;font-family:'Noto Sans KR',sans-serif;color:var(--pd);line-height:1.1;}
.top-title p{margin:.25rem 0 0;font-size:.8rem;opacity:.9;color:rgba(0,0,0,.6);}

/* Landing title style (large, but refined spacing) */
.landing-title{font-family:'Noto Sans KR',sans-serif;font-weight:900;font-size:3.2rem;letter-spacing:-.02em;margin:0;padding:0;line-height:1.02;color:#0f2730;text-transform:none}
.landing-sub{color:#6b7575;margin-top:.6rem}
.panel{background:rgba(255,255,255,.68);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.8);border-radius:14px;box-shadow:inset 0 1px 0 rgba(255,255,255,.5),0 8px 24px rgba(0,0,0,.12);padding:1.8rem 1.6rem;margin:1.6rem 0;position:relative;z-index:1;}
.section-head{font-size:1rem;font-weight:900;color:var(--pd);padding-left:.6rem;border-left:4px solid var(--p);margin:.2rem 0 .9rem;}
.stButton>button{min-height:3.1rem;border-radius:8px;border:1px solid rgba(0,0,0,.08)!important;background:linear-gradient(135deg,var(--p),var(--pd))!important;color:white!important;font-weight:900;box-shadow:0 4px 12px rgba(0,0,0,.15)!important;transition:.15s ease!important;padding:.6rem 1rem!important;position:relative;z-index:10;}
.stButton>button:hover{filter:brightness(1.08);transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,.2)!important;}
.stButton>button:active{transform:translateY(0);box-shadow:0 2px 8px rgba(0,0,0,.1)!important;}
/* Prevent button wrapper from causing overlap */
.stButton{z-index:10;position:relative;margin:.5rem 0;}
/* Ensure buttons inside panels/cards are opaque and visible */
.panel .stButton>button, .block-container .stButton>button, section[data-testid="stSidebar"] .stButton>button {background:linear-gradient(135deg,var(--p),var(--pd))!important;color:white!important;border:1px solid rgba(0,0,0,.08)!important;box-shadow:0 4px 12px rgba(0,0,0,.15)!important}
/* Force opaque themed buttons immediately following card panels (landing page selection buttons) */
.panel + .stButton>button, .panel ~ .stButton>button, .stColumns .stButton>button {background:linear-gradient(135deg,var(--p),var(--pd))!important;color:white!important;opacity:1!important;border:1px solid rgba(0,0,0,.08)!important;box-shadow:0 4px 12px rgba(0,0,0,.15)!important}
/* Strong fallback to prevent Streamlit theme from making buttons transparent */
.stButton>button, .stButton>button * {background-image:none!important;background-color:var(--pd)!important;background:linear-gradient(135deg,var(--p),var(--pd))!important;color:white!important;opacity:1!important}
.stTabs [data-baseweb="tab-list"]{gap:6px;background:rgba(255,255,255,.5);padding:6px;border-radius:10px;border:1px solid rgba(255,255,255,.7);box-shadow:inset 0 1px 2px rgba(255,255,255,.5);}
.stTabs [data-baseweb="tab"]{height:44px;border-radius:8px;font-weight:800;color:rgba(0,0,0,.7);background:transparent;transition:.15s;}
.stTabs [aria-selected="true"]{background:rgba(255,255,255,.8)!important;color:var(--pd)!important;border-bottom:none!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.6),0 2px 8px rgba(0,0,0,.06)!important;}
div[data-testid="stMetric"]{background:rgba(255,255,255,.68);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.8);border-top:4px solid var(--p);border-radius:12px;padding:1.2rem;box-shadow:inset 0 1px 0 rgba(255,255,255,.5),0 6px 16px rgba(0,0,0,.08);min-width:160px;}
/* Ensure metric labels/values are visible and not clipped */
div[data-testid="stMetric"] div[data-testid="stMetricLabel"]{font-weight:900;color:#22343a!important;font-family:'Noto Sans KR',sans-serif;font-size:.9rem;opacity:1!important;letter-spacing:.06em;text-transform:capitalize;margin-bottom:.3rem}
div[data-testid="stMetric"] div[data-testid="stMetricValue"]{font-weight:900;color:#0f2730!important;font-family:'Noto Sans KR',sans-serif;letter-spacing:-.02em;white-space:normal;overflow-wrap:anywhere;word-break:break-word;text-overflow:clip;font-size:1.25rem;}
@media(max-width:900px){div[data-testid="stMetric"] div[data-testid="stMetricValue"]{font-size:1.1rem;}}
div[data-baseweb="input"],div[data-baseweb="select"]>div{border-radius:8px!important;background:rgba(255,255,255,.9)!important;border:1px solid rgba(200,200,200,.5)!important;box-shadow:inset 0 1px 2px rgba(255,255,255,.8)!important;}
[data-testid="stDataFrame"]{border-radius:10px;overflow:hidden;border:1px solid rgba(255,255,255,.4);}
.summary-banner{display:flex;justify-content:space-between;align-items:end;padding:1.4rem 1.8rem;border-radius:14px;background:rgba(255,255,255,.68);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.8);color:var(--pd);box-shadow:inset 0 1px 0 rgba(255,255,255,.5),0 8px 24px rgba(0,0,0,.12);position:relative;}
.summary-banner::before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,255,255,.3),rgba(255,255,255,.08));border-radius:14px;pointer-events:none;z-index:-1;}
.summary-banner small{font-weight:800;letter-spacing:.14em;opacity:1;color:var(--p);} .summary-banner strong{font-size:2.2rem;font-weight:900;letter-spacing:-.05em;color:var(--pd);}
.mini-card{background:rgba(255,255,255,.65);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.8);border-radius:12px;padding:1.2rem;min-height:128px;box-shadow:inset 0 1px 0 rgba(255,255,255,.5),0 6px 16px rgba(0,0,0,.08);position:relative;transition:.2s;}
.mini-card::before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,255,255,.25),rgba(255,255,255,.08));border-radius:12px;pointer-events:none;z-index:-1;}
.mini-card:hover{transform:translateY(-4px);box-shadow:0 10px 28px rgba(0,0,0,.1);}
.mini-card small{font-weight:900;color:var(--p);letter-spacing:.1em;font-size:.75rem;} .mini-card b{display:block;font-size:1.4rem;color:var(--pd);margin:.6rem 0 .4rem;font-weight:900;}
.nav-label{font-size:.72rem;letter-spacing:.12em;font-weight:900;opacity:.6;margin-top:.4rem;}
@media(max-width:800px){.stApp{background-size:auto 100%%;} .block-container{padding:6.4rem .8rem 4rem;} .top-title{padding:1rem} .top-title img{max-width:54px;height:54px;}}
</style>
""" % (service.primary, service.primary_dark, service.primary_soft, service.border, logo, bg)
    st.markdown(css, unsafe_allow_html=True)


def landing():
    # 첫 화면은 육군 계열 중립 프레임으로 표시
    service = SERVICES["육군"]
    inject_css(service)
    st.markdown("<div class='panel' style='max-width:920px;margin:3rem auto 1.5rem;text-align:center;padding:2.2rem'><div style='font-size:.72rem;letter-spacing:.22em;font-weight:900;color:#52631f'>MILITARY FINANCIAL READINESS SYSTEM</div><h1 class='landing-title'>헌신의 대가</h1><p class='landing-sub' style='font-size:1rem;color:#67716a'>군종을 선택하면 해당 군종의 공식 로고와 전용 프레임을 적용한 전역 자금 계산 화면으로 진입합니다.</p></div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (key, s) in zip(cols, SERVICES.items()):
        with col:
            logo = data_uri(ASSETS / s.logo_file)
            st.markdown(f"<div class='panel' style='text-align:center;min-height:260px;border-top:6px solid {s.primary}'><img src='{logo}' style='width:118px;height:118px;object-fit:contain'><h3 style='margin:.5rem 0 .2rem'>{s.name}</h3><div style='font-size:.68rem;color:#77808a'>{s.english}</div><div style='font-size:.8rem;margin-top:.8rem'>{s.months}개월 복무 기준</div></div>", unsafe_allow_html=True)
            if st.button(f"{key} 선택", key=f"select_{key}", use_container_width=True):
                st.session_state.service = key
                st.rerun()


def dashboard(service_key: str):
    s = SERVICES[service_key]
    inject_css(s)
    logo = data_uri(ASSETS / s.logo_file)

    default_enlist = date.today() - relativedelta(months=3)
    with st.sidebar:
        st.markdown(f"<div class='brand'><img src='{logo}'><div><h1>{s.name}</h1><p>{s.english}</p></div></div>", unsafe_allow_html=True)
        st.markdown("<div class='nav-label'>CALCULATION CONTROL</div>", unsafe_allow_html=True)
        if st.button("← 군종 다시 선택", use_container_width=True):
            st.session_state.service = None
            st.rerun()
        st.markdown("### 기본 정보")
        enlistment = st.date_input("입영일", default_enlist)
        auto = st.toggle("전역일 자동 계산", True)
        auto_discharge = calc_discharge_date(enlistment, s.months)
        discharge = auto_discharge if auto else st.date_input("전역일", auto_discharge, min_value=enlistment)
        if auto:
            st.caption(f"전역 예정일 · {discharge:%Y.%m.%d}")
        daily_unit = 10 if st.radio("일급 절사 방식", ["10원 단위 절사", "1원 단위 절사"], horizontal=True) == "10원 단위 절사" else 1

        with st.expander("계급별 월 봉급"):
            salaries = {rank: st.number_input(rank, 0, 3_000_000, salary, 10_000, key=f"salary_{rank}") for rank, salary in DEFAULT_SALARY.items()}

        st.markdown("### 적금 설정")
        s1 = st.number_input("적금 1 월 납입액", 0, 300_000, 300_000, 10_000)
        r1 = st.number_input("적금 1 연이율(%)", 0.0, 20.0, 5.0, 0.1)
        d1 = st.number_input("적금 1 납입일", 1, 31, min(enlistment.day, 28))
        s2 = st.number_input("적금 2 월 납입액", 0, 300_000, 250_000, 10_000)
        r2 = st.number_input("적금 2 연이율(%)", 0.0, 20.0, 5.0, 0.1)
        d2 = st.number_input("적금 2 납입일", 1, 31, min(enlistment.day, 28))
        method = st.radio("이자 계산", ["월수 기준 단리", "실제 예치일수 ÷ 365"], horizontal=False)
        matching_rate = st.slider("매칭지원금 비율", 0, 200, 100, 1, format="%d%%")

    if s1 + s2 > 550_000:
        st.error("월 적금 합계는 550,000원을 초과할 수 없습니다.")
        st.stop()

    salary_df = salary_ledger(enlistment, discharge, salaries, daily_unit)
    sav1 = savings_ledger(enlistment, discharge, s1, r1, int(d1), method)
    sav2 = savings_ledger(enlistment, discharge, s2, r2, int(d2), method)
    salary_sum = total(salary_df, "지급 봉급")
    principal = total(sav1, "납입원금") + total(sav2, "납입원금")
    interest = total(sav1, "예상이자") + total(sav2, "예상이자")
    matching = (principal * D(matching_rate) / D(100)).quantize(D("1"), rounding=ROUND_DOWN)
    spendable = salary_sum - principal
    final_asset = spendable + principal + interest + matching
    discharge_month = salary_df[salary_df["지급월"] == f"{discharge.year}-{discharge.month:02d}"]
    discharge_pay = D(int(discharge_month["지급 봉급"].sum()))

    st.markdown(f"<div class='top-title'><img src='{logo}'><div><h2>{s.name} · 헌신의 대가</h2><p>{s.motto} · {enlistment:%Y.%m.%d} — {discharge:%Y.%m.%d}</p></div></div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'><div class='section-head'>전역 자금 계산기</div><div style='font-size:.8rem;color:#6f7880'>급여 일할계산, 적금 원금, 단리 이자와 매칭지원금을 원 단위로 산출합니다.</div></div>", unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("예상 전역 자산", won(final_asset))
    c2.metric("누적 봉급", won(salary_sum))
    c3.metric("적금 원금", won(principal))
    c4.metric("적금 이자", won(interest))
    c5.metric("매칭지원금", won(matching))

    st.markdown(f"<div class='summary-banner'><div><small>PROJECTED DISCHARGE ASSET</small><div style='margin-top:.3rem'>전역 시점 예상 누적 자산</div></div><strong>{won(final_asset)}</strong></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-head' style='margin-top:1.5rem'>운용 지표</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    items = [
        ("SERVICE DAYS", f"{(discharge-enlistment).days+1:,}일", "입영일부터 전역일까지"),
        ("DISCHARGE PAY", won(discharge_pay), f"전역월 {discharge.day}일까지"),
        ("MONTHLY SAVING", won(s1+s2), "두 적금 월 납입액 합계"),
        ("AVAILABLE PAY", won(spendable), "봉급에서 적금 원금 차감"),
    ]
    for col, (label, value, desc) in zip(cols, items):
        with col:
            st.markdown(f"<div class='mini-card'><small>{label}</small><b>{value}</b><span style='font-size:.75rem;color:#747d84'>{desc}</span></div>", unsafe_allow_html=True)

    tabs = st.tabs(["봉급 상세", "적금 1", "적금 2", "최종 산식"])
    with tabs[0]:
        st.dataframe(salary_df.style.format({"월 봉급":"{:,.0f}원","계산 일급":"{:,.0f}원","지급 봉급":"{:,.0f}원"}), use_container_width=True, hide_index=True)
        st.caption(f"월 봉급 ÷ 해당 월 일수 후 {daily_unit}원 단위 미만 절사 × 실제 복무일수")
    with tabs[1]:
        st.dataframe(sav1.style.format({"납입원금":"{:,.0f}원","예상이자":"{:,.0f}원"}), use_container_width=True, hide_index=True)
    with tabs[2]:
        st.dataframe(sav2.style.format({"납입원금":"{:,.0f}원","예상이자":"{:,.0f}원"}), use_container_width=True, hide_index=True)
    with tabs[3]:
        summary = pd.DataFrame({
            "항목":["누적 봉급","적금 원금","적금 단리이자","매칭지원금","복무 중 사용 가능액","최종 자산"],
            "금액":[int(salary_sum),int(principal),int(interest),int(matching),int(spendable),int(final_asset)],
            "계산 기준":["월별·계급별 일할계산","실제 납입 회차 합계",method,f"원금 × {matching_rate}%","봉급 - 적금 원금","사용 가능액 + 원금 + 이자 + 지원금"],
        })
        st.dataframe(summary.style.format({"금액":"{:,.0f}원"}), use_container_width=True, hide_index=True)
        st.info("표시는 1원 단위입니다. 실제 은행 정산액은 영업일 처리와 상품 약관의 절사 규칙에 따라 차이가 날 수 있습니다.")


if "service" not in st.session_state:
    st.session_state.service = None

if st.session_state.service is None:
    landing()
else:
    dashboard(st.session_state.service)
