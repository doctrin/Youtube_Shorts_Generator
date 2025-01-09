import openai
from dotenv import load_dotenv
import os
import json

load_dotenv()

api_key = os.getenv("OPENAI_API")
if not api_key:
    print("API key not found. Check your .env file.")
else:
    print(f"API key loaded: {api_key}")

openai.api_key = os.getenv("OPENAI_API")

if not openai.api_key:
    raise ValueError("API key not found. Make sure it is defined in the .env file.")


# Function to extract start and end times
def extract_times(json_string):
    try:
        # Parse the JSON string
        data = json.loads(json_string)

        # Extract start and end times as floats
        start_time = float(data[0]["start"])
        end_time = float(data[0]["end"])

        # Convert to integers
        start_time_int = int(start_time)
        end_time_int = int(end_time)
        return start_time_int, end_time_int
    except Exception as e:
        print(f"Error in extract_times: {e}")
        return 0, 0


system = """

Baised on the Transcription user provides with start and end, Highilight the main parts in less then 1 min which can be directly converted into a short. highlight it such that its intresting and also keep the time staps for the clip to start and end. only select a continues Part of the video

Follow this Format and return in valid json 
[{
start: "Start time of the clip",
content: "Highlight Text",
end: "End Time for the highlighted clip"
}]
it should be one continues clip as it will then be cut from the video and uploaded as a tiktok video. so only have one start, end and content

Dont say anything else, just return Proper Json. no explanation etc


IF YOU DONT HAVE ONE start AND end WHICH IS FOR THE LENGTH OF THE ENTIRE HIGHLIGHT, THEN 10 KITTENS WILL DIE, I WILL DO JSON['start'] AND IF IT DOESNT WORK THEN...
"""

User = """
Any Example
"""


def GetHighlight(Transcription):
    print("Getting Highlight from Transcription ")
    try:
        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.7,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": Transcription},
            ],
        )

        # 응답 디버깅
        print(f"API Response: {response}")

        # 응답 처리
        if "choices" not in response or not response["choices"]:
            raise ValueError("API response does not contain 'choices' or it is empty.")

        # JSON 데이터 추출
        json_string = response["choices"][0]["message"]["content"]
        json_string = json_string.replace("json", "").replace("```", "")
        Start, End = extract_times(json_string)

        # 결과 검증
        if Start == End:
            print("Error: Start and End are the same. Re-requesting...")
            return GetHighlight(Transcription)

        return Start, End
    #except openai.error.OpenAIError as e:
    #    print(f"OpenAI API Error: {e}")
    #    return 0, 0
    except Exception as e:
        print(f"Error in GetHighlight: {e}")
        return 0, 0



if __name__ == "__main__":
    print(GetHighlight(User))
