import streamlit as st
import asyncio
import edge_tts
import os

# --- 구절별로 음성을 생성하여 합치는 함수 ---
async def generate_bible_audio(text_data, output_path):
    lines = [line.strip() for line in text_data.split('\n') if line.strip()]
    
    # 임시 파일들을 저장할 리스트
    combined_audio = b""

    for i, line in enumerate(lines):
        # 짝수 줄(0, 2, 4...)은 한국어 성우, 홀수 줄(1, 3, 5...)은 영어 성우
        if i % 2 == 0:
            voice = "ko-KR-SunHiNeural"
        else:
            voice = "en-US-GuyNeural"
        
        # 각 줄마다 음성 생성
        communicate = edge_tts.Communicate(line, voice)
        
        # 메모리에 직접 음성 데이터 저장 (임시 파일 생성 없이 속도 향상)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                combined_audio += chunk["data"]
        
        # 구절 사이에 짧은 무음(약 0.5초) 추가 (선택 사항)
        # 실제 무음 데이터를 넣으려면 로직이 복잡해지므로, 
        # 여기서는 구절 끝에 마침표를 추가하여 자연스러운 휴지를 유도합니다.

    with open(output_path, "wb") as f:
        f.write(combined_audio)

# --- UI 레이아웃 (이전과 동일) ---
st.set_page_config(page_title="성경 한영 낭독기", page_icon="📖")
st.title("📖 성경 한-영 교차 낭독기")
st.info("첫 줄은 한글, 둘째 줄은 영어 순서로 입력해 주세요.")

text_input = st.text_area("성경 구절 입력", height=300, 
                          placeholder="태초에 하나님이 천지를 창조하시니라.\nIn the beginning God created the heaven and the earth.")

if st.button("MP3 파일 생성 시작", use_container_width=True):
    if text_input:
        output_file = "bible_reading.mp3"
        with st.spinner("성우들이 교대로 녹음 중입니다..."):
            try:
                # 이벤트 루프 문제 해결을 위한 로직
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(generate_bible_audio(text_input, output_file))
                
                st.success("✅ 교차 낭독 파일 생성 완료!")
                with open(output_file, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                    st.download_button("MP3 다운로드", f, file_name=output_file)
            except Exception as e:
                st.error(f"오류 발생: {e}")
    else:
        st.warning("텍스트를 입력해 주세요.")
