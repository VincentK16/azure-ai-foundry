from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import azure.cognitiveservices.speech as speechsdk

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages

# Set up Azure AI Project Client
project_connection_string = "<REPLACE-WITH-YOUR-PROJECT-CONNECTION-STRING>"
project = AIProjectClient.from_connection_string(
    conn_str=project_connection_string, credential=DefaultAzureCredential()
)
chat = project.inference.get_chat_completions_client()

# Set up Azure Speech SDK
speech_key = "<REPLACE-WITH-YOUR-SPEECH-KEY>"
service_region = "<REPLACE WITH YOUR SPEECH REGION>"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_message = request.form['user_message']
        speech_enabled = request.form['speech_enabled'] == 'true'
        selected_voice = request.form['selected_voice']
        
        try:
            response = chat.complete(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that speaks like a techno punk rocker from 2350. Be cool but not too cool. Ya dig?",
                    },
                    {"role": "user", "content": user_message},
                ],
            )
            ai_response = response.choices[0].message.content

            
            if speech_enabled:
                # Synthesize speech
                speech_config.speech_synthesis_voice_name = selected_voice
                audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
                synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
                synthesizer.speak_text_async(ai_response)

            return render_template('index.html', user_message=user_message, ai_response=ai_response, speech_enabled=speech_enabled)
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for('index'))
    return render_template('index.html', speech_enabled=False)


if __name__ == '__main__':
    app.run(debug=True)