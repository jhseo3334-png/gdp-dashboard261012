from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

@st.cache_data
def read_csv_contents(contents: bytes) -> pd.DataFrame:
    try:
        return pd.read_csv(BytesIO(contents))
    except UnicodeDecodeError:
        return pd.read_csv(BytesIO(contents), encoding="cp949")


st.set_page_config(page_title="학생 성적 분석", page_icon="📊", layout="wide")
st.title("학생 성적 분석")

uploaded_file = st.file_uploader("분석할 CSV 파일", type="csv")

try:
    if uploaded_file is not None:
        csv_contents = uploaded_file.getvalue()
        data = read_csv_contents(csv_contents)
        st.session_state["uploaded_csv_contents"] = csv_contents
        st.session_state["uploaded_csv_name"] = uploaded_file.name
    elif st.session_state.get("uploaded_csv_contents"):
        data = read_csv_contents(st.session_state["uploaded_csv_contents"])
        st.caption(f"현재 분석 파일: {st.session_state.get('uploaded_csv_name', 'CSV')}")
    else:
        st.info("CSV 파일을 업로드해 분석을 시작하세요.")
        st.stop()
except (UnicodeDecodeError, pd.errors.EmptyDataError, pd.errors.ParserError) as error:
    st.error(f"CSV 파일을 읽지 못했습니다: {error}")
    st.stop()

if st.button("업로드한 데이터 지우기"):
    st.session_state.pop("uploaded_csv_contents", None)
    st.session_state.pop("uploaded_csv_name", None)
    st.rerun()

if data.empty:
    st.warning("업로드한 CSV에 분석할 데이터가 없습니다.")
    st.stop()

numeric_columns = data.select_dtypes(include="number").columns.tolist()
category_columns = [
    column
    for column in data.columns
    if (
        pd.api.types.is_object_dtype(data[column])
        or pd.api.types.is_string_dtype(data[column])
        or isinstance(data[column].dtype, pd.CategoricalDtype)
        or pd.api.types.is_bool_dtype(data[column])
    )
]

if not numeric_columns:
    st.warning("기술 통계를 계산할 숫자형 열이 없습니다.")
    st.stop()

default_scores = [
    column for column in ("math score", "reading score") if column in numeric_columns
]
default_group = category_columns[0] if category_columns else None

with st.sidebar:
    st.header("분석 설정")
    selected_scores = st.multiselect(
        "점수 변수",
        numeric_columns,
        default=default_scores or numeric_columns[:2],
    )
    if category_columns:
        group_column = st.selectbox(
            "그룹 비교 변수",
            options=category_columns,
            index=category_columns.index(default_group) if default_group else 0,
        )
        color_options = ["구분 없음"] + [
            column for column in category_columns if column != group_column
        ]
        color_selection = st.selectbox("추가 구분 변수", color_options)
        color_column = None if color_selection == "구분 없음" else color_selection
    else:
        group_column = None
        color_column = None

if not selected_scores:
    st.info("점수 변수에서 하나 이상의 숫자형 열을 선택하세요.")
    st.stop()

st.subheader("기술 통계")
st.dataframe(data[selected_scores].describe().round(2).T, use_container_width=True)

st.subheader("점수 분포와 그룹 평균")
for score_column in selected_scores:
    st.markdown(f"#### {score_column}")
    chart_columns = st.columns(2)

    if group_column:
        box_figure = px.box(
            data,
            x=group_column,
            y=score_column,
            color=color_column,
            points="outliers",
            title=f"{score_column}: 그룹별 점수 분포",
        )
        group_keys = [group_column] + ([color_column] if color_column else [])
        means = data.groupby(group_keys, dropna=False)[score_column].mean().reset_index()
        mean_figure = px.bar(
            means,
            x=group_column,
            y=score_column,
            color=color_column,
            barmode="group",
            title=f"{score_column}: 그룹별 평균",
        )
        chart_columns[0].plotly_chart(box_figure, use_container_width=True)
        chart_columns[1].plotly_chart(mean_figure, use_container_width=True)
    else:
        histogram = px.histogram(data, x=score_column, title=f"{score_column}: 점수 분포")
        box_figure = px.box(data, x=score_column, title=f"{score_column}: 상자그림")
        chart_columns[0].plotly_chart(histogram, use_container_width=True)
        chart_columns[1].plotly_chart(box_figure, use_container_width=True)