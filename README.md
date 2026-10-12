# CSV 분석 앱

CSV 파일을 업로드해 기술 통계와 Plotly 그래프로 살펴보는 Streamlit 앱입니다. 메인 화면은 업로드한 데이터의 집계 통계를 사용해 생성형 AI 설명을 제공합니다.

분석하려는 CSV 파일을 **학생 성적 분석** 페이지에서 업로드하세요. 업로드한 파일은 현재 브라우저 세션에서만 사용되며, 앱은 저장소의 CSV를 기본 데이터로 불러오지 않습니다.

AI 설명을 사용하려면 Codespaces의 환경 변수 또는 Streamlit secrets에 `ANTHROPIC_API_KEY`를 설정해야 합니다. 키 없이도 데이터 분석 페이지의 기술 통계와 그래프를 사용할 수 있습니다.

### 실행 방법

1. 필요한 패키지를 설치합니다.

   ```bash
   python -m pip install -r requirements.txt
   ```

2. 앱을 실행합니다.

   ```bash
   python -m streamlit run streamlit_app.py
   ```
