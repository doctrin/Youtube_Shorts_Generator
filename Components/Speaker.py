import cv2
import numpy as np
import webrtcvad
import wave
import contextlib
from pydub import AudioSegment
import os

# FFmpeg 경로를 환경 변수에서 로드하거나 기본 경로 설정
AudioSegment.converter = os.getenv("FFMPEG_PATH", r"C:\\Users\\doctr\\PycharmProjects\\Util\\ffmpeg-2025-01-05-git-19c95ecbff-full_build\\bin\\ffmpeg.exe")

# Update paths to the model files
prototxt_path = "models/deploy.prototxt"
model_path = "models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
temp_audio_path = "temp_audio.wav"

# Load DNN model
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

# Initialize VAD
vad = webrtcvad.Vad(2)  # Aggressiveness mode from 0 to 3

def voice_activity_detection(audio_frame, sample_rate=16000):
    return vad.is_speech(audio_frame, sample_rate)

def extract_audio_from_video(video_path, audio_path):
    audio = AudioSegment.from_file(video_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(audio_path, format="wav")

def process_audio_frame(audio_data, sample_rate=16000, frame_duration_ms=30):
    n = int(sample_rate * frame_duration_ms / 1000) * 2  # 2 bytes per sample
    offset = 0
    while offset + n <= len(audio_data):
        frame = audio_data[offset:offset + n]
        offset += n
        yield frame

def process_detection(detections, frame, w, h, MaxDif, is_speaking_audio):
    """ 얼굴 감지 및 스피커 활성 상태 표시 처리 """
    Add = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.3:  # Confidence threshold
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x, y, x1, y1) = box.astype("int")
            face_width = x1 - x
            face_height = y1 - y

            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x1, y1), (0, 255, 0), 2)

            # Assuming lips are approximately at the bottom third of the face
            lip_distance = abs((y + 2 * face_height // 3) - (y1))
            Add.append([[x, y, x1, y1], lip_distance])

            if lip_distance >= MaxDif and is_speaking_audio:
                cv2.putText(frame, "Active Speaker", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return Add

global Frames
Frames = []  # [x,y,w,h]

def detect_faces_and_speakers(input_video_path, output_video_path):
    global Frames
    # Extract audio from the video
    extract_audio_from_video(input_video_path, temp_audio_path)

    # Read the extracted audio
    with contextlib.closing(wave.open(temp_audio_path, 'rb')) as wf:
        sample_rate = wf.getframerate()
        audio_data = wf.readframes(wf.getnframes())

    cap = cv2.VideoCapture(input_video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))

    frame_duration_ms = 30  # 30ms frames
    audio_generator = process_audio_frame(audio_data, sample_rate, frame_duration_ms)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()

        audio_frame = next(audio_generator, None)
        if audio_frame is None:
            break
        is_speaking_audio = voice_activity_detection(audio_frame, sample_rate)
        MaxDif = 0
        Add = process_detection(detections, frame, w, h, MaxDif, is_speaking_audio)

        #Frames.append([x, y, x1, y1] for x, y, x1, y1, _ in Add)
        Frames.extend(bounding_box for bounding_box, _ in Add)

        out.write(frame)
        #cv2.imshow('Frame', frame)

        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break

    cap.release()
    out.release()
    #cv2.destroyAllWindows()
    os.remove(temp_audio_path)


"""
if __name__ == "__main__":
    # Example usage
    input_video_path = "path/to/input_video.mp4"
    output_video_path = "path/to/output_video.mp4"
    detect_faces_and_speakers(input_video_path, output_video_path)
    print(Frames)
    print(len(Frames))
    print(Frames[:5])

    # FFmpeg 권한 확인 테스트
    print(f"FFmpeg path being used: {AudioSegment.converter}")

    # 테스트용 비디오 파일 경로
    test_video_path = "path/to/test_video.mp4"

    try:
        # FFmpeg를 사용하여 오디오를 추출
        audio = AudioSegment.from_file(test_video_path)
        print("FFmpeg successfully processed the file.")
    except Exception as e:
        print(f"Error with FFmpeg: {e}")
"""

if __name__ == "__main__":
    detect_faces_and_speakers()

    print(Frames)
    print(len(Frames))
    print(Frames[1:5])
