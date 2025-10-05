#!/usr/bin/env python3
"""
AI Receptionist Webhook Server
Handles Twilio webhooks for the AI Receptionist app
"""

from flask import Flask, request, Response
import json
import os
import requests
from datetime import datetime

app = Flask(__name__)

# Configuration
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', 'YOUR_CLAUDE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')
AI_PROVIDER = os.getenv('AI_PROVIDER', 'claude')

def generate_ai_response(message):
    """Generate AI response using Claude or OpenAI"""
    try:
        if AI_PROVIDER == 'claude':
            return generate_claude_response(message)
        else:
            return generate_openai_response(message)
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "Lo siento, no puedo procesar tu solicitud en este momento."

def generate_claude_response(message):
    """Generate response using Claude AI"""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    system_prompt = """
    Eres una recepcionista humana real, no un robot. Tu personalidad es:
    - Cálida, amigable y natural
    - Hablas como una persona real, no como una máquina
    - Usas expresiones naturales y conversacionales
    - Eres empática y comprensiva
    - Mantienes un tono profesional pero humano
    
    Tu trabajo es ayudar a los visitantes de manera natural y conversacional. 
    Responde como si fueras una persona real, no un sistema automatizado.
    """
    
    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 200,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    result = response.json()
    return result['content'][0]['text']

def generate_openai_response(message):
    """Generate response using OpenAI"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """
    Eres una recepcionista virtual profesional y amigable. Tu trabajo es:
    1. Saludar cordialmente a los visitantes
    2. Preguntar en qué puedes ayudar
    3. Proporcionar información básica sobre la empresa
    4. Tomar mensajes si es necesario
    5. Conectar con el personal apropiado si es requerido
    
    Mantén las respuestas breves, profesionales y útiles. Si no sabes algo, admítelo y ofrece tomar un mensaje.
    """
    
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "max_tokens": 150
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    result = response.json()
    return result['choices'][0]['message']['content']

@app.route('/webhook/incoming', methods=['POST'])
def handle_incoming_call():
    """Handle incoming call from Twilio"""
    try:
        # Get call information from Twilio
        call_sid = request.form.get('CallSid')
        from_number = request.form.get('From')
        to_number = request.form.get('To')
        
        print(f"📞 Incoming call: {call_sid} from {from_number} to {to_number}")
        
        # Generate natural human-like greeting
        greeting = generate_ai_response("Eres una recepcionista humana real, no un robot. Saluda de manera natural, cálida y personal como si fueras una persona real. Pregunta cómo puedes ayudar de forma conversacional.")
        
        # Generate TwiML response with better configuration
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">{greeting}</Say>
    <Pause length="2"/>
    <Say voice="alice" language="es-MX">¿En qué puedo ayudarte hoy?</Say>
    <Record maxLength="30" timeout="10" action="/webhook/recording" method="POST" 
            recordingStatusCallback="/webhook/recording-status" 
            recordingStatusCallbackMethod="POST" />
</Response>"""
        
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        print(f"Error handling incoming call: {e}")
        # Fallback response
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">Hola, soy tu recepcionista virtual. ¿En qué puedo ayudarte?</Say>
    <Pause length="2"/>
    <Say voice="alice" language="es-MX">Por favor, habla después del tono.</Say>
    <Record maxLength="30" timeout="10" action="/webhook/recording" method="POST" />
</Response>"""
        return Response(twiml, mimetype='text/xml')

@app.route('/webhook/recording', methods=['POST'])
def handle_recording():
    """Handle recording from Twilio"""
    try:
        recording_url = request.form.get('RecordingUrl')
        call_sid = request.form.get('CallSid')
        recording_duration = request.form.get('RecordingDuration')
        
        print(f"🎙️ Recording received: {recording_url} for call {call_sid}, duration: {recording_duration}")
        
        if recording_url and recording_duration and int(recording_duration) > 0:
            # Process the recording
            try:
                print(f"Processing recording: {recording_url}, duration: {recording_duration}")
                
                # Process the recording as a professional receptionist
                try:
                    # Download and transcribe the recording
                    import requests
                    response = requests.get(recording_url)
                    if response.status_code == 200:
                        # Save the recording temporarily
                        with open('/tmp/recording.wav', 'wb') as f:
                            f.write(response.content)
                        
                        # Transcribe using OpenAI Whisper
                        import openai
                        client = openai.OpenAI(api_key=OPENAI_API_KEY)
                        
                        with open('/tmp/recording.wav', 'rb') as audio_file:
                            transcript = client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file,
                                language="es"
                            )
                        
                        user_message = transcript.text
                        print(f"Transcribed: {user_message}")
                        
                        # Generate natural human-like response
                        ai_response = generate_ai_response(f"Eres una recepcionista humana real, no un robot. El visitante dijo: '{user_message}'. Responde de manera natural, conversacional y humana. Habla como una persona real, no como una máquina. Sé cálida, útil y natural en tu respuesta.")
                        
                        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">{ai_response}</Say>
    <Pause length="2"/>
    <Say voice="alice" language="es-MX">¿Hay algo más en lo que pueda ayudarte hoy?</Say>
    <Record maxLength="30" timeout="10" action="/webhook/recording" method="POST" />
</Response>"""
                    else:
                        # Fallback if transcription fails
                        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">Gracias por tu mensaje. He tomado nota y me pondré en contacto contigo pronto.</Say>
    <Pause length="1"/>
    <Say voice="alice" language="es-MX">¿Hay algo más en lo que pueda ayudarte hoy?</Say>
    <Record maxLength="30" timeout="10" action="/webhook/recording" method="POST" />
</Response>"""
                except Exception as e:
                    print(f"Error processing recording: {e}")
                    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">Gracias por tu mensaje. He tomado nota y me pondré en contacto contigo pronto.</Say>
    <Pause length="1"/>
    <Say voice="alice" language="es-MX">¿Hay algo más en lo que pueda ayudarte hoy?</Say>
    <Record maxLength="30" timeout="10" action="/webhook/recording" method="POST" />
</Response>"""
            except Exception as e:
                print(f"Error processing recording: {e}")
                twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">Gracias por tu mensaje. Lo procesaré y me pondré en contacto contigo pronto.</Say>
    <Hangup/>
</Response>"""
        else:
            # No recording or empty recording
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">No pude escuchar tu mensaje. ¿Podrías repetirlo?</Say>
    <Record maxLength="30" timeout="10" action="/webhook/recording" method="POST" />
</Response>"""
        
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        print(f"Error handling recording: {e}")
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">Gracias por llamar. ¡Que tengas un buen día!</Say>
    <Hangup/>
</Response>"""
        return Response(twiml, mimetype='text/xml')

def process_recording(recording_url):
    """Process the recording and generate AI response"""
    try:
        print(f"Processing recording: {recording_url}")
        
        # Download the recording
        import requests
        response = requests.get(recording_url)
        if response.status_code != 200:
            print(f"Failed to download recording: {response.status_code}")
            return "Lo siento, no pude descargar tu mensaje. ¿Podrías repetirlo?"
        
        # Save the recording temporarily
        with open('/tmp/recording.wav', 'wb') as f:
            f.write(response.content)
        
        # Transcribe using OpenAI Whisper
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            with open('/tmp/recording.wav', 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"
                )
            
            user_message = transcript.text
            print(f"Transcribed: {user_message}")
            
            # Generate AI response based on the transcription
            ai_response = generate_ai_response(f"El usuario dijo: {user_message}. Responde de manera útil y profesional.")
            
            return ai_response
            
        except Exception as e:
            print(f"Error transcribing: {e}")
            return "Gracias por tu mensaje. He tomado nota y me pondré en contacto contigo pronto."
        
    except Exception as e:
        print(f"Error processing recording: {e}")
        return "Lo siento, no pude procesar tu mensaje. ¿Podrías repetirlo?"

@app.route('/webhook/recording-status', methods=['POST'])
def handle_recording_status():
    """Handle recording status updates"""
    try:
        call_sid = request.form.get('CallSid')
        recording_status = request.form.get('RecordingStatus')
        recording_url = request.form.get('RecordingUrl')
        
        print(f"📊 Recording status: {recording_status} for call {call_sid}, URL: {recording_url}")
        
        return "OK"
        
    except Exception as e:
        print(f"Error handling recording status: {e}")
        return "OK"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return {
        "message": "AI Receptionist Webhook Server",
        "status": "running",
        "provider": AI_PROVIDER,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
