//
//  CallService.swift
//  AI Receptionist
//
//  Created by Juan Gandarillas on 10/4/25.
//

import Foundation
import CoreData
import Combine

class CallService: ObservableObject {
    static let shared = CallService()
    
    @Published var activeCalls: [Call] = []
    @Published var callHistory: [Call] = []
    
    private let persistenceController = PersistenceController.shared
    private let twilioService = TwilioService.shared
    private let openAIService = OpenAIService.shared
    private let claudeService = ClaudeService.shared
    private let configurationService = ConfigurationService.shared
    
    private init() {
        loadCallHistory()
    }
    
    func loadCallHistory() {
        let request: NSFetchRequest<Call> = Call.fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Call.startTime, ascending: false)]
        
        do {
            callHistory = try persistenceController.container.viewContext.fetch(request)
        } catch {
            print("Error loading call history: \(error)")
        }
    }
    
    func createCall(fromNumber: String, toNumber: String, callSid: String) -> Call {
        let context = persistenceController.container.viewContext
        let call = Call(context: context)
        
        call.callSid = callSid
        call.fromNumber = fromNumber
        call.toNumber = toNumber
        call.status = "in-progress"
        call.startTime = Date()
        
        do {
            try context.save()
            activeCalls.append(call)
            loadCallHistory()
        } catch {
            print("Error creating call: \(error)")
        }
        
        return call
    }
    
    func endCall(callSid: String) {
        let request: NSFetchRequest<Call> = Call.fetchRequest()
        request.predicate = NSPredicate(format: "callSid == %@", callSid)
        
        do {
            let calls = try persistenceController.container.viewContext.fetch(request)
            if let call = calls.first {
                call.status = "completed"
                call.endTime = Date()
                call.duration = Int32(Date().timeIntervalSince(call.startTime ?? Date()))
                
                try persistenceController.container.viewContext.save()
                
                // Remove from active calls
                activeCalls.removeAll { $0.callSid == callSid }
                loadCallHistory()
            }
        } catch {
            print("Error ending call: \(error)")
        }
    }
    
    func processIncomingCall(fromNumber: String, toNumber: String, callSid: String) async {
        let call = createCall(fromNumber: fromNumber, toNumber: toNumber, callSid: callSid)
        
        // Generate initial greeting
        do {
            let greeting = try await generateAIResponse(for: "Saluda al visitante que acaba de llamar")
            let twiml = twilioService.generateTwimlResponse(message: greeting)
            
            // In a real implementation, you would send this TwiML to Twilio
            print("TwiML Response: \(twiml)")
            
        } catch {
            print("Error processing incoming call: \(error)")
        }
    }
    
    func processUserMessage(callSid: String, message: String) async {
        // Find the call
        let request: NSFetchRequest<Call> = Call.fetchRequest()
        request.predicate = NSPredicate(format: "callSid == %@", callSid)
        
        do {
            let calls = try persistenceController.container.viewContext.fetch(request)
            guard let call = calls.first else { return }
            
            // Create conversation record
            let conversation = Conversation(context: persistenceController.container.viewContext)
            conversation.call = call
            conversation.timestamp = Date()
            conversation.userMessage = message
            
            // Generate AI response
            let aiResponse = try await generateAIResponse(for: message)
            conversation.aiResponse = aiResponse
            
            // Generate TwiML response
            let twiml = twilioService.generateTwimlResponse(message: aiResponse)
            
            try persistenceController.container.viewContext.save()
            
            // In a real implementation, you would send this TwiML to Twilio
            print("TwiML Response: \(twiml)")
            
        } catch {
            print("Error processing user message: \(error)")
        }
    }
    
    func processAudioRecording(callSid: String, audioData: Data) async {
        do {
            // Transcribe audio
            let transcription = try await transcribeAudio(audioData)
            
            // Process the transcribed message
            await processUserMessage(callSid: callSid, message: transcription)
            
        } catch {
            print("Error processing audio recording: \(error)")
        }
    }
    
    // MARK: - AI Provider Selection
    private func generateAIResponse(for message: String) async throws -> String {
        guard let config = configurationService.configuration else {
            throw NSError(domain: "CallService", code: 1, userInfo: [NSLocalizedDescriptionKey: "Configuration missing"])
        }
        
        switch config.aiProvider {
        case "claude":
            return try await claudeService.generateResponse(for: message)
        default:
            return try await openAIService.generateResponse(for: message)
        }
    }
    
    private func transcribeAudio(_ audioData: Data) async throws -> String {
        guard let config = configurationService.configuration else {
            throw NSError(domain: "CallService", code: 1, userInfo: [NSLocalizedDescriptionKey: "Configuration missing"])
        }
        
        switch config.aiProvider {
        case "claude":
            return try await claudeService.transcribeAudio(from: audioData)
        default:
            return try await openAIService.transcribeAudio(from: audioData)
        }
    }
}
