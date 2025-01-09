from faster_whisper import WhisperModel
import torch

def transcribeAudio(audio_path):
    try:
        print("Transcribing audio...")
        # 명시적으로 CUDA 또는 CPU 설정
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        # 모델 로드 시 compute_type 명시
        model = WhisperModel(
            "base.en",
            device=device,
            compute_type="float32"  # float16 경고를 제거
        )
        print("Model loaded")

        # 전사 수행
        segments, info = model.transcribe(
            audio=audio_path,
            beam_size=5,
            language="en",
            max_new_tokens=128,
            condition_on_previous_text=False
        )
        extracted_texts = [[segment.text, segment.start, segment.end] for segment in segments]
        return extracted_texts
    except Exception as e:
        print("Transcription Error:", e)
        return []
