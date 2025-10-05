//
//  AI_ReceptionistApp.swift
//  AI Receptionist
//
//  Created by Juan Gandarillas on 10/4/25.
//

import SwiftUI
import CoreData

@main
struct AI_ReceptionistApp: App {
    let persistenceController = PersistenceController.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
        }
    }
}
