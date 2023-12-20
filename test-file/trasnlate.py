from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator

app = Flask(__name__)


@app.route('/summarize', methods=['POST'])
def translate_text():
    translator = Translator()
    data = request.get_json()  # Get the JSON data from the request
    text = data.get('text', '')  # Get the 'text' field from the JSON data
    tipe = data.get('type', '')
    translation = translator.translate(text, dest='en')
    return jsonify({'result': translation.text})
    # Initialize translation with a default value
    # translation = None

    # try:
    #     if tipe == 'uri' :
    #         transcript_list = YouTubeTranscriptApi.list_transcripts(text)
    #         transcript = transcript_list.find_transcript(['en'])
    #         captions = transcript.fetch()

    #         # Convert the captions into a text format
    #         captions_text = ' '.join([caption['text'] for caption in captions])

    #         # Translate the captions text into English
    #         translation = translator.translate(captions_text, dest='en')

    #         return jsonify({'translated_captions': translation.text})

    #     if tipe == 'text' :
    #         # Translate the text into English
    #         translation = translator.translate(text, dest='en')
    #         return jsonify({'result': translation.text})

    #     # Return the translated text in a JSON response
    # except Exception as e:
    #     print(e)
    # finally:
    #     if translation is not None:
    #         return jsonify({'result': translation.text})
    #     else:
    #         return jsonify({'result': 'No translation available'})

if __name__ == '__main__':
    app.run(debug=True)

