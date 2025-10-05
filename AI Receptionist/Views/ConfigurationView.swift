//
//  ConfigurationView.swift
//  AI Receptionist
//
//  Created by Juan Gandarillas on 10/4/25.
//

import SwiftUI

struct ConfigurationView: View {
    @StateObject private var configurationService = ConfigurationService.shared
    @StateObject private var webhookServer = WebhookServer.shared
    @State private var twilioAccountSid = ""
    @State private var twilioAuthToken = ""
    @State private var twilioPhoneNumber = ""
    @State private var openaiApiKey = ""
    @State private var claudeApiKey = ""
    @State private var aiProvider = "openai"
    @State private var webhookUrl = ""
    @State private var isActive = false
    @State private var showingAlert = false
    @State private var alertMessage = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section("Twilio Configuration") {
                    SecureField("Account SID", text: $twilioAccountSid)
                    SecureField("Auth Token", text: $twilioAuthToken)
                    TextField("Phone Number", text: $twilioPhoneNumber)
                        .keyboardType(.phonePad)
                }
                
                Section("AI Provider Selection") {
                    Picker("AI Provider", selection: $aiProvider) {
                        Text("OpenAI").tag("openai")
                        Text("Claude AI").tag("claude")
                    }
                    .pickerStyle(SegmentedPickerStyle())
                }
                
                Section("OpenAI Configuration") {
                    SecureField("OpenAI API Key", text: $openaiApiKey)
                        .disabled(aiProvider != "openai")
                }
                
                Section("Claude AI Configuration") {
                    SecureField("Claude API Key", text: $claudeApiKey)
                        .disabled(aiProvider != "claude")
                }
                
                Section("Webhook Configuration") {
                    TextField("Webhook URL", text: $webhookUrl)
                        .keyboardType(.URL)
                        .autocapitalization(.none)
                    
                    if webhookServer.isRunning {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Server Status: Running")
                                .foregroundColor(.green)
                            Text("URL: \(webhookServer.serverURL)")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        Button("Stop Server") {
                            webhookServer.stopServer()
                        }
                        .foregroundColor(.red)
                    } else {
                        Button("Start Webhook Server") {
                            webhookServer.startServer()
                        }
                        .foregroundColor(.blue)
                    }
                }
                
                Section("Status") {
                    Toggle("AI Receptionist Active", isOn: $isActive)
                        .onChange(of: isActive) { newValue in
                            configurationService.updateActiveStatus(newValue)
                        }
                }
                
                Section {
                    Button("Save Configuration") {
                        saveConfiguration()
                    }
                    .disabled(twilioAccountSid.isEmpty || twilioAuthToken.isEmpty || 
                             (aiProvider == "openai" && openaiApiKey.isEmpty) ||
                             (aiProvider == "claude" && claudeApiKey.isEmpty))
                }
            }
            .navigationTitle("Configuration")
            .onAppear {
                loadCurrentConfiguration()
            }
            .alert("Configuration", isPresented: $showingAlert) {
                Button("OK") { }
            } message: {
                Text(alertMessage)
            }
        }
    }
    
    private func loadCurrentConfiguration() {
        if let config = configurationService.configuration {
            twilioAccountSid = config.twilioAccountSid ?? ""
            twilioAuthToken = config.twilioAuthToken ?? ""
            twilioPhoneNumber = config.twilioPhoneNumber ?? ""
            openaiApiKey = config.openaiApiKey ?? ""
            claudeApiKey = config.claudeApiKey ?? ""
            aiProvider = config.aiProvider ?? "openai"
            webhookUrl = config.webhookUrl ?? ""
            isActive = config.isActive
        }
    }
    
    private func saveConfiguration() {
        // Use the webhook server URL if it's running, otherwise use the manual URL
        let finalWebhookUrl = webhookServer.isRunning ? webhookServer.serverURL : webhookUrl
        
        configurationService.saveConfiguration(
            twilioAccountSid: twilioAccountSid,
            twilioAuthToken: twilioAuthToken,
            twilioPhoneNumber: twilioPhoneNumber,
            openaiApiKey: openaiApiKey,
            claudeApiKey: claudeApiKey,
            aiProvider: aiProvider,
            webhookUrl: finalWebhookUrl
        )
        
        alertMessage = "Configuration saved successfully!"
        showingAlert = true
    }
}

#Preview {
    ConfigurationView()
}
