//
//  TwilioService.swift
//  AI Receptionist
//
//  Created by Juan Gandarillas on 10/4/25.
//

import Foundation

class TwilioService {
    static let shared = TwilioService()
    
    private let configurationService = ConfigurationService.shared
    
    private init() {}
    
    func sendSMS(to phoneNumber: String, message: String) async throws {
        guard let config = configurationService.configuration else {
            throw TwilioError.configurationMissing
        }
        
        let url = URL(string: "https://api.twilio.com/2010-04-01/Accounts/\(config.twilioAccountSid ?? "")/Messages.json")!
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let credentials = "\(config.twilioAccountSid ?? ""):\(config.twilioAuthToken ?? "")"
        let encodedCredentials = Data(credentials.utf8).base64EncodedString()
        
        request.setValue("Basic \(encodedCredentials)", forHTTPHeaderField: "Authorization")
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let body = "To=\(phoneNumber)&From=\(config.twilioPhoneNumber ?? "")&Body=\(message)"
        request.httpBody = body.data(using: .utf8)
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw TwilioError.networkError
        }
        
        if httpResponse.statusCode != 201 {
            throw TwilioError.apiError(httpResponse.statusCode)
        }
    }
    
    func makeCall(to phoneNumber: String, twimlUrl: String) async throws {
        guard let config = configurationService.configuration else {
            throw TwilioError.configurationMissing
        }
        
        let url = URL(string: "https://api.twilio.com/2010-04-01/Accounts/\(config.twilioAccountSid ?? "")/Calls.json")!
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let credentials = "\(config.twilioAccountSid ?? ""):\(config.twilioAuthToken ?? "")"
        let encodedCredentials = Data(credentials.utf8).base64EncodedString()
        
        request.setValue("Basic \(encodedCredentials)", forHTTPHeaderField: "Authorization")
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let body = "To=\(phoneNumber)&From=\(config.twilioPhoneNumber ?? "")&Url=\(twimlUrl)"
        request.httpBody = body.data(using: .utf8)
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw TwilioError.networkError
        }
        
        if httpResponse.statusCode != 201 {
            throw TwilioError.apiError(httpResponse.statusCode)
        }
    }
    
    func generateTwimlResponse(message: String) -> String {
        return """
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="alice">\(message)</Say>
            <Pause length="1"/>
            <Say voice="alice">¿Hay algo más en lo que pueda ayudarte?</Say>
            <Record timeout="10" maxLength="30" action="\(configurationService.configuration?.webhookUrl ?? "")/process-recording" method="POST"/>
        </Response>
        """
    }
}

enum TwilioError: Error, LocalizedError {
    case configurationMissing
    case networkError
    case apiError(Int)
    
    var errorDescription: String? {
        switch self {
        case .configurationMissing:
            return "Twilio configuration is missing"
        case .networkError:
            return "Network error occurred"
        case .apiError(let code):
            return "Twilio API error with code: \(code)"
        }
    }
}
