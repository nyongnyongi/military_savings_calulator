import streamlit as st

def calculate_compound_savings(service_type, s1, r1, s2, r2):
    # 군종별 복무 기간
    periods = {"공군(21개월)": [2, 6, 6, 7], "육군/해병대(18개월)": [2, 6, 6, 4], "해군(20개월)": [2, 6, 6, 6]}
    salaries = [75, 90, 120, 150]
    current_periods = periods[service_type]
    total_months = sum(current_periods)
    
    # 각 적금별 월 이율 계산
    m_rate1 = (r1 / 100) / 12
    m_rate2 = (r2 / 100) / 12
    
    # 1. 적금별 복리 만기 금액 계산 (함수 내 로직 분리)
    def get_final_deposit(principal, m_rate, months):
        if m_rate > 0:
           return principal * (((1 + m_rate)**months - 1) / m_rate) * (1 + m_rate)
        return principal * months

    final_s1 = get_final_deposit(s1, m_rate1, total_months)
    final_s2 = get_final_deposit(s2, m_rate2, total_months)
    
    total_deposit_with_interest = final_s1 + final_s2
    total_deposit_principal = (s1 + s2) * total_months
    total_interest = total_deposit_with_interest - total_deposit_principal
    
    # 2. 실 수령 월급 (월급 - 적금합계)
    total_salary_only = 0
    monthly_deposit_total = s1 + s2
    for rank_idx, duration in enumerate(current_periods):
        total_salary_only += (salaries[rank_idx] - monthly_deposit_total) * duration
        
    # 3. 매칭 지원금
    matching_fund = total_deposit_principal
    
    return {
        "실수령 월급 합계": int(total_salary_only),
        "적금 원금": int(total_deposit_principal),
        "복리 이자": int(total_interest),
        "매칭 지원금": int(matching_fund),
        "최종 자산": int(total_salary_only + total_deposit_with_interest + matching_fund)
    }

st.title("🪖 군 전역 자금 시뮬레이터 ")

with st.sidebar:
    st.header("⚙️ 설정")
    service = st.selectbox("군종", ["공군(21개월)", "육군/해병대(18개월)", "해군(20개월)"])
    
    st.subheader("💰 적금 1")
    s1 = st.number_input("납입액 (만원)", 0, 30, 30, key="s1")
    r1 = st.slider("금리 (%)", 0.0, 10.0, 5.0, step=0.1, key="r1")

    
    st.subheader("💰 적금 2")
    s2 = st.number_input("납입액 (만원)", 0, 30, 25, key="s2")
    r2 = st.slider("금리 (%)", 0.0, 10.0, 5.0, step=0.1, key="r2")

if s1 + s2 <= 55:
    # 수정된 함수 호출 (인자 5개)
    data = calculate_compound_savings(service, s1, r1, s2, r2)
    
    c1, c2 = st.columns(2)
    c1.metric("최종 수령액", f"{data['최종 자산']:,} 만원")
    c2.metric("순수 이자(복리 합산)", f"{data['복리 이자']:,} 만원")

    st.write("### 📝 세부 내역")
    st.table({
        "구분": ["월급(적금제외)", "적금 원금", "복리 이자", "매칭 지원금"],
        "금액": [f"{data['실수령 월급 합계']:,} 만원", 
                f"{data['적금 원금']:,} 만원", 
                f"{data['복리 이자']:,} 만원", 
                f"{data['매칭 지원금']:,} 만원"]
    })
else:
    st.error("적금 합계는 55만원을 넘을 수 없습니다.")