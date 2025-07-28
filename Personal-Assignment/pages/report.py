import streamlit as st
from assignment1 import save_csv
import logging
# import seaborn as sb
import pandas as pd
from plotly import graph_objects as go

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="서브 페이지: 리포트 출력",
    layout="wide", # 넓은 레이아웃으로 설정 가능
    initial_sidebar_state="expanded" # 사이드바를 펼쳐진 상태로 시작
)

visible_sidebar_css = """
<style>
    .stSidebar {
        display: block;
    }
</style>
"""

center_aligned_css = """
<style>
    table {
        width : 100%;
    }
    th {
        text-align: center !important;
    }
    td {
        text-align: center !important;
    }
    .dataframe > thead > tr > th:nth-child(2) {
        width : 100px;
    }
    .dataframe > tbody > tr > td:nth-child(1) {
        width : 100px;
    }



</style>
"""
st.markdown(center_aligned_css, unsafe_allow_html=True)
st.markdown(visible_sidebar_css, unsafe_allow_html=True)

# 제목 설정
st.markdown("<h2>리포트</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

for_sale_list = st.session_state.get('for_sale_data', []) # 기본값으로 빈 리스트 지정

# if for_sale_list:
#     st.subheader("검색된 매물 목록:")
#     # 여기에 for_sale_list를 표, 리스트 등으로 표시하는 로직 추가
#     for i, item in enumerate(for_sale_list):
#         st.write(f"**매물 {i+1}:** {item}")
#         # 예시: item이 딕셔너리라면 item['이름'], item['가격'] 등으로 접근
# else:
#     st.warning("표시할 매물 데이터가 없습니다. 메인 페이지에서 먼저 검색을 해주세요.")

st.markdown("---")

df = pd.DataFrame(for_sale_list)
df.columns = ["번호", "거래 유형", "매물명", "매물가","면적", "URL", "수집시간"]
# styled_df = df.style.set_properties(**{'text-align': 'center'})
# styled_df = df.style.set_properties(**{'text-align': 'center'}).hide(axis="index")
# df_reset = df.reset_index(drop=True)
# styled_df = df_reset.style.hide(axis="index").set_properties(**{'text-align': 'center'})
# st.dataframe(styled_df, use_container_width=True)
# st.text(df.to_string(index=False))
# name = [name['item_name'] for name in for_sale_list]
# price = [price['item_price'] for price in for_sale_list]
df_filtered = df.drop(columns=['번호'])

df_reset = df_filtered.reset_index(drop=True)
df_reset.index = df_reset.index + 1 
df_reset['면적'] = df_reset['면적'].astype(int)

# URL을 클릭 가능한 링크로 변환하는 함수
def make_url(url):
    return f'<a href="{url}" target="_blank">링크</a>'


styled_df = df_reset.style.format({
    '매물가': "{:,.0f}만원",
    '면적': "{:,.0f}㎡",
    'URL' : make_url
})

# Streamlit에서 스타일링된 DataFrame 출력 (인덱스 숨기기)
# st.dataframe(styled_df, use_container_width=True)

# st.dataframe(df_reset, use_container_width=True)

# DataFrame을 HTML로 변환하고 스타일을 적용
styled_html = styled_df.to_html(classes=['dataframe'], justify='center')

# HTML을 Streamlit에 렌더링
st.markdown(styled_html, unsafe_allow_html=True)



# # x축과 y축에 해당하는 데이터를 각각 넣고 리스트로 감싸줌
# data = [go.Bar(x = name, y = price)]
# # 만들어놓은 데이터 전달
# fig = go.Figure(data = data)

# fig.update_layout(
#     xaxis_title="매물 이름",
#     yaxis_title="가격 (만원)",
#     yaxis=dict(
#         tickformat=',',  # 천 단위 구분 기호 추가
#         ticksuffix=' 만원'  # 가격 뒤에 '원' 추가
#     )
# )


# # 그래프 출력
# st.plotly_chart(fig)

if st.button("메인 페이지로 돌아가기"):
    # 메인 페이지로 돌아갈 때 필요하다면 세션 상태를 초기화할 수 있습니다.
    # del st.session_state['for_sale_data'] # 매물 데이터 초기화
    st.switch_page("streamlit_AI.py") # 메인 페이지 파일명으로 변경