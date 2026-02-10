import streamlit as st
import asyncio
import edge_tts
from pydub import AudioSegment
from moviepy.editor import ImageClip, AudioFileClip
import io
import os

# (기존 generate_audio_segment, process_narration 함수는 그대로 유지)

def create_video(audio_path, image_file, output_video_path):
    """오디오와 이미지를 합쳐 MP4 생성"""
    # 1. 이미지 처리 (사용자가 올린 이미지 혹은 기본 검은 배경)
    if image_file:
        # 임시로 이미지 저장
        with open("temp_img.png", "wb") as f:
            f.write(image_file.getbuffer())
        img_clip = ImageClip("temp_img.png")
    else:
        # 이미지가 없으면 검은색 배경 생성 (640x360)
        img_clip = ColorClip(size=(640, 360), color=(0,0,0))

    # 2. 오디오 로드 및 길이 측정
    audio_clip = AudioFileClip(audio_path)
    
    # 3. 영상 설정 (이미지 지속 시간을 오디오 길이에 맞춤)
    video_clip = img_clip.set_duration(audio_clip.duration)
    video_clip = video_clip.set_audio(audio_clip)
    
    # 4. 파일 쓰기 (fps는 10 정도로 낮게 설정해도 충분합니다)
    video_clip.write_videofile(output_video_path, fps=10, codec="libx264")
    
    # 클립 닫기 (메모리 해제)
    audio_clip.close()
    video_clip.close()

# --- UI 부분 ---
with st.sidebar:
    st.header("🎬 영상 설정")
    bg_image = st.file_uploader("배경 이미지 업로드 (선택)", type=["jpg", "png", "jpeg"])

# ... 제작 시작 버튼 클릭 시 ...
if st.button("고퀄리티 MP4 영상 제작"):
    # 1. 오디오 먼저 생성 (기존 로직 사용)
    # 2. 생성된 오디오를 파일로 저장
    temp_audio = "temp_audio.mp3"
    final_audio.export(temp_audio, format="mp3")
    
    # 3. 영상 제작 호출
    with st.spinner("영상을 렌더링 중입니다. 잠시만 기다려 주세요..."):
        video_output = "final_video.mp4"
        create_video(temp_audio, bg_image, video_output)
        
        # 4. 결과 출력
        with open(video_output, "rb") as v:
            st.video(v.read())
            st.download_button("MP4 영상 다운로드", v, file_name="bible_video.mp4")
