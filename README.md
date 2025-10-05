# AI Receptionist - Recepcionista Virtual

Una aplicación iOS que utiliza Twilio y OpenAI para crear una recepcionista virtual inteligente que puede manejar llamadas telefónicas de forma automática.

## 🚀 Características

- **Llamadas Automáticas**: Recibe y maneja llamadas telefónicas usando Twilio
- **IA Conversacional**: Utiliza OpenAI GPT-4 para generar respuestas inteligentes
- **Transcripción de Audio**: Convierte audio a texto usando Whisper
- **Síntesis de Voz**: Convierte respuestas de texto a audio usando TTS
- **Historial de Llamadas**: Almacena y visualiza todas las conversaciones
- **Interfaz Intuitiva**: Dashboard moderno para monitorear el sistema

## 📋 Requisitos Previos

### Cuentas Necesarias
1. **Twilio Account** - Para manejo de llamadas telefónicas
2. **OpenAI Account** - Para IA conversacional y procesamiento de audio
3. **Apple Developer Account** - Para desarrollo iOS

### Software Requerido
- Xcode 15.0+
- iOS 17.0+
- Swift 5.9+

## 🛠️ Configuración

### 1. Configuración de Twilio

1. Ve a [Twilio Console](https://console.twilio.com/)
2. Crea una cuenta o inicia sesión
3. Obtén tu **Account SID** y **Auth Token** del dashboard
4. Compra un número de teléfono en la sección Phone Numbers
5. Configura el webhook URL en la configuración del número

### 2. Configuración de OpenAI

1. Ve a [OpenAI Platform](https://platform.openai.com/)
2. Crea una cuenta o inicia sesión
3. Ve a la sección API Keys
4. Crea una nueva API key
5. Asegúrate de tener créditos en tu cuenta

### 3. Configuración del Proyecto

1. Abre el proyecto en Xcode
2. Ve a `Config/APIKeys.swift`
3. Actualiza las siguientes variables:
   ```swift
   static let twilioAccountSid = "TU_TWILIO_ACCOUNT_SID"
   static let twilioAuthToken = "TU_TWILIO_AUTH_TOKEN"
   static let twilioPhoneNumber = "TU_NUMERO_TWILIO" // Formato: +1234567890
   static let openaiApiKey = "TU_OPENAI_API_KEY"
   static let webhookBaseUrl = "TU_URL_WEBHOOK"
   ```

### 4. Configuración del Webhook

Para desarrollo local:
1. Instala [ngrok](https://ngrok.com/)
2. Ejecuta: `ngrok http 8080`
3. Copia la URL HTTPS generada
4. Configura esta URL en Twilio como webhook

Para producción:
1. Despliega el servidor webhook en un servicio en la nube
2. Configura la URL de producción en Twilio

## 🏗️ Arquitectura

### Servicios Principales

- **ConfigurationService**: Maneja la configuración de API keys
- **TwilioService**: Gestiona llamadas y SMS
- **OpenAIService**: Procesa conversaciones y audio
- **CallService**: Coordina el flujo de llamadas
- **WebhookHandler**: Maneja webhooks de Twilio

### Modelos de Datos

- **Call**: Información de llamadas telefónicas
- **Conversation**: Registro de conversaciones
- **Configuration**: Configuración del sistema

## 📱 Uso

### Configuración Inicial
1. Abre la aplicación
2. Ve a la pestaña "Settings"
3. Ingresa tus credenciales de Twilio y OpenAI
4. Activa el sistema

### Monitoreo
- **Dashboard**: Vista general del estado del sistema
- **Calls**: Historial de llamadas y conversaciones
- **Settings**: Configuración y credenciales

## 🔧 Desarrollo

### Estructura del Proyecto
```
AI Receptionist/
├── Services/           # Servicios de negocio
├── Views/             # Interfaces de usuario
├── Config/            # Configuración
├── Models/            # Modelos de datos (Core Data)
└── Resources/         # Recursos de la aplicación
```

### Dependencias
- **Twilio Voice iOS SDK**: Para manejo de llamadas
- **OpenAI Swift SDK**: Para IA conversacional
- **Alamofire**: Para networking
- **Core Data**: Para persistencia de datos

## 🚨 Solución de Problemas

### Errores Comunes

1. **"Configuration Missing"**
   - Verifica que las API keys estén configuradas correctamente
   - Asegúrate de que las credenciales sean válidas

2. **"Webhook Error"**
   - Verifica que la URL del webhook sea accesible
   - Asegúrate de que el servidor esté ejecutándose

3. **"OpenAI API Error"**
   - Verifica que la API key sea válida
   - Asegúrate de tener créditos en tu cuenta OpenAI

### Logs de Depuración
Los logs se muestran en la consola de Xcode. Busca mensajes que comiencen con:
- `[TwilioService]`
- `[OpenAIService]`
- `[CallService]`

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Si tienes problemas o preguntas:
1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

**Nota**: Este es un proyecto de demostración. Para uso en producción, considera implementar medidas de seguridad adicionales y manejo de errores más robusto.

