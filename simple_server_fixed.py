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
            
            # Detectar hora actual para saludo apropiado
            import datetime
            current_hour = datetime.datetime.now().hour
            greeting = "Buenos días" if current_hour < 12 else "Buenas tardes"
            
            prompt = f"""Eres Javier, el recepcionista experto de una empresa de servicios automotrices. Eres extremadamente profesional, eficiente y conocedor.

Contexto: {call_context}
Lo que la persona dijo: {user_message}
Hora actual: {current_hour}:00 - Saludo apropiado: {greeting}

IMPORTANTE: Responde como un recepcionista experto en servicios automotrices:

- SIEMPRE usa "{greeting}" (nunca cambies el saludo)
- Usa un tono profesional, confiable y experto
- Demuestra conocimiento técnico cuando sea relevante
- Si es una cita: confirma los detalles que te han dado y pregunta por los que faltan
- Si es información: proporciona información técnica precisa y útil
- Si es una queja: muestra empatía profesional y ofrece soluciones concretas
- Usa terminología técnica apropiada (cambio de aceite, frenos, motor, etc.)
- NUNCA preguntes "¿Hay algo más?" hasta que tengas TODOS los detalles necesarios
- Solo pregunta "¿Hay algo más en lo que pueda asistirle?" cuando tengas toda la información completa

Responde como un recepcionista experto en servicios automotrices. Máximo 2-3 oraciones.
Responde solo lo que dirías, sin explicaciones:"""
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.5
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=5
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
            
            # Conversación natural en español
            # Detectar hora para saludo apropiado
            import datetime
            current_hour = datetime.datetime.now().hour
            greeting = "Buenos días" if current_hour < 12 else "Buenas tardes"
        
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="diego" language="es-AR" rate="x-fast">{greeting}, gracias por llamar a AutoServicios Pro. Soy Javier, su especialista en servicios automotrices. ¿En qué puedo asistirle hoy?</Say>
    <Gather input="speech" action="/speech" method="POST" timeout="10" speechTimeout="5" language="es-AR">
    </Gather>
    <Say voice="diego" language="es-AR" rate="x-fast">No pude escucharte claramente. Por favor deja un mensaje detallado con su nombre, teléfono y el servicio que necesita.</Say>
    <Record maxLength="60" action="/recording" method="POST" />
    <Say voice="diego" language="es-AR" rate="x-fast">Gracias por su mensaje. Nuestro equipo técnico le contactará a la brevedad.</Say>
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
            print(f"🔢 Received gather: {data.decode('utf-8')}")
            
            # Parsear los parámetros
            params = urllib.parse.parse_qs(data.decode('utf-8'))
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
            if any(word in speech_result.lower() for word in ['bye', 'goodbye', 'thanks', 'thank you', 'see you', 'chau', 'adiós', 'gracias', 'hasta luego', 'eso es todo', 'nada más', 'no hay más', 'ya está', 'listo', 'terminado']):
                # Enviar SMS con resumen
                if self.owner_phone_number:
                    self.send_sms_summary(self.owner_phone_number)
                
                twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="diego" language="es-AR" rate="x-fast">{ai_response}</Say>
    <Say voice="diego" language="es-AR" rate="x-fast">Perfecto, ha sido un placer atenderle. Nuestro equipo técnico se encargará de todo. Que tenga un excelente día.</Say>
</Response>"""
            else:
                twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="diego" language="es-AR" rate="x-fast">{ai_response}</Say>
    <Gather input="speech" action="/speech" method="POST" timeout="12" speechTimeout="6" language="es-AR">
    </Gather>
    <Say voice="diego" language="es-AR" rate="x-fast">Ha sido un placer atenderle. Nuestro equipo técnico está a su disposición. Que tenga un excelente día.</Say>
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
            print(f"🎙️ Received recording: {data.decode('utf-8')}")
            print(f"🎙️ Headers: {dict(self.headers)}")
            
            # Parsear los parámetros de la grabación
            params = urllib.parse.parse_qs(data.decode('utf-8'))
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
    PORT = 8096
    with socketserver.TCPServer(("", PORT), WebhookHandler) as httpd:
        print(f"🚀 Server running on port {PORT}")
        httpd.serve_forever()
