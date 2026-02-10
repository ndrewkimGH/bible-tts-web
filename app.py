import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment
from moviepy.editor import ImageClip, AudioFileClip
import io
import os

# --- 설정 ---
VOICES = {
    "한국어 여성 (선희)": "ko-KR-SunHiNeural",
    "한국어 남성 (인준)": "ko-KR-InJunNeural",
    "영어 여성 (에바)": "en-US-AvaNeural",
    "영어 남성 (가이)": "en-US-GuyNeural"
}

async def generate_audio_segment(text, voice, rate):
    rate_str = f"{rate:+d}%"
    communicate = edge_tts.Communicate(text, voice, rate=rate_str)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    if not audio_data: return None
    return AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")

async def process_narration(text_data, selected_voice, speed, pause_sec, bgm_file):
    raw_lines = text_data.split('\n')
    combined = AudioSegment.empty()
    normal_pause = AudioSegment.silent(duration=int(pause_sec * 1000))
    paragraph_pause = AudioSegment.silent(duration=int(pause_sec * 3000))

    for line in raw_lines:
        clean_line = line.strip()
        if not clean_line:
            combined += paragraph_pause
            continue
        segment = await generate_audio_segment(clean_line, selected_voice, speed)
        if segment:
            combined += segment + normal_pause

    if bgm_file is not None:
        bgm = AudioSegment.from_file(bgm_file) - 25
        if len(bgm) < len(combined):
            bgm = bgm * (len(combined) // len(bgm) + 1)
        combined = combined.overlay(bgm[:len(combined)])
    
    return combined

# --- UI 레이아웃 ---
st.set_page_config(page_title="성경 영상 제작기", layout="wide")
st.title("🎬 성경 나레이션 영상(MP4) 제작")

with st.sidebar:
    st.header("⚙️ 설정")
    chosen_voice = st.selectbox("성우 선택", list(VOICES.keys()))
    speed = st.slider("속도 (%)", -50, 50, 0, step=5)
    pause_time = st.slider("간격 (초)", 0.0, 5.0, 1.0, 0.5)
    st.write("---")
    img_upload = st.file_uploader("배경 이미지 (필수)", type=["jpg", "png", "jpeg"])
    bgm_upload = st.file_uploader("배경음악 (선택)", type=["mp3", "wav"])

text_input = st.text_area("스크립트 입력", height=300)

if st.button("MP4 영상 생성 시작", use_container_width=True):
    if text_input and img_upload:
        try:
            # 3.12용 안전한 비동기 루프 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            with st.spinner("1단계: 음성 및 배경음악 합성 중..."):
                final_audio = loop.run_until_complete(process_narration(
                    text_input, VOICES[chosen_voice], speed, pause_time, bgm_upload
                ))
                audio_path = "temp_audio.mp3"
                final_audio.export(audio_path, format="mp3")
            
            with st.spinner("2단계: 영상 렌더링 중 (약 1~2분 소요)..."):
                img_path = "temp_img.png"
                with open(img_path, "wb") as f:
                    f.write(img_upload.getbuffer())
                
                # 영상 제작
                audio_clip = AudioFileClip(audio_path)
                img_clip = ImageClip(img_path).set_duration(audio_clip.duration)
                video_clip = img_clip.set_audio(audio_clip)
                
                video_output = "bible_final.mp4"
                video_clip.write_videofile(video_output, fps=10, codec="libx264", audio_codec="aac")
                
                st.success("✅ 제작 완료!")
                st.video(video_output)
                with open(video_output, "rb") as f:
                    st.download_button("MP4 다운로드", f, file_name="bible_video.mp4")
                
                # 메모리 해제
                audio_clip.close()
                video_clip.close()
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
    else:
        st.warning("스크립트와 배경 이미지를 입력해 주세요.")
