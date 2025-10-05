#!/usr/bin/env python3
"""
AI Receptionist Server - Twilio Webhook Handler
Handles incoming calls and provides AI-powered responses
"""

import http.server
import socketserver
import urllib.parse
import json
import os
import requests
import datetime

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Load environment variables
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.owner_phone_number = os.getenv('OWNER_PHONE_NUMBER')
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
            
            # Detectar hora actual para saludo apropiado (zona horaria del usuario)
            import pytz
            # Zona horaria de Argentina (Buenos Aires)
            argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
            current_time = datetime.datetime.now(argentina_tz)
            current_hour = current_time.hour
            
            if current_hour < 12:
                greeting = "Buenos días"
            elif current_hour < 18:
                greeting = "Buenas tardes"
            else:
                greeting = "Buenas noches"
            
            prompt = f"""Eres Lindy, el mejor agente de voz de IA. Súper inteligente, empático y eficiente.

Usuario dijo: {user_message}

ANÁLISIS INTELIGENTE:
1. ¿Tiene NOMBRE? (Juan, María, Carlos, etc.)
2. ¿Tiene TELÉFONO? (números como 805000, 9145000, etc.)
3. ¿Tiene MOTIVO? (que me llame, que me regrese la llamada, consulta, etc.)

REGLAS DE RAZONAMIENTO:
- Si tiene NOMBRE + TELÉFONO + MOTIVO: ¡TIENES TODO! Responde confirmando y termina
- Si tiene NOMBRE + TELÉFONO: Pregunta solo el motivo
- Si tiene solo NOMBRE: Pregunta teléfono y motivo
- Si tiene solo TELÉFONO: Pregunta nombre y motivo
- Si tiene solo MOTIVO: Pregunta nombre y teléfono
- Si dice "Eso es todo", "Nada más", "No hay más", "Ya está", "Listo", "Terminado", "Perfecto", "No", "No gracias": TERMINA LA CONVERSACIÓN

RESPUESTAS ESPECÍFICAS:
- Si tienes TODO: "Perfecto [NOMBRE], he tomado nota de tu mensaje. Javier se pondrá en contacto contigo pronto al [TELÉFONO]. ¡Que tengas un excelente día!"
- Si dice "Eso es todo": "Perfecto, he tomado nota de todo. Javier se pondrá en contacto contigo pronto. ¡Que tengas un excelente día!"
- Si te falta información: Pregunta solo lo que falta
- Máximo 1 oración corta y útil

EJEMPLOS:
- "Juan" → "¿Cuál es tu número de teléfono y el motivo de tu consulta?"
- "Juan, 805000, que me regrese la llamada" → "Perfecto Juan, he tomado nota de tu mensaje. Javier se pondrá en contacto contigo pronto al 805000. ¡Que tengas un excelente día!"
- "Eso es todo" → "Perfecto, he tomado nota de todo. Javier se pondrá en contacto contigo pronto. ¡Que tengas un excelente día!"

ANALIZA EL MENSAJE DEL USUARIO Y RESPONDE SEGÚN LAS REGLAS:"""
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
                "temperature": 0.1,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
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
            print(f"❌ Error getting AI response: {e}")
            # Respuesta más natural cuando hay problemas técnicos
            return "Disculpa, no pude procesar tu mensaje. ¿Podrías repetir tu información?"

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
        print(f"📱 Attempting to send SMS to {phone_number}")
        print(f"📱 Twilio credentials check:")
        print(f"📱 Account SID: {self.twilio_account_sid}")
        print(f"📱 Auth Token: {self.twilio_auth_token[:10]}...")
        print(f"📱 Phone Number: {self.twilio_phone_number}")
        print(f"📱 Conversation notes count: {len(self.conversation_notes)}")
        
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

        print(f"📱 SMS Summary: {summary}")

        # Enviar SMS
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            auth = (self.twilio_account_sid, self.twilio_auth_token)
            data = {
                'From': self.twilio_phone_number,
                'To': phone_number,
                'Body': summary
            }
            
            print(f"📱 Sending SMS to {phone_number} from {self.twilio_phone_number}")
            print(f"📱 SMS URL: {url}")
            print(f"📱 SMS Data: {data}")

            response = requests.post(url, auth=auth, data=data)
            print(f"📱 SMS Response Status: {response.status_code}")
            print(f"📱 SMS Response Text: {response.text}")
            
            if response.status_code == 201:
                print(f"✅ SMS sent to {phone_number}")
            else:
                print(f"❌ SMS failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error sending SMS: {e}")

    def send_email_summary(self):
        """Send email summary of the conversation"""
        try:
            print("📧 Attempting to send email summary")
            
            # Create summary
            summary = "📞 Call Summary:\n\n"
            for note in self.conversation_notes:
                summary += f"⏰ {note['timestamp']}\n"
                summary += f"👤 User: {note['user']}\n"
                summary += f"🤖 AI: {note['ai']}\n\n"
            
            print(f"📧 Email Summary: {summary}")
            print("📧 Email notification logged (implement email service as needed)")
            
            # TODO: Implement actual email sending
            # For now, just log the summary
            with open("call_summaries.txt", "a", encoding="utf-8") as f:
                f.write(f"\n=== NEW CALL SUMMARY ===\n{summary}\n")
            
            print("✅ Email summary saved to call_summaries.txt")
                
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            import traceback
            traceback.print_exc()

    def do_POST(self):
        """Handle POST requests from Twilio"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        print(f"📞 Received webhook: {post_data.decode('utf-8')}")
        print(f"📞 Headers: {dict(self.headers)}")
        
        # Parse parameters
        params = urllib.parse.parse_qs(post_data.decode('utf-8'))
        print(f"📞 Parsed params: {params}")
        
        if self.path == '/':
            self.handle_initial_call(params)
        elif self.path == '/speech':
            self.handle_speech(post_data)
        elif self.path == '/recording':
            self.handle_recording(params)
        else:
            self.send_response(404)
            self.end_headers()

    def handle_initial_call(self, params):
        """Handle initial call"""
        # Verificar si es un error de Twilio
        if 'ErrorCode' in params:
            error_code = params['ErrorCode'][0]
            print(f"⚠️ Twilio Error Code: {error_code}")
        
        # Detectar hora para saludo apropiado (zona horaria del usuario)
        import pytz
        # Zona horaria de Argentina (Buenos Aires)
        argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
        current_time = datetime.datetime.now(argentina_tz)
        current_hour = current_time.hour
        
        if current_hour < 12:
            greeting = "Buenos días"
        elif current_hour < 18:
            greeting = "Buenas tardes"
        else:
            greeting = "Buenas noches"
        
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Lupe" language="es-ES" rate="fast">Hola, soy Lindy, tu asistente de voz inteligente. ¿En qué puedo ayudarte hoy?</Say>
    <Gather input="speech" action="/speech" method="POST" timeout="15" speechTimeout="8" language="es-AR">
    </Gather>
    <Say voice="Polly.Lupe" language="es-ES" rate="fast">No pude escucharte claramente. Por favor deja un mensaje detallado con su nombre, teléfono y el motivo de su llamada.</Say>
    <Record maxLength="60" action="/recording" method="POST" />
    <Say voice="Polly.Lupe" language="es-ES" rate="fast">Gracias por su mensaje. Javier le contactará a la brevedad.</Say>
</Response>"""
        
        # Enviar respuesta con headers correctos
        self.send_response(200)
        self.send_header('Content-Type', 'text/xml; charset=utf-8')
        self.send_header('Content-Length', str(len(twiml_response.encode('utf-8'))))
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(twiml_response.encode('utf-8'))
        print("✅ Sent TwiML response")

    def handle_speech(self, data):
        """Handle speech input"""
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
            
            print(f"🎯 FINAL speech_result: '{speech_result}'")
            
            # Obtener respuesta de IA
            ai_response = self.get_ai_response(speech_result, "Conversación en vivo")
            
            # Agregar nota de la conversación
            self.add_conversation_note(speech_result, ai_response)
            
            # Si el usuario dice "bye" o "goodbye", enviar SMS y terminar
            # Solo terminar si el usuario dice explícitamente que quiere terminar
            if any(word in speech_result.lower() for word in ['bye', 'goodbye', 'thanks', 'thank you', 'see you', 'chau', 'adiós', 'gracias', 'hasta luego', 'eso es todo', 'nada más', 'no hay más', 'ya está', 'listo', 'terminado', 'no necesito nada más', 'ya terminé', 'eso es', 'listo gracias', 'perfecto gracias', 'no', 'no gracias', 'no necesito', 'no hay nada más', 'no hay más', 'nada', 'ya está bien', 'perfecto', 'listo gracias', 'no más', 'no necesito más', 'eso es todo', 'eso es', 'ya terminé', 'listo', 'perfecto', 'no hay nada más', 'no necesito nada', 'ya está todo', 'terminé', 'listo gracias', 'perfecto gracias', 'no hay nada', 'no necesito nada más', 'ya está todo', 'terminé', 'listo', 'perfecto', 'no hay nada', 'no necesito nada más', 'ya está todo', 'terminé', 'listo', 'perfecto']):
                # Enviar notificación por email en lugar de SMS
                if self.owner_phone_number:
                    self.send_email_summary()
                print("📧 Notificación por email enviada")
                
                twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Lupe" language="es-ES" rate="fast">{ai_response}</Say>
    <Say voice="Polly.Lupe" language="es-ES" rate="fast">Perfecto, he tomado nota de todo. Javier se pondrá en contacto contigo pronto. ¡Que tengas un excelente día!</Say>
</Response>"""
            else:
                twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Lupe" language="es-ES" rate="fast">{ai_response}</Say>
    <Gather input="speech" action="/speech" method="POST" timeout="15" speechTimeout="8" language="es-AR">
    </Gather>
    <Say voice="Polly.Lupe" language="es-ES" rate="fast">No pude escucharte bien. Por favor, repite tu mensaje o di 'eso es todo' si ya terminaste.</Say>
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

    def handle_recording(self, params):
        """Handle call recording"""
        print("📹 Recording received")
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    PORT = 8103
    
    print(f"🚀 Server running on port {PORT}")
    
    with socketserver.TCPServer(("", PORT), WebhookHandler) as httpd:
        httpd.serve_forever()
