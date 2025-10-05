//
//  ConfigurationService.swift
//  AI Receptionist
//
//  Created by Juan Gandarillas on 10/4/25.
//

import Foundation
import CoreData
import Combine

class ConfigurationService: ObservableObject {
    static let shared = ConfigurationService()
    
    @Published var configuration: Configuration?
    @Published var isConfigured = false
    
    private let persistenceController = PersistenceController.shared
    
    private init() {
        loadConfiguration()
    }
    
    func loadConfiguration() {
        let request: NSFetchRequest<Configuration> = Configuration.fetchRequest()
        request.fetchLimit = 1
        
        do {
            let configurations = try persistenceController.container.viewContext.fetch(request)
            if let config = configurations.first {
                self.configuration = config
                self.isConfigured = !(config.twilioAccountSid?.isEmpty ?? true) && 
                                  !(config.twilioAuthToken?.isEmpty ?? true) && 
                                  !(config.openaiApiKey?.isEmpty ?? true)
            }
        } catch {
            print("Error loading configuration: \(error)")
        }
    }
    
    func saveConfiguration(
        twilioAccountSid: String,
        twilioAuthToken: String,
        twilioPhoneNumber: String,
        openaiApiKey: String,
        claudeApiKey: String,
        aiProvider: String,
        webhookUrl: String
    ) {
        let context = persistenceController.container.viewContext
        
        // Delete existing configuration
        if let existingConfig = configuration {
            context.delete(existingConfig)
        }
        
        // Create new configuration
        let newConfig = Configuration(context: context)
        newConfig.twilioAccountSid = twilioAccountSid
        newConfig.twilioAuthToken = twilioAuthToken
        newConfig.twilioPhoneNumber = twilioPhoneNumber
        newConfig.openaiApiKey = openaiApiKey
        newConfig.claudeApiKey = claudeApiKey
        newConfig.aiProvider = aiProvider
        newConfig.webhookUrl = webhookUrl
        newConfig.isActive = true
        
        do {
            try context.save()
            self.configuration = newConfig
            self.isConfigured = true
        } catch {
            print("Error saving configuration: \(error)")
        }
    }
    
    func updateActiveStatus(_ isActive: Bool) {
        guard let config = configuration else { return }
        
        config.isActive = isActive
        
        do {
            try persistenceController.container.viewContext.save()
        } catch {
            print("Error updating active status: \(error)")
        }
    }
}
