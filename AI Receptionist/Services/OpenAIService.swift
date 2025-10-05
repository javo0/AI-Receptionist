//
//  OpenAIService.swift
//  AI Receptionist
//
//  Created by Juan Gandarillas on 10/4/25.
//

import Foundation
import Combine

class OpenAIService: ObservableObject {
    static let shared = OpenAIService()
    
    private let configurationService = ConfigurationService.shared
    
    private init() {}
    
    func generateResponse(for message: String) async throws -> String {
        guard let config = configurationService.configuration else {
            throw OpenAIError.configurationMissing
        }
        
        let systemPrompt = """
        Eres una recepcionista virtual profesional y amigable. Tu trabajo es:
        1. Saludar cordialmente a los visitantes
        2. Preguntar en qué puedes ayudar
        3. Proporcionar información básica sobre la empresa
        4. Tomar mensajes si es necesario
        5. Conectar con el personal apropiado si es requerido
        
        Mantén las respuestas breves, profesionales y útiles. Si no sabes algo, admítelo y ofrece tomar un mensaje.
        """
        
        let url = URL(string: "https://api.openai.com/v1/chat/completions")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(config.openaiApiKey ?? "")", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody: [String: Any] = [
            "model": "gpt-4",
            "messages": [
                ["role": "system", "content": systemPrompt],
                ["role": "user", "content": message]
            ],
            "max_tokens": 150
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw OpenAIError.noResponse
        }
        
        let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        guard let choices = json?["choices"] as? [[String: Any]],
              let firstChoice = choices.first,
              let message = firstChoice["message"] as? [String: Any],
              let content = message["content"] as? String else {
            throw OpenAIError.noResponse
        }
        
        return content
    }
    
    func transcribeAudio(from audioData: Data) async throws -> String {
        guard let config = configurationService.configuration else {
            throw OpenAIError.configurationMissing
        }
        
        let url = URL(string: "https://api.openai.com/v1/audio/transcriptions")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(config.openaiApiKey ?? "")", forHTTPHeaderField: "Authorization")
        
        let boundary = "Boundary-\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"recording.m4a\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: audio/m4a\r\n\r\n".data(using: .utf8)!)
        body.append(audioData)
        body.append("\r\n--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"model\"\r\n\r\n".data(using: .utf8)!)
        body.append("whisper-1".data(using: .utf8)!)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw OpenAIError.transcriptionFailed
        }
        
        let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        guard let text = json?["text"] as? String else {
            throw OpenAIError.transcriptionFailed
        }
        
        return text
    }
    
    func generateSpeech(from text: String) async throws -> Data {
        guard let config = configurationService.configuration else {
            throw OpenAIError.configurationMissing
        }
        
        let url = URL(string: "https://api.openai.com/v1/audio/speech")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(config.openaiApiKey ?? "")", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody: [String: Any] = [
            "model": "tts-1",
            "input": text,
            "voice": "alloy",
            "response_format": "mp3",
            "speed": 1.0
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw OpenAIError.speechGenerationFailed
        }
        
        return data
    }
    
    func updateConfiguration() {
        // No-op for now
    }
}

enum OpenAIError: Error, LocalizedError {
    case configurationMissing
    case noResponse
    case transcriptionFailed
    case speechGenerationFailed
    
    var errorDescription: String? {
        switch self {
        case .configurationMissing:
            return "OpenAI configuration is missing"
        case .noResponse:
            return "No response from OpenAI"
        case .transcriptionFailed:
            return "Failed to transcribe audio"
        case .speechGenerationFailed:
            return "Failed to generate speech"
        }
    }
}
