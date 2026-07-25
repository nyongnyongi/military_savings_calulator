# 헌신의 대가 (Military Financial Readiness System)

A comprehensive military salary and savings calculation system for South Korean military service personnel, calculating discharge assets based on rank progression, daily salary rates, and matching support funds.

## Tech Stack

### Languages & Frameworks
- **Python 3.14**: Core programming language
- **Streamlit**: Web application framework for rapid UI development
- **Pandas**: Data manipulation and tabular calculations
- **Python Decimal**: High-precision financial calculations (prevents floating-point errors)
- **dateutil.relativedelta**: Date arithmetic for military service periods
- **Base64**: Image encoding for embedded assets

### Key Libraries
```
streamlit>=1.28.0
pandas>=2.0.0
python-dateutil>=2.8.2
```

## AI & Development

**Developed with Claude Haiku 4.5** (Anthropic)
- Entire application architecture and logic
- Python financial calculation algorithms
- Streamlit UI/UX components
- CSS styling for military-themed design
- Multi-language support (Korean/English)

## Features

**Rank-Based Salary Calculation**: Automatic progression through 4 military ranks (이병 → 일병 → 상병 → 병장)
**Precise Daily Rate Calculation**: Truncated daily rates to prevent discrepancies
**Multiple Savings Products**: Support for 2 concurrent savings accounts with configurable rates and payment days
**Matching Support Fund**: Government matching contributions calculation
**Service Branch Themes**: Dedicated UI themes for Army (육군), Navy (해군), Air Force (공군), Marines (해병대)
**Detailed Ledgers**: Salary ledger, savings ledger, and comprehensive final asset breakdown
**Custom Rank Salaries**: Adjustable salary per rank and truncation unit

## Current Issues & Limitations

### UI/UX Issues
- ⚠️ CSS transparency levels required multiple iterations to balance background visibility with text readability
- ⚠️ Button overlap issues encountered during sidebar interactions (partially resolved with z-index adjustments)
- ⚠️ Streamlit CSS injection limitations make consistent cross-component styling challenging
- ⚠️ Responsive design needs improvement for mobile/tablet views

### Technical Issues
- ⚠️ Streamlit page caching can cause stale CSS on refresh (requires manual cache clear or full server restart)
- ⚠️ Limited control over Streamlit's default component styling (backdrop-filter and advanced CSS features have inconsistent support)
- ⚠️ Tab styling limitations with Streamlit's built-in components
- ⚠️ Sidebar button layout can appear overcrowded on smaller screens

### Known Bugs
- Asset images must remain in `assets/` folder; relative path dependencies may cause issues if file structure changes
- Date input validation could be more granular
- Interest calculation precision depends on bank rounding rules (disclaimer included in app)

## Installation & Usage

### Prerequisites
```bash
Python 3.8 or higher
```

### Setup
```bash
pip install -r requirements.txt
```

### Run
```bash
streamlit run app.py
```

The app will start at `http://localhost:8501` by default. If this port is already in use, Streamlit will automatically use the next available port (8502, 8503, etc.). Check the terminal output for the actual URL:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501 (or the next available port)
Network URL: http://192.168.x.x:8501
```

### File Structure
```
.
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── README.md             # This file
└── assets/               # Military branch assets (must not move)
    ├── army_bg.png
    ├── army_logo.png
    ├── navy_bg.png
    ├── navy_logo.png
    ├── airforce_bg.png
    ├── airforce_logo.png
    ├── marines_bg.png
    └── marines_logo.png
```

---

# 헌신의 대가 (군 전역 자금 계산 시스템)

대한민국 국군 현역 복무자를 위한 전역 자산 종합 계산 시스템입니다. 계급 진급에 따른 봉급, 일일 급여 누적액, 정부 매칭 지원금을 기반으로 전역 시점의 예상 자산 합계를 계산합니다.

## 기술 스택

### 언어 및 프레임워크
- **Python 3.13**: 핵심 프로그래밍 언어
- **Streamlit**: 빠른 웹 애플리케이션 개발 프레임워크
- **Pandas**: 데이터 조작 및 표형식 계산
- **Python Decimal**: 고정밀 금융 계산 (부동소수점 오류 방지)
- **dateutil.relativedelta**: 군 복무 기간 날짜 산술
- **Base64**: 자산 이미지 임베딩 인코딩

### 주요 라이브러리
```
streamlit>=1.28.0
pandas>=2.0.0
python-dateutil>=2.8.2
```

## AI 및 개발

**Claude Haiku 4.5** (Anthropic)로 개발
- 전체 애플리케이션 아키텍처 및 로직
- Python 금융 계산 알고리즘
- Streamlit UI/UX 컴포넌트
- 군 테마 CSS 스타일링
- 다국어 지원 (한국어/영어)

## 주요 기능

✅ **계급별 봉급 계산**: 4개 계급 자동 진급 (이병 → 일병 → 상병 → 병장)
✅ **정확한 일일 급여 계산**: 일할계산된 일급으로 오차 방지
✅ **다중 적금 상품**: 서로 다른 이율과 납입일의 2개 적금 동시 지원
✅ **정부 매칭 지원금**: 정부 매칭 지원금 자동 계산
✅ **군종별 테마**: 육군, 해군, 공군, 해병대 각각의 맞춤형 UI
✅ **상세 장부**: 봉급 내역서, 적금 내역서, 최종 자산 산식 표시
✅ **커스텀 계급 봉급**: 계급별 봉급 및 절사 단위 조정 가능

## 현재 문제점 및 제한사항

### UI/UX 문제
- ⚠️ CSS 투명도 레벨 조정: 배경 표시와 텍스트 가독성 균형을 위해 여러 번 반복 조정
- ⚠️ 버튼 겹침 이슈: 사이드바 인터랙션 중 버튼이 겹쳐 보이는 현상 (z-index 조정으로 부분 해결)
- ⚠️ Streamlit CSS 주입 제한: 컴포넌트 간 일관된 스타일링 적용 어려움
- ⚠️ 반응형 디자인: 모바일/태블릿 뷰에서 개선 필요

### 기술적 문제
- ⚠️ Streamlit 캐싱: 새로고침 시 기존 CSS가 유지될 수 있음 (수동 캐시 삭제 또는 서버 재시작 필요)
- ⚠️ Streamlit 컴포넌트 스타일 제한: backdrop-filter, 고급 CSS 기능 지원 불일치
- ⚠️ 탭 스타일링 제한: Streamlit 기본 컴포넌트의 스타일 커스터마이제이션 제약
- ⚠️ 사이드바 버튼 레이아웃: 작은 화면에서 버튼이 과밀화될 수 있음

### 알려진 버그
- 자산 이미지는 반드시 `assets/` 폴더에 유지해야 함 (파일 구조 변경 시 경로 오류 발생 가능)
- 날짜 입력 검증이 더 세분화될 수 있음
- 이자 계산 정확도는 은행의 반올림 규칙에 따라 차이 발생 가능 (앱에 면책조항 포함)

## 설치 및 사용법

### 필수 요구사항
```bash
Python 3.8 이상
```

### 설치
```bash
pip install -r requirements.txt
```

### 실행
```bash
streamlit run app.py
```

기본적으로 앱이 `http://localhost:8501`에서 시작됩니다. 해당 포트가 이미 사용 중이면 Streamlit이 자동으로 다음 사용 가능한 포트(8502, 8503 등)를 사용합니다. 터미널 출력에서 실제 URL을 확인하세요:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501 (또는 다음 사용 가능한 포트)
Network URL: http://192.168.x.x:8501
```

### 파일 구조
```
.
├── app.py                 # 메인 애플리케이션
├── requirements.txt       # 의존성
├── README.md             # 이 파일
└── assets/               # 군종 자산 (이동 금지)
    ├── army_bg.png
    ├── army_logo.png
    ├── navy_bg.png
    ├── navy_logo.png
    ├── airforce_bg.png
    ├── airforce_logo.png
    ├── marines_bg.png
    └── marines_logo.png
```
