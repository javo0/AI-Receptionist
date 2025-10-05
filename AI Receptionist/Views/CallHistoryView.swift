//
//  CallHistoryView.swift
//  AI Receptionist
//
//  Created by Juan Gandarillas on 10/4/25.
//

import SwiftUI

struct CallHistoryView: View {
    @StateObject private var callService = CallService.shared
    @State private var selectedCall: Call?
    
    var body: some View {
        NavigationView {
            List {
                if !callService.activeCalls.isEmpty {
                    Section("Active Calls") {
                        ForEach(callService.activeCalls, id: \.callSid) { call in
                            CallRowView(call: call, isActive: true)
                                .onTapGesture {
                                    selectedCall = call
                                }
                        }
                    }
                }
                
                Section("Call History") {
                    ForEach(callService.callHistory, id: \.callSid) { call in
                        CallRowView(call: call, isActive: false)
                            .onTapGesture {
                                selectedCall = call
                            }
                    }
                }
            }
            .navigationTitle("Call History")
            .refreshable {
                callService.loadCallHistory()
            }
            .sheet(item: $selectedCall) { call in
                CallDetailView(call: call)
            }
        }
    }
}

struct CallRowView: View {
    let call: Call
    let isActive: Bool
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(call.fromNumber ?? "Unknown")
                    .font(.headline)
                Spacer()
                if isActive {
                    Circle()
                        .fill(Color.green)
                        .frame(width: 8, height: 8)
                }
            }
            
            Text("To: \(call.toNumber ?? "Unknown")")
                .font(.caption)
                .foregroundColor(.secondary)
            
            Text(call.startTime ?? Date(), style: .time)
                .font(.caption)
                .foregroundColor(.secondary)
            
            if call.duration > 0 {
                Text("Duration: \(formatDuration(Int(call.duration)))")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 2)
    }
    
    private func formatDuration(_ seconds: Int) -> String {
        let minutes = seconds / 60
        let remainingSeconds = seconds % 60
        return String(format: "%d:%02d", minutes, remainingSeconds)
    }
}

struct CallDetailView: View {
    let call: Call
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    // Call Information
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Call Information")
                            .font(.headline)
                        
                        InfoRow(label: "From", value: call.fromNumber ?? "Unknown")
                        InfoRow(label: "To", value: call.toNumber ?? "Unknown")
                        InfoRow(label: "Status", value: call.status ?? "Unknown")
                        InfoRow(label: "Start Time", value: call.startTime?.formatted() ?? "Unknown")
                        
                        if let endTime = call.endTime {
                            InfoRow(label: "End Time", value: endTime.formatted())
                        }
                        
                        if call.duration > 0 {
                            InfoRow(label: "Duration", value: formatDuration(Int(call.duration)))
                        }
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
                    
                    // Conversations
                    if let conversations = call.conversations?.allObjects as? [Conversation], !conversations.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Conversation")
                                .font(.headline)
                            
                            ForEach(conversations.sorted(by: { $0.timestamp ?? Date() < $1.timestamp ?? Date() }), id: \.timestamp) { conversation in
                                ConversationView(conversation: conversation)
                            }
                        }
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(8)
                    }
                }
                .padding()
            }
            .navigationTitle("Call Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    private func formatDuration(_ seconds: Int) -> String {
        let minutes = seconds / 60
        let remainingSeconds = seconds % 60
        return String(format: "%d:%02d", minutes, remainingSeconds)
    }
}

struct InfoRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label + ":")
                .fontWeight(.medium)
            Spacer()
            Text(value)
                .foregroundColor(.secondary)
        }
    }
}

struct ConversationView: View {
    let conversation: Conversation
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            if let userMessage = conversation.userMessage, !userMessage.isEmpty {
                HStack {
                    Spacer()
                    Text(userMessage)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
            }
            
            if let aiResponse = conversation.aiResponse, !aiResponse.isEmpty {
                HStack {
                    Text(aiResponse)
                        .padding()
                        .background(Color(.systemGray5))
                        .cornerRadius(12)
                    Spacer()
                }
            }
            
            Text(conversation.timestamp ?? Date(), style: .time)
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
}

#Preview {
    CallHistoryView()
}
