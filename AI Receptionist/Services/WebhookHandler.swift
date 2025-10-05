//
//  WebhookHandler.swift
//  AI Receptionist
//
//  Created by Juan Gandarillas on 10/4/25.
//

import Foundation

class WebhookHandler {
    static let shared = WebhookHandler()
    
    private let callService = CallService.shared
    private let twilioService = TwilioService.shared
    
    private init() {}
    
    func handleIncomingCall(callSid: String, fromNumber: String, toNumber: String) async {
        // Process the incoming call
        await callService.processIncomingCall(
            fromNumber: fromNumber,
            toNumber: toNumber,
            callSid: callSid
        )
    }
    
    func handleRecording(callSid: String, recordingUrl: String) async {
        // Download and process the recording
        if let audioData = await downloadAudio(from: recordingUrl) {
            await callService.processAudioRecording(callSid: callSid, audioData: audioData)
        }
    }
    
    private func downloadAudio(from url: String) async -> Data? {
        guard let audioUrl = URL(string: url) else { return nil }
        
        do {
            let (data, _) = try await URLSession.shared.data(from: audioUrl)
            return data
        } catch {
            print("Error downloading audio: \(error)")
            return nil
        }
    }
}

// MARK: - Webhook URL Generation
extension WebhookHandler {
    func generateWebhookResponse(message: String) -> String {
        return twilioService.generateTwimlResponse(message: message)
    }
}
