//
//  ClaudeService.swift
//  AI Receptionist
//
//  Created by Juan Gandarillas on 10/4/25.
//

import Foundation
import Combine

class ClaudeService: ObservableObject {
    static let shared = ClaudeService()
    
    private let configurationService = ConfigurationService.shared
    
    private init() {}
    
    func generateResponse(for message: String) async throws -> String {
        guard let config = configurationService.configuration else {
            throw ClaudeError.configurationMissing
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
        
        let url = URL(string: "https://api.anthropic.com/v1/messages")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("x-api-key: \(config.claudeApiKey ?? "")", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("anthropic-version: 2023-06-01", forHTTPHeaderField: "anthropic-version")
        
        let requestBody: [String: Any] = [
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 150,
            "system": systemPrompt,
            "messages": [
                [
                    "role": "user",
                    "content": message
                ]
            ]
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw ClaudeError.noResponse
        }
        
        let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        guard let content = json?["content"] as? [[String: Any]],
              let firstContent = content.first,
              let text = firstContent["text"] as? String else {
            throw ClaudeError.noResponse
        }
        
        return text
    }
    
    func transcribeAudio(from audioData: Data) async throws -> String {
        guard let config = configurationService.configuration else {
            throw ClaudeError.configurationMissing
        }
        
        let url = URL(string: "https://api.anthropic.com/v1/messages")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("x-api-key: \(config.claudeApiKey ?? "")", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("anthropic-version: 2023-06-01", forHTTPHeaderField: "anthropic-version")
        
        // Convert audio to base64
        let base64Audio = audioData.base64EncodedString()
        
        let requestBody: [String: Any] = [
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1000,
            "messages": [
                [
                    "role": "user",
                    "content": [
                        [
                            "type": "text",
                            "text": "Transcribe this audio message accurately."
                        ],
                        [
                            "type": "audio",
                            "source": [
                                "type": "base64",
                                "media_type": "audio/m4a",
                                "data": base64Audio
                            ]
                        ]
                    ]
                ]
            ]
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw ClaudeError.transcriptionFailed
        }
        
        let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        guard let content = json?["content"] as? [[String: Any]],
              let firstContent = content.first,
              let text = firstContent["text"] as? String else {
            throw ClaudeError.transcriptionFailed
        }
        
        return text
    }
    
    func generateSpeech(from text: String) async throws -> Data {
        // Claude doesn't have native TTS, so we'll use a fallback
        // In a real implementation, you might use a different TTS service
        // or keep using OpenAI's TTS for speech generation
        
        guard let config = configurationService.configuration else {
            throw ClaudeError.configurationMissing
        }
        
        // For now, we'll use a simple text-to-speech approach
        // You could integrate with Azure Speech, Google TTS, or keep OpenAI TTS
        throw ClaudeError.speechGenerationNotSupported
    }
    
    func updateConfiguration() {
        // No-op for now
    }
}

enum ClaudeError: Error, LocalizedError {
    case configurationMissing
    case noResponse
    case transcriptionFailed
    case speechGenerationNotSupported
    
    var errorDescription: String? {
        switch self {
        case .configurationMissing:
            return "Claude configuration is missing"
        case .noResponse:
            return "No response from Claude"
        case .transcriptionFailed:
            return "Failed to transcribe audio"
        case .speechGenerationNotSupported:
            return "Speech generation not supported by Claude API"
        }
    }
}
