import os

from moviepy.video.io.ffmpeg_tools import ffmpeg_merge_video_audio
from pytubefix import YouTube
import ffmpeg
from pytube import YouTube


# FFmpeg 경로 설정 (필요한 경우 환경 변수 또는 기본 경로 사용)
FFMPEG_PATH = os.getenv("FFMPEG_PATH", r"C:\\Users\\doctr\\PycharmProjects\\Util\\ffmpeg-2025-01-05-git-19c95ecbff-full_build\\bin\\ffmpeg.exe")

def get_video_size(stream):

    return stream.filesize / (1024 * 1024)

def download_youtube_video(url):
    try:
        yt = YouTube(url)

        video_streams = yt.streams.filter(type="video").order_by('resolution').desc()
        audio_stream = yt.streams.filter(only_audio=True).first()

        print("Available video streams:")
        for i, stream in enumerate(video_streams):
            size = get_video_size(stream)
            stream_type = "Progressive" if stream.is_progressive else "Adaptive"
            print(f"{i}. Resolution: {stream.resolution}, Size: {size:.2f} MB, Type: {stream_type}")

        choice = int(input("Enter the number of the video stream to download: "))
        selected_stream = video_streams[choice]

        if not os.path.exists('videos'):
            os.makedirs('videos')

        print(f"Downloading video: {yt.title}")
        video_file = selected_stream.download(output_path='videos', filename_prefix="video_")

        if not selected_stream.is_progressive:
            print("Downloading audio...")
            audio_file = audio_stream.download(output_path='videos', filename_prefix="audio_")

            print("Merging video and audio...")
            output_file = os.path.join('videos', f"{yt.title}.mp4")
            stream = ffmpeg.input(video_file)
            audio = ffmpeg.input(audio_file)
            stream = ffmpeg.output(stream, audio, output_file, vcodec='libx264', acodec='aac', strict='experimental')
            ffmpeg.run(stream, overwrite_output=True)

            os.remove(video_file)
            os.remove(audio_file)
        else:
            output_file = video_file

        
        print(f"Downloaded: {yt.title} to 'videos' folder")
        print(f"File path: {output_file}")
        return output_file

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please make sure you have the latest version of pytube and ffmpeg-python installed.")
        print("You can update them by running:")
        print("pip install --upgrade pytube ffmpeg-python")
        print("Also, ensure that ffmpeg is installed on your system and available in your PATH.")


def download_video(youtube_url, resolution=360):
    print(f"처리할 YouTube URL: {youtube_url}")

    # YouTube 객체 생성
    yt = YouTube(youtube_url)
    print("사용 가능한 비디오 스트림 목록:")

    # 비디오 스트림 필터링 (Adaptive, MP4 형식)
    video_streams = yt.streams.filter(progressive=False, file_extension="mp4", type="video").order_by(
        'resolution').desc()
    # 오디오 스트림 필터링
    audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()

    # 각 스트림의 정보 출력
    for i, stream in enumerate(video_streams):
        print(f"{i}. 해상도: {stream.resolution}, FPS: {stream.fps}, 유형: Adaptive")

    # 다운로드할 스트림 선택
    selected_stream_index = int(input("다운로드할 비디오 스트림 번호를 입력하세요: "))
    video_stream = video_streams[selected_stream_index]

    # 비디오 스트림 다운로드
    print(f"비디오 스트림 다운로드 중: {video_stream.resolution}")
    video_path = video_stream.download(output_path="downloads", filename="video.mp4")
    print(f"비디오가 다운로드되었습니다: {video_path}")

    # 오디오 스트림 다운로드
    print("오디오 스트림 다운로드 중...")
    audio_path = audio_stream.download(output_path="downloads", filename="audio.mp4")
    print(f"오디오가 다운로드되었습니다: {audio_path}")

    # 비디오와 오디오 병합
    merged_output = "downloads/output.mp4"
    print(f"비디오와 오디오를 병합하여 {merged_output}에 저장합니다...")
    ffmpeg_merge_video_audio(video_path, audio_path, merged_output, ffmpeg_path=FFMPEG_PATH)
    print(f"병합된 파일이 {merged_output}에 저장되었습니다.")

    # 임시 파일 정리
    os.remove(video_path)
    os.remove(audio_path)
    print("임시 파일이 삭제되었습니다.")

    return merged_output


if __name__ == "__main__":
    youtube_url = input("Enter YouTube video URL: ")
    try:
        output_file = download_video(youtube_url)
        print(f"Video saved successfully at: {output_file}")
    except Exception as e:
        print(f"Error during download and processing: {e}")
