import os
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from anthropic import Anthropic

DATA_FILE = Path(__file__).parent / "StudentsPerformance.csv"
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")


@st.cache_data(ttl=86400, show_spinner=False)
def generate_data_description(csv_contents: bytes, model: str, api_key: str) -> str:
    data = pd.read_csv(BytesIO(csv_contents))
    score_columns = ["math score", "reading score", "writing score"]
    score_summary = data[score_columns].describe().round(1).to_string()
    group_summary = (
        data.groupby(["race/ethnicity", "gender"])[["math score", "reading score"]]
        .mean()
        .round(1)
        .to_string()
    )

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=250,
        system=(
            "당신은 교육 데이터 분석가입니다. 제공된 집계 수치만 근거로 한국어로 "
            "학생 성적 데이터의 특징을 3문장 이내로 간략히 설명하세요. "
            "상관관계를 인과관계로 단정하지 마세요."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"행 수: {len(data)}\n\n점수 기술 통계:\n{score_summary}\n\n"
                    f"인종/민족 및 성별별 수학·읽기 평균:\n{group_summary}"
                ),
            }
        ],
    )
    return "\n".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )


def get_api_key() -> str | None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    secrets_file = Path(__file__).parent / ".streamlit" / "secrets.toml"
    if not api_key and secrets_file.exists():
        api_key = st.secrets.get("ANTHROPIC_API_KEY")
    return api_key


st.set_page_config(page_title="학생 성적 데이터 설명", page_icon="📚")

if not DATA_FILE.exists():
    st.error("프로젝트 루트에서 StudentsPerformance.csv 파일을 찾을 수 없습니다.")
else:
    api_key = get_api_key()
    if not api_key:
        st.info("AI 설명을 보려면 ANTHROPIC_API_KEY를 Codespaces 환경 변수 또는 .streamlit/secrets.toml에 설정하세요.")
    else:
        try:
            description = generate_data_description(DATA_FILE.read_bytes(), MODEL, api_key)
            st.markdown(description)
        except Exception:
            st.error("AI 설명을 생성하지 못했습니다. API 키와 모델 설정을 확인해 주세요.")
