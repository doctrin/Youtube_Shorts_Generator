from pydub import AudioSegment

# FFmpeg 실행 파일 경로를 명시적으로 설정
AudioSegment.converter = r"C:\Users\doctr\PycharmProjects\Util\ffmpeg-2025-01-05-git-19c95ecbff-full_build\bin\ffmpeg.exe"

# FFmpeg 경로 확인
print(f"FFmpeg path being used: {AudioSegment.converter}")

# 테스트용 비디오 파일 경로
test_video_path = "ffmpeg_test/test_video.mp4"

try:
    # FFmpeg를 사용하여 오디오를 추출
    audio = AudioSegment.from_file(test_video_path)
    print("FFmpeg successfully processed the file.")
except Exception as e:
    print(f"Error with FFmpeg: {e}")
