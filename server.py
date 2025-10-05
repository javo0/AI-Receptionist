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
    Eres una recepcionista virtual profesional y amigable. Tu trabajo es:
    1. Saludar cordialmente a los visitantes
    2. Preguntar en qué puedes ayudar
    3. Proporcionar información básica sobre la empresa
    4. Tomar mensajes si es necesario
    5. Conectar con el personal apropiado si es requerido
    
    Mantén las respuestas breves, profesionales y útiles. Si no sabes algo, admítelo y ofrece tomar un mensaje.
    """
    
    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 150,
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
        
        # Generate greeting
        greeting = generate_ai_response("Saluda al visitante que acaba de llamar")
        
        # Generate TwiML response
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">{greeting}</Say>
    <Pause length="1"/>
    <Say voice="alice" language="es-MX">¿En qué puedo ayudarte?</Say>
    <Record maxLength="30" action="/webhook/recording" method="POST" />
</Response>"""
        
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        print(f"Error handling incoming call: {e}")
        # Fallback response
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">Hola, soy tu recepcionista virtual. ¿En qué puedo ayudarte?</Say>
    <Record maxLength="30" action="/webhook/recording" method="POST" />
</Response>"""
        return Response(twiml, mimetype='text/xml')

@app.route('/webhook/recording', methods=['POST'])
def handle_recording():
    """Handle recording from Twilio"""
    try:
        recording_url = request.form.get('RecordingUrl')
        call_sid = request.form.get('CallSid')
        
        print(f"🎙️ Recording received: {recording_url} for call {call_sid}")
        
        # For now, just acknowledge the recording
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="es-MX">Gracias por tu mensaje. Lo procesaré y me pondré en contacto contigo pronto.</Say>
    <Hangup/>
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
