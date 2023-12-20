from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from pytube import extract, YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import re
import whisper
import googleapiclient.discovery

import validators

import os
from google.cloud import translate_v2

import deploytest


# link sample
# https://youtu.be/QFLAuddS6qM?si=zAPC2cK3zK5ClQ10
# https://youtu.be/z-0wXNoEjmo?si=RZgza-EuHpVhA1aj

app = Flask(__name__)
api = Api(app)

# Constants
PATTERN_URL = (
    r'(https?://)?(www\.)?'
    '(youtube|youtu|youtube-nocookie)\.(com|be)/'
    '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
)

API_KEY = "AIzaSyB7ydnfsfAPuJPJFR_VFgQaAanUCKBvZsc"

OUTPUT_PATH = "YoutubeAudios"

class Transcript(Resource):
    def __init__(self):
        self.data = {}

    #  cek pattern link yt 
    def url_path_validation(self, url):
        pattern_url_match = re.match(PATTERN_URL, url)
        return bool(pattern_url_match)
    
    # cek  jika video tersedia di youtube
    def is_video_available(self, API_KEY, video_id):
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

        # Make API request to get video details
        request = youtube.videos().list(part="status", id=video_id)
        response = request.execute()

        # Check if the response contains the video details
        items = response.get("items", [])
        if items:
            status = items[0]["status"]
            upload_status = status.get("uploadStatus")
            
            # Check if video is available
            return upload_status == "processed"
        else:
            return False

    # create file transcript (dipakai hanya jika yt transcript disable)
    def create_and_open_txt(self, text, filename):
        with open(filename, "w") as file:
            file.write(text)

    # take youtube transcript 
    def transcribe_youtube_video(self, yt_video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(yt_video_id, languages=['en','id'])
            text = ' '.join([entry['text'] for entry in transcript])
            return text
        except Exception as e:
            return False
        
    # translate
    def translate_text(self, text, target_language):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f"sumrizz-408115-e2f06ec5cc15.json"

        translate_client = translate_v2.Client()

        output = translate_client.translate(text, target_language=target_language)
        return output['translatedText']

    #  download audio youtube (dipakai hanya jika yt transcript disable)
    def download_audio_stream(self, url):
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        id = extract.video_id(url)
        filename = f"audio_{id}.mp3"
        audio_stream.download(output_path=OUTPUT_PATH, filename=filename)
        print("Audio downloaded successfully!")
        self.data.update({'source': url, 'filename': filename, 'id': id, 'output_path': OUTPUT_PATH})

    # transcript audio (dipakai hanya jika yt transcript disable)
    def transcript_audio(self):
        model = whisper.load_model("base")
        audio_path = f"{OUTPUT_PATH}/audio_{self.data['id']}.mp3"
        result = model.transcribe(audio_path, fp16=False)
        transcribed_text = result["text"]
        return transcribed_text

    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument("source", required=True)
        parse.add_argument("type", required=True)
        parse.add_argument("language", required=True)
        args = parse.parse_args()
        self.data['source'] = args['source']
        self.data['type'] = args['type']
        self.data['language'] = args['language']

        if self.data['type'] == 'link':
            if not self.url_path_validation(self.data['source']):
                return {"error": "Enter the correct YouTube source"}, 400
        
            video_id = extract.video_id(self.data['source'])
            self.data['id'] = video_id

            if not self.is_video_available(API_KEY, self.data['id']):
                return {"error": "video doesnt exist anymore"}, 400

            try:
                transcription = self.transcribe_youtube_video(self.data['id'])
                if transcription is False:
                    self.download_audio_stream(self.data['source'])
                    transcription = self.transcript_audio()   

                self.data['transcription'] = transcription

                translate_transcription = self.translate_text(self.data['transcription'], 'en' )
                clean_translate_transcription =  re.sub("&#39;","'", translate_transcription)
                self.data[f"en_transcription"] = clean_translate_transcription
                
                # =====================================================
                summarize = deploytest.run_model(self.data["en_transcription"])
                self.data['summarize'] = summarize
                # =====================================================
                result  =  self.translate_text(self.data['summarize'], self.data['language'] )
                self.data['result'] = result

                return {'status': 'Success', 'body': self.data}, 200
            except FileNotFoundError:
                return {"error": "Audio file not found"}, 404
            except Exception as e:
                return {"error in": str(e)}, 400
            
        elif self.data['type'] == 'text':

            if self.data['source'].startswith("http") or self.data['source'].startswith("www"):
                return {"error": 'Enter the appropriate data'}, 400
            
            if validators.url(self.data['source']):
                return {"error": 'Enter the appropriate data'}, 400

            try:
                en_transcription = self.translate_text(self.data['source'], 'en')
                self.data['en_transcription'] = en_transcription

                # =====================================================
                summarize = deploytest.run_model(self.data["en_transcription"])
                self.data['summarize'] = summarize
                # =====================================================
                result  =  self.translate_text(self.data['summarize'], self.data['language'] )
                self.data['result'] = result

                
                return {'status': 'Success', 'body': self.data}, 200
            except Exception as e:
                return {"error": str(e)}, 400

        


api.add_resource(Transcript, '/transcript')

if __name__ == '__main__':
    app.run(debug=True)
