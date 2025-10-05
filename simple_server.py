#!/usr/bin/env python3
import http.server
import socketserver
import requests
import urllib.parse
import json
import os
import datetime

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER', '')
        self.owner_phone_number = os.getenv('OWNER_PHONE_NUMBER', '')
        self.conversation_notes = []
        super().__init__(*args, **kwargs)
    
    def get_ai_response(self, user_message, call_context=""):
        """Obtener respuesta de OpenAI"""
        if not self.openai_api_key:
            return "Lo siento, no tengo acceso a la inteligencia artificial en este momento."
        
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            prompt = f"""Eres un recepcionista amigable y profesional. Habla exactamente como una persona real.

Contexto: {call_context}
Lo que la persona dijo: {user_message}

IMPORTANTE: Responde como una persona real hablando por teléfono. Sé natural, amigable y servicial.

- Habla conversacionalmente, no formalmente
- Usa expresiones naturales como "perfecto", "entendido", "claro"
- Si es una pregunta: responde y pregunta qué más necesitan
- Si es una cita: pregunta detalles naturalmente
- Si es una queja: muestra empatía real
- Si es información: confirma y pregunta si necesitan algo más

Responde como si estuvieras hablando con un amigo por teléfono. Máximo 2-3 oraciones.
Responde solo lo que dirías, sin explicaciones:"""
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                print(f"❌ OpenAI API Error: {response.status_code} - {response.text}")
                return "Lo siento, hay un problema técnico. ¿Podrías intentar de nuevo?"
                
        except Exception as e:
            print(f"❌ Error calling OpenAI: {e}")
            return "Lo siento, no puedo procesar tu solicitud en este momento."
    
    def add_conversation_note(self, user_message, ai_response):
        """Agregar nota de la conversación"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        note = {
            "timestamp": timestamp,
            "user": user_message,
            "ai": ai_response
        }
        self.conversation_notes.append(note)
        print(f"📝 Added note: {note}")
    
    def send_sms_summary(self, phone_number):
        """Enviar resumen por SMS"""
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
            print("❌ Twilio credentials not configured")
            return
        
        if not self.conversation_notes:
            print("❌ No conversation notes to send")
            return
        
        # Crear resumen
        summary = "📞 Call Summary:\n\n"
        for note in self.conversation_notes:
            summary += f"⏰ {note['timestamp']}\n"
            summary += f"👤 User: {note['user']}\n"
            summary += f"🤖 AI: {note['ai']}\n\n"
        
        # Enviar SMS
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            auth = (self.twilio_account_sid, self.twilio_auth_token)
            data = {
                'From': self.twilio_phone_number,
                'To': phone_number,
                'Body': summary
            }
            
            response = requests.post(url, auth=auth, data=data)
            if response.status_code == 201:
                print(f"✅ SMS sent to {phone_number}")
            else:
                print(f"❌ SMS failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error sending SMS: {e}")
    def do_POST(self):
        try:
            # Leer los datos del webhook
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            print(f"📞 Received webhook: {post_data.decode('utf-8')}")
            print(f"📞 Headers: {dict(self.headers)}")
            
            # Parsear los parámetros
            params = urllib.parse.parse_qs(post_data.decode('utf-8'))
            print(f"📞 Parsed params: {params}")
            
            # Verificar si es una grabación
            if self.path == '/recording':
                self.handle_recording(post_data)
                return
            
            # Verificar si es una selección del menú
            if self.path == '/gather':
                self.handle_gather(post_data)
                return
            
            # Verificar si es reconocimiento de voz
            if self.path == '/speech':
                self.handle_speech(post_data)
                return
            
            # Verificar si es un error de Twilio
            if 'ErrorCode' in params:
                error_code = params['ErrorCode'][0]
                print(f"⚠️ Twilio Error Code: {error_code}")
            
            # Conversación natural en inglés
            twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="diego" language="es-AR" rate="fast">Hola, ¿en qué puedo ayudarte hoy?</Say>
    <Gather input="speech" action="/speech" method="POST" timeout="10" speechTimeout="5" language="es-AR">
    </Gather>
    <Say voice="diego" language="es-AR" rate="fast">No pude escucharte. Por favor deja un mensaje después del tono.</Say>
    <Record maxLength="60" action="/recording" method="POST" />
    <Say voice="diego" language="es-AR" rate="fast">Gracias por tu mensaje. Te contactaré pronto.</Say>
</Response>"""
            
            # Enviar respuesta con headers correctos
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml; charset=utf-8')
            self.send_header('Content-Length', str(len(twiml_response.encode('utf-8'))))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(twiml_response.encode('utf-8'))
            
            print("✅ Sent TwiML response")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        # Manejar peticiones GET también
        print(f"📞 Received GET request: {self.path}")
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"AI Receptionist Webhook Server")
    
    def handle_gather(self, data):
        """Manejar selección del menú"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            print(f"🔢 Received gather: {post_data.decode('utf-8')}")
            
            # Parsear los parámetros
            params = urllib.parse.parse_qs(post_data.decode('utf-8'))
            digits = params.get('Digits', [''])[0]
            
            print(f"🔢 User pressed: {digits}")
            
            if digits == '1':
                # Hablar con IA
                ai_response = self.get_ai_response("Usuario quiere hablar directamente", "Conversación en vivo")
                
                twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="diego" language="es-AR">Perfecto, estoy aquí para ayudarte. {ai_response}</Say>
    <Gather input="speech" action="/speech" method="POST" timeout="20" speechTimeout="auto" language="es-AR" enhanced="true">
        <Say voice="diego" language="es-AR">Dime, ¿en qué puedo ayudarte?</Say>
    </Gather>
    <Say voice="diego" language="es-AR">No escuché tu respuesta. Te transfiero al buzón de voz.</Say>
    <Record maxLength="60" action="/recording" method="POST" />
    <Say voice="diego" language="es-AR">Gracias por tu mensaje.</Say>
</Response>"""
            elif digits == '2':
                # Dejar mensaje
                twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="diego" language="es-AR">Perfecto, puedes dejar tu mensaje después del tono.</Say>
    <Record maxLength="60" action="/recording" method="POST" />
    <Say voice="diego" language="es-AR">Gracias por tu mensaje. Javier te contactará pronto.</Say>
</Response>"""
            else:
                # Opción inválida
                twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="diego" language="es-AR">Opción no válida. Te transfiero al buzón de voz.</Say>
    <Record maxLength="60" action="/recording" method="POST" />
    <Say voice="diego" language="es-AR">Gracias por tu mensaje.</Say>
</Response>"""
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml; charset=utf-8')
            self.send_header('Content-Length', str(len(twiml_response.encode('utf-8'))))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(twiml_response.encode('utf-8'))
            
            print("✅ Gather processed successfully")
        except Exception as e:
            print(f"❌ Error processing gather: {e}")
            self.send_response(500)
            self.end_headers()
    
    def handle_speech(self, data):
        """Manejar reconocimiento de voz"""
        try:
            # Usar los datos que ya se leyeron en do_POST
            print(f"🗣️ Received speech: {data.decode('utf-8')}")
            
            # Parsear los parámetros
            params = urllib.parse.parse_qs(data.decode('utf-8'))
            
            # Intentar primero con SpeechResult, luego con UnstableSpeechResult
            speech_result = params.get('SpeechResult', [''])[0]
            if not speech_result:
                speech_result = params.get('UnstableSpeechResult', [''])[0]
            
            print(f"🗣️ SpeechResult: {params.get('SpeechResult', [''])[0]}")
            print(f"🗣️ UnstableSpeechResult: {params.get('UnstableSpeechResult', [''])[0]}")
            print(f"🗣️ Final speech_result: {speech_result}")
            print(f"🗣️ All params: {params}")
            
            # Si aún no hay speech_result, usar un mensaje por defecto
            if not speech_result:
                speech_result = "Hola, necesito ayuda"
                print(f"🗣️ Using default message: {speech_result}")
            
            # Debug: mostrar exactamente qué está pasando
            print(f"🔍 DEBUG: speech_result = '{speech_result}'")
            print(f"🔍 DEBUG: speech_result type = {type(speech_result)}")
            print(f"🔍 DEBUG: speech_result length = {len(speech_result) if speech_result else 0}")
            
            # Asegurar que speech_result no esté vacío
            if not speech_result or speech_result.strip() == "":
                speech_result = "Hola, necesito ayuda"
                print(f"🔧 FIXED: speech_result was empty, using: {speech_result}")
            
            # Asegurar que speech_result no esté vacío después de todo
            if not speech_result or speech_result.strip() == "":
                speech_result = "Hola, necesito ayuda"
                print(f"🔧 FINAL FIX: speech_result was empty, using: {speech_result}")
            
            print(f"🎯 FINAL speech_result: '{speech_result}'")
            
            # Obtener respuesta de IA
            ai_response = self.get_ai_response(speech_result, "Conversación en vivo")
            
            # Agregar nota de la conversación
            self.add_conversation_note(speech_result, ai_response)
            
            # Si el usuario dice "bye" o "goodbye", enviar SMS y terminar
            if any(word in speech_result.lower() for word in ['bye', 'goodbye', 'thanks', 'thank you', 'see you', 'chau', 'adiós', 'gracias', 'hasta luego']):
                # Enviar SMS con resumen
                if self.owner_phone_number:
                    self.send_sms_summary(self.owner_phone_number)
                
                twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="diego" language="es-AR" rate="fast">{ai_response}</Say>
    <Say voice="diego" language="es-AR" rate="fast">Perfecto, gracias por llamar. ¡Que tengas un excelente día!</Say>
</Response>"""
            else:
                twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="diego" language="es-AR" rate="fast">{ai_response}</Say>
    <Gather input="speech" action="/speech" method="POST" timeout="10" speechTimeout="5" language="es-AR">
    </Gather>
    <Say voice="diego" language="es-AR" rate="fast">Perfecto, gracias por llamar. ¡Que tengas un excelente día!</Say>
</Response>"""
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml; charset=utf-8')
            self.send_header('Content-Length', str(len(twiml_response.encode('utf-8'))))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(twiml_response.encode('utf-8'))
            
            print("✅ Speech processed successfully")
        except Exception as e:
            print(f"❌ Error processing speech: {e}")
            self.send_response(500)
            self.end_headers()
    
    def handle_recording(self, data):
        """Manejar grabaciones de voz"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            print(f"🎙️ Received recording: {post_data.decode('utf-8')}")
            print(f"🎙️ Headers: {dict(self.headers)}")
            
            # Parsear los parámetros de la grabación
            params = urllib.parse.parse_qs(post_data.decode('utf-8'))
            print(f"🎙️ Recording params: {params}")
            
            # Respuesta de confirmación
            twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="diego" language="es-AR">Gracias por tu mensaje. Javier te contactará pronto.</Say>
</Response>"""
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml; charset=utf-8')
            self.send_header('Content-Length', str(len(twiml_response.encode('utf-8'))))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(twiml_response.encode('utf-8'))
            
            print("✅ Recording processed successfully")
        except Exception as e:
            print(f"❌ Error processing recording: {e}")
            self.send_response(500)
            self.end_headers()

if __name__ == "__main__":
    PORT = 8095
    with socketserver.TCPServer(("", PORT), WebhookHandler) as httpd:
        print(f"🚀 Server running on port {PORT}")
        httpd.serve_forever()
