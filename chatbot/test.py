import streamlit as st
import pandas as pd

st.title('메인보드에 위치한 필터 예시')

st.set_page_config(
    page_title="와이드 모드 필터 예시",
    layout="wide"  # 여기를 'wide'로 설정
)

# 예시 데이터프레임 생성
data = {
    '카테고리': ['과일', '채소', '과일', '채소', '음료', '음료', '과일'],
    '상품': ['사과', '당근', '바나나', '양파', '콜라', '사이다', '포도'],
    '제조사': ['A', 'B', 'A', 'C', 'B', 'A', 'C'],
    '가격': [1000, 500, 1500, 700, 2000, 1800, 2500]
}
df = pd.DataFrame(data)

st.title('🛒 와이드 모드 필터 예시')

# st.columns를 사용해 필터가 들어갈 공간을 1:1:1 비율로 나누고,
# 이를 전체 너비에 맞추기 위해 'use_container_width=True'를 사용합니다.
# 필터 3개를 좁게 배치하려면 st.columns([1, 1, 1]) 대신
# 다른 위젯과 함께 배치하거나, 더 많은 컬럼을 만들고 일부만 사용해 조절할 수 있습니다.
col1, col2, col3, _ = st.columns([0.5, 0.5, 0.5, 2]) # 3개의 필터에 작은 공간을 할당하고 나머지는 비워둡니다.

with col1:
    selected_category = st.selectbox(
        '카테고리:',
        options=['모두'] + list(df['카테고리'].unique())
    )

with col2:
    selected_manufacturer = st.selectbox(
        '제조사:',
        options=['모두'] + list(df['제조사'].unique())
    )
    
with col3:
    min_price, max_price = st.slider(
        '가격:',
        min_value=0, max_value=3000, value=(0, 3000)
    )

# 필터링 로직
filtered_df = df.copy()

if selected_category != '모두':
    filtered_df = filtered_df[filtered_df['카테고리'] == selected_category]

if selected_manufacturer != '모두':
    filtered_df = filtered_df[filtered_df['제조사'] == selected_manufacturer]

filtered_df = filtered_df[(filtered_df['가격'] >= min_price) & (filtered_df['가격'] <= max_price)]

st.write("---")

st.subheader("필터링된 데이터")
st.dataframe(filtered_df, use_container_width=True)