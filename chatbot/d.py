# 필요한 라이브러리 import
import streamlit as st
import requests
import os
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client, Client
import datetime
import re

# 페이지 설정
st.set_page_config(page_title="소설 프롤로그 생성기", layout="centered")

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Supabase 클라이언트 초기화
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
st.write("supabase 연동 성공")

series = supabase.table('novel').select('title').execute()

# 'title' 값만 추출하여 리스트로 만듦
titles = [item['title'] for item in series.data]

# 중복 제거
unique_titles = list(set(titles))


# 사이드바 메뉴
st.sidebar.title("📚 메뉴")
menu = st.sidebar.radio("이동할 화면을 선택하세요", ["초기 세팅", "히스토리 확인", "다음 화 작성"])

# Gemini API Key 입력
gemini_api_key = st.sidebar.text_input(
    "🔑 Gemini API Key",
    type="password",
    help="Google AI Studio에서 발급받은 API 키를 입력해주세요."
)
model_choice = st.sidebar.selectbox(
    '🧠 사용할 모델:',
    ('gemini-1.5-flash', 'gemini-2.5-flash')
)

series_choice = st.sidebar.selectbox(
    '🧠 작품 선택:',
    unique_titles
)

# 모델 초기화
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel(model_choice)
    system_prompt = "당신은 초인기 소설 작가입니다."

# 세션 상태 초기화
defaults = {
    'history': [],
    'novel_genre': ["판타지"],
    'background_time': ["중세유럽"],
    'background_space': ["국가"],
    'background_social': ["제국주의"],
    'literary_style': ["서술성"],
    'theme': ["희망"],
    'main_character_background': ["빈곤"],
    'main_character_appearance': ["단발"],
    'main_character_ability': ["힘이 셈"],
    'main_character_superpower': ["검술"],
    'main_character_personality': ["낙천적인"],
    'main_character_relationship': ["스승"],
    'novel_title': '' # 소설 제목을 위한 변수 추가
}
for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

file_name = ""
novel_dir = ""
file_path = ""
st.session_state['button_name'] = "소설 1화 생성하기 "
st.session_state['button_name'] = "소설 1화 생성하기 "


def sanitize_filename(filename):
    """파일 이름으로 사용할 수 없는 문자를 제거하는 함수"""
    return re.sub(r'[\\/:*?"<>|]', '', filename)

# =============================
# 화면 1: 초기 세팅 및 생성 기능
# =============================
if menu == "초기 세팅":
    st.title("📖 AI 소설 프롤로그 생성기")
    st.markdown("---")

    # 메타데이터 입력
    with st.expander("메타데이터"):
        st.session_state['novel_title'] = "신비한 모험의 시작 시즌2"
        st.write(f"소설 제목: **{st.session_state['novel_title']}**")
        st.session_state['perspective'] = st.selectbox(
            "시점 선택",
            ["1인칭 주인공 시점", "1인칭 관찰자 시점", "3인칭 관찰자 시점", "전지적 작가 시점"],
            index=0
        )

        st.session_state['novel_genre'] = st.multiselect(
            "장르 선택 (다중 선택 가능):",
            ["현실주의", "로맨스", "과학", "판타지", "추리", "공포", "역사", "디스토피아", "모험", "게임", "전쟁", "오컬트"],
            default=st.session_state['novel_genre']
        )

        st.session_state['literary_style'] = st.multiselect(
            "문체 (다중 선택 가능):",
            ["격식", "비격식", "서술성", "대화성", "서정적", "시적", "회화적", "극적"],
            default=st.session_state['literary_style']
        )

        st.session_state['theme'] = st.multiselect(
            "주제 (다중 선택 가능):",
            ["사랑", "정체성", "사회비판", "존재", "자유", "선악", "죽음", "인간성", "자연", "운명", "가족", "희생", "희망", "환상", "기억", "기술찬양"],
            default=st.session_state['theme']
        )

    # 세계관 설정
    with st.expander("세계관"):
        st.session_state['background_time'] = st.multiselect(
            "시간적 배경 (다중 선택 가능)",
            ["고대 이집트", "고대 그리스", "고대 로마", "중세유럽", "르네상스 시대", "조선시대", "대항해 시대",
             "근대", "제1차 세계대전", "제2차 세계대전", "현대", "미래", "가상 현실"],
            default=st.session_state['background_time']
        )

        st.session_state['background_space'] = st.multiselect(
            "공간적 배경 (다중 선택 가능)",
            ["우주", "행성", "국가", "도시", "마을", "산", "해안", "심해", "하늘", "지하", "사막", "숲",
             "극지방", "고대 유적지", "판타지세계"],
            default=st.session_state['background_space']
        )

        st.session_state['background_social'] = st.multiselect(
            "사회적 환경 (다중 선택 가능)",
            ["독재", "민주주의", "공산주의", "계몽주의", "제국주의", "전쟁", "자본주의", "공동체주의",
             "유토피아", "디스토피아", "반과학주의", "종교", "환경", "아포칼립스", "인류멸망"],
            default=st.session_state['background_social']
        )

    # 주인공 설정
    with st.expander("주인공 설정"):
        name = st.text_input("이름을 입력하세요")
        age = st.number_input("나이를 입력하세요", min_value=0, max_value=100, value=20)
        job = st.text_input("직업을 입력하세요")
        gender = st.selectbox("성별을 선택하세요", ["남성", "여성","선택하지 않음"], index=0)

        st.session_state['main_character_background'] = st.multiselect(
            "주인공 배경 (다중 선택 가능)",
            ["부모없음", "조부모", "학교폭력", "가정폭력", "연인과헤어짐", "부유함", "평범함",
             "고아원", "이민", "빈곤", "귀족", "평안한 가족", "범죄"],
            default=st.session_state['main_character_background']
        )

        st.session_state['main_character_appearance'] = st.multiselect(
            "외모 (다중 선택 가능)",
            ["장발", "단발", "금발", "흑발", "장신", "단신", "안경", "노인", "장년", "청년",
             "청소년", "미성년", "유아", "영아"],
            default=st.session_state['main_character_appearance']
        )

        st.session_state['main_character_ability'] = st.multiselect(
            "능력 (다중 선택 가능)",
            ["힘이 셈", "힘이 약함", "머리가 좋음", "머리가 나쁨", "손재주가 좋음", "손재주가 나쁨",
             "빠름", "느림", "기억력이 좋음", "잘 잊어버림", "말재주가 좋음", "말재주가 나쁨",
             "기계를 잘 다룸", "기계치"],
            default=st.session_state['main_character_ability']
        )

        st.session_state['main_character_superpower'] = st.multiselect(
            "초능력 (다중 선택 가능)",
            ["물", "불", "번개", "어둠", "바람", "땅", "빛", "부활", "초스피드", "초감각", "힘",
             "정신조작", "소환수", "순간이동", "검술", "기", "에너지조작", "비행"],
            default=st.session_state['main_character_superpower']
        )

        st.session_state['main_character_personality'] = st.multiselect(
            "성격 (다중 선택 가능)",
            ["소심한", "대담한", "말이 많은", "말이 적은", "적극적인", "소극적인", "낙천적인", "비판적인",
             "자기중심적인", "이타적인", "온화한", "고집이 센", "완벽주의의", "의존적인", "상냥한",
             "두려움이 많은", "모험적인", "포용하는", "둔한", "민감한", "냉혹한", "밝은", "배려하는"],
            default=st.session_state['main_character_personality']
        )

        st.session_state['main_character_relationship'] = st.multiselect(
            "주변 관계 (다중 선택 가능)",
            ["부모", "형제", "친구", "악당", "조력자", "스승", "제자", "배우자", "연인"],
            default=st.session_state['main_character_relationship']
        )

    # 프롤로그 생성 버튼
    if st.button("소설 프롤로그 생성하기 ✨"):
        if not gemini_api_key:
            st.error("⚠️ Gemini API 키가 설정되지 않아 프롤로그를 생성할 수 없습니다.")
        else:
            user_prompt_to_llm = f"""당신은 초인기 소설 작가입니다.
            다음 정보를 기반으로 3500자 이내의 소설 프롤로그 1화를 작성해주세요.

            1. 시점: {st.session_state['perspective']}
            2. 장르: {", ".join(st.session_state['novel_genre'])}
            3. 문체: {", ".join(st.session_state['literary_style'])}
            4. 주제: {", ".join(st.session_state['theme'])}
            5. 시간적 배경: {", ".join(st.session_state['background_time'])}
            6. 공간적 배경: {", ".join(st.session_state['background_space'])}
            7. 사회적 환경: {", ".join(st.session_state['background_social'])}
            8. 주인공 이름: {name}, 나이: {age}, 성별: {gender}, 직업: {job}
            9. 주인공 배경: {", ".join(st.session_state['main_character_background'])}
            10. 주인공 외모: {", ".join(st.session_state['main_character_appearance'])}
            11. 주인공 능력: {", ".join(st.session_state['main_character_ability'])}
            12. 주인공 초능력: {", ".join(st.session_state['main_character_superpower'])}
            13. 주인공 성격: {", ".join(st.session_state['main_character_personality'])}
            14. 주인공 주변 관계: {", ".join(st.session_state['main_character_relationship'])}
            """

            with st.spinner("프롤로그를 생성 중입니다... 잠시만 기다려주세요."):
                try:
                    response = model.generate_content([system_prompt, user_prompt_to_llm])
                    result_text = response.text

                    # 결과 저장
                    st.session_state['history'].append(result_text)

                                        # =============================
                    # 새롭게 추가된 파일 저장 로직
                    # =============================
                    try:
                        # 'novel' 디렉토리 생성 (없으면)
                        novel_dir = f"novel/{st.session_state['novel_title']}"
                        if not os.path.exists(novel_dir):
                            os.makedirs(novel_dir)
                            st.success(f"'{novel_dir}' 디렉토리가 생성되었습니다.")


                        # 파일 경로 및 이름 생성 (기존 다운로드 로직 재활용)
                        novel_title = st.session_state.get('novel_title', '제목없음')
                        sanitized_title = sanitize_filename(novel_title)
                        date_str = datetime.date.today().strftime('%Y-%m-%d')
                        file_name = f"{sanitized_title}_episode_{len(st.session_state['history'])}__{date_str}.txt"
                        file_path = os.path.join(novel_dir, file_name)
                        

                        # 파일에 내용 쓰기
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(result_text)

                        st.success(f"프롤로그가 파일로 저장되었습니다: '{file_path}'")
                    except Exception as e:
                        st.error(f"⚠️ 파일 저장 중 오류가 발생했습니다: {e}")


                    st.markdown("---")
                    st.subheader(f"📘 생성된 소설 프롤로그 ({len(st.session_state['history'])}화)")
                    st.write(result_text)

                    # 현재 스크립트가 실행되는 디렉터리를 가져옵니다.
                    current_dir = os.path.dirname(__file__)

                    # 파일 이름을 지정합니다.

                    # 파일의 전체 경로를 조합합니다.
                    file_path = os.path.join(novel_dir, file_name)

                    st.title("파일 경로 출력 예시")

                    # 파일이 존재하는지 확인합니다.
                    if os.path.exists(file_path):
                        st.success(f"파일이 존재합니다! 경로: {file_path}")
                        st.code(f"파일 경로: {file_path}", language="python")
                    else:
                        st.error(f"파일을 찾을 수 없습니다. 경로: {file_path}")
                        st.info("이 코드를 실행하기 전에 'example.txt' 파일을 같은 디렉터리에 만들어주세요.")

                    # Supabase novel 테이블에 데이터 삽입
                    try:
                        inserted_data, count = supabase.table('novel').insert({
                            "title": st.session_state['novel_title'],
                            "novel_genre" : st.session_state['novel_genre'],
                            "background_time" : st.session_state['background_time'],
                            "background_space" : st.session_state['background_space'],
                            "background_social" : st.session_state['background_social'],
                            "literary_style" : st.session_state['literary_style'],
                            "theme" : st.session_state['theme'],
                            "main_character_background" : st.session_state['main_character_background'],
                            "main_character_appearance" : st.session_state['main_character_appearance'],
                            "main_character_ability" : st.session_state['main_character_ability'],
                            "main_character_superpower" : st.session_state['main_character_superpower'],
                            "main_character_personality" : st.session_state['main_character_personality'],
                            "main_character_relationship" : st.session_state['main_character_relationship'],
                            "episode": len(st.session_state['history']),
                            "prompt": user_prompt_to_llm,
                            "contents": file_path
                        }).execute()

                        # inserted_data에서 새로 생성된 id를 가져옴
                        new_record_id = inserted_data[0]['id']
                        st.write(type(len(st.session_state['history'])))

                        st.success("데이터가 성공적으로 삽입되었습니다!")

                    except Exception as e:
                        st.write(type(len(st.session_state['history'])))
                        st.error(f"⚠️ 데이터 삽입 중 오류가 발생했습니다: {e}")



                except Exception as e:
                    st.error(f"⚠️ 프롤로그 생성 중 오류가 발생했습니다: {e}")

# =============================
# 화면 2: 히스토리 확인
# =============================
elif menu == "히스토리 확인":
    st.title("📜 생성된 히스토리")

    series = supabase.table('novel').select('title').execute()

    for button in series :
        if st.button(f"{button[2]}화"):
                FILE_PATH = os.path.join('novel', '신비한 모험의 시작_episode_1__2025-08-07.txt')

                st.title("버튼을 누르면 소설 읽기")
                st.write(f"미리 지정된 파일: **`{FILE_PATH}`**")

                # 파일을 읽는 함수를 정의합니다.
                def read_local_file(path):
                    try:
                        with open(path, 'r', encoding='utf-8') as file:
                            return file.read()
                    except FileNotFoundError:
                        return f"오류: 지정된 파일 '{path}'을(를) 찾을 수 없습니다."
                    except Exception as e:
                        return f"파일을 읽는 중 오류가 발생했습니다: {e}"

                # 버튼을 생성하고, 버튼이 클릭되었을 때의 동작을 정의합니다.
                if st.button("소설 읽기"):
                    # 버튼이 클릭되면 파일을 읽습니다.
                    content = read_local_file(FILE_PATH)
                    
                    # 읽은 내용을 화면에 출력합니다.
                    st.subheader("소설 내용:")
                    st.text(content) 



elif menu == "에피소드 확인":
    st.title("📜 에피소드 확인")

    # data = supabase.table('novel').select('*').eq('id', new_record_id).execute()

    FILE_PATH = os.path.join('novel', '신비한 모험의 시작_episode_1__2025-08-07.txt')

    st.title("버튼을 누르면 소설 읽기")
    st.write(f"미리 지정된 파일: **`{FILE_PATH}`**")

    # 파일을 읽는 함수를 정의합니다.
    def read_local_file(path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return f"오류: 지정된 파일 '{path}'을(를) 찾을 수 없습니다."
        except Exception as e:
            return f"파일을 읽는 중 오류가 발생했습니다: {e}"

    # 버튼을 생성하고, 버튼이 클릭되었을 때의 동작을 정의합니다.
    if st.button("소설 읽기"):
        # 버튼이 클릭되면 파일을 읽습니다.
        content = read_local_file(FILE_PATH)
        
        # 읽은 내용을 화면에 출력합니다.
        st.subheader("소설 내용:")
        st.text(content)


elif menu == "다음 화 작성":
    st.title("📜 다음 화 작성")

    if not st.session_state['novel_title']:
        st.info("아직 작성된 소설이 없습니다.")
    else:
        # TODO: 다음 화 작성 로직 추가
        st.write(f"소설 '{st.session_state['novel_title']}'의 다음 화를 작성할 준비가 되었습니다.")
        # 이 부분에 다음 화를 생성하는 로직을 추가할 수 있습니다.
