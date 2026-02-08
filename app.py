import streamlit as st
import asyncio
import edge_tts
import os

# --- TTS 생성 함수 (한/영 교차 로직) ---
async def generate_bible_audio(text_data, output_path):
    lines = [line.strip() for line in text_data.split('\n') if line.strip()]
    communicate_tasks = []
    
    # SSML 방식을 사용하여 성우 교체
    # 한국어: ko-KR-SunHiNeural, 영어: en-US-GuyNeural
    full_ssml = "<speak>"
    for i, line in enumerate(lines):
        # 짝수 줄은 한글, 홀수 줄은 영어로 가정 (혹은 그 반대)
        # 여기서는 단순히 번갈아가며 적용하거나, 언어 감지 로직을 넣을 수 있음
        if i % 2 == 0:
            full_ssml += f'<voice name="ko-KR-SunHiNeural">{line}</voice>'
        else:
            full_ssml += f'<voice name="en-US-GuyNeural">{line}</voice>'
        full_ssml += '<break time="500ms" />'
    full_ssml += "</speak>"

    communicate = edge_tts.Communicate(full_ssml)
    await communicate.save(output_path)

# --- UI 레이아웃 ---
st.set_page_config(page_title="성경 한영 낭독기", page_icon="📖")
st.title("📖 성경 한-영 교차 낭독기")
st.markdown("텍스트를 **'한글 한 줄, 영어 한 줄'** 순서로 입력해 주세요.")

text_input = st.text_area("성경 구절 입력", height=300, placeholder="창세기 1:1\nIn the beginning...")

if st.button("MP3 파일 생성 시작", use_container_width=True):
    if text_input:
        output_file = "bible_reading.mp3"
        with st.spinner("성우가 녹음 중입니다... (분량이 많으면 오래 걸릴 수 있습니다)"):
            try:
                asyncio.run(generate_bible_audio(text_input, output_file))
                
                # 결과물 출력
                st.success("✅ 생성이 완료되었습니다!")
                with open(output_file, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                    st.download_button("MP3 다운로드 받기", f, file_name=output_file)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
    else:
        st.warning("텍스트를 입력해 주세요.")