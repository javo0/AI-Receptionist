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
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')

def generate_ai_response(message):
    """Generate AI response using Claude or OpenAI"""
    try:
        if AI_PROVIDER == 'claude':
            return generate_claude_response(message)
        else:
            return generate_openai_response(message)
    except Exception as e:
        print(f"Error generating AI response: {e}")
        # Fallback to simple responses when APIs are not available
        return generate_fallback_response(message)

def generate_fallback_response(message):
    """Generate simple fallback responses when APIs are not available"""
    message_lower = message.lower()
    
    if "saluda" in message_lower or "saludo" in message_lower:
        return "¡Hola! Bienvenido, ¿en qué puedo ayudarte hoy?"
    elif "ayuda" in message_lower or "ayudar" in message_lower:
        return "Por supuesto, estoy aquí para ayudarte. ¿Qué necesitas?"
    elif "información" in message_lower or "info" in message_lower:
        return "Te puedo proporcionar información básica. ¿Sobre qué tema específicamente?"
    elif "contacto" in message_lower or "llamar" in message_lower:
        return "Puedo ayudarte con información de contacto. ¿A quién necesitas contactar?"
    elif "horario" in message_lower or "hora" in message_lower:
        return "Nuestro horario de atención es de lunes a viernes de 9 AM a 6 PM."
    elif "servicio" in message_lower or "servicios" in message_lower:
        return "Ofrecemos varios servicios. ¿Te interesa conocer más sobre alguno en particular?"
    else:
        return "Gracias por tu mensaje. He tomado nota y me pondré en contacto contigo pronto."

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
        
        # Generate TwiML response for real conversation
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">{greeting}</Say>
    <Pause length="1"/>
    <Say voice="alice" language="es-MX">¿En qué puedo ayudarte hoy?</Say>
    <Gather numDigits="1" timeout="10" action="/webhook/gather" method="POST">
        <Say voice="alice" language="es-MX">Por favor, presiona 1 si necesitas información, 2 para hablar con alguien, o 3 para dejar un mensaje.</Say>
    </Gather>
    <Say voice="alice" language="es-MX">No recibí tu respuesta. ¿En qué puedo ayudarte?</Say>
    <Gather numDigits="1" timeout="10" action="/webhook/gather" method="POST">
        <Say voice="alice" language="es-MX">Presiona 1 para información, 2 para hablar con alguien, o 3 para dejar un mensaje.</Say>
    </Gather>
    <Say voice="alice" language="es-MX">Gracias por llamar. ¡Que tengas un buen día!</Say>
    <Hangup/>
</Response>"""
        
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        print(f"Error handling incoming call: {e}")
        # Fallback response
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">Hola, soy tu recepcionista virtual. ¿En qué puedo ayudarte?</Say>
    <Pause length="1"/>
    <Say voice="alice" language="es-MX">¿En qué puedo ayudarte hoy?</Say>
    <Gather numDigits="1" timeout="10" action="/webhook/gather" method="POST">
        <Say voice="alice" language="es-MX">Presiona 1 para información, 2 para hablar con alguien, o 3 para dejar un mensaje.</Say>
    </Gather>
    <Say voice="alice" language="es-MX">Gracias por llamar. ¡Que tengas un buen día!</Say>
    <Hangup/>
</Response>"""
        return Response(twiml, mimetype='text/xml')

@app.route('/webhook/gather', methods=['POST'])
def handle_gather():
    """Handle user input from Gather"""
    try:
        digits = request.form.get('Digits')
        call_sid = request.form.get('CallSid')
        
        print(f"📱 User pressed: {digits} for call {call_sid}")
        
        if digits == '1':
            # Information request
            response_text = generate_ai_response("El visitante pidió información. Proporciona información útil sobre la empresa.")
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">{response_text}</Say>
    <Pause length="1"/>
    <Say voice="alice" language="es-MX">¿Hay algo más en lo que pueda ayudarte?</Say>
    <Gather numDigits="1" timeout="10" action="/webhook/gather" method="POST">
        <Say voice="alice" language="es-MX">Presiona 1 para más información, 2 para hablar con alguien, o 3 para dejar un mensaje.</Say>
    </Gather>
    <Say voice="alice" language="es-MX">Gracias por llamar. ¡Que tengas un buen día!</Say>
    <Hangup/>
</Response>"""
        elif digits == '2':
            # Talk to someone
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">Perfecto, te voy a conectar con alguien que pueda ayudarte mejor.</Say>
    <Pause length="2"/>
    <Say voice="alice" language="es-MX">Por favor, espera mientras te transfiero.</Say>
    <Hangup/>
</Response>"""
        elif digits == '3':
            # Leave a message
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">Perfecto, puedes dejar tu mensaje después del tono.</Say>
    <Record maxLength="60" timeout="10" action="/webhook/recording" method="POST" />
    <Say voice="alice" language="es-MX">Gracias por tu mensaje. Lo procesaré y me pondré en contacto contigo pronto.</Say>
    <Hangup/>
</Response>"""
        else:
            # Invalid option
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">Lo siento, no entendí tu opción.</Say>
    <Pause length="1"/>
    <Say voice="alice" language="es-MX">¿En qué puedo ayudarte hoy?</Say>
    <Gather numDigits="1" timeout="10" action="/webhook/gather" method="POST">
        <Say voice="alice" language="es-MX">Presiona 1 para información, 2 para hablar con alguien, o 3 para dejar un mensaje.</Say>
    </Gather>
    <Say voice="alice" language="es-MX">Gracias por llamar. ¡Que tengas un buen día!</Say>
    <Hangup/>
</Response>"""
        
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        print(f"Error handling gather: {e}")
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">Lo siento, hubo un problema. ¿En qué puedo ayudarte?</Say>
    <Gather numDigits="1" timeout="10" action="/webhook/gather" method="POST">
        <Say voice="alice" language="es-MX">Presiona 1 para información, 2 para hablar con alguien, o 3 para dejar un mensaje.</Say>
    </Gather>
    <Say voice="alice" language="es-MX">Gracias por llamar. ¡Que tengas un buen día!</Say>
    <Hangup/>
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
                
                # Generate a more interactive response
                ai_response = generate_ai_response("El visitante acaba de decir algo. Responde de manera útil y personalizada como una recepcionista real. Sé específica y útil en tu respuesta.")
                
                twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">{ai_response}</Say>
    <Pause length="2"/>
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
