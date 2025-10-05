//
//  ContentView.swift
//  AI Receptionist
//
//  Created by Juan Gandarillas on 10/4/25.
//

import SwiftUI
import CoreData

struct ContentView: View {
    @Environment(\.managedObjectContext) private var viewContext

    var body: some View {
        DashboardView()
            .environment(\.managedObjectContext, viewContext)
    }
}

#Preview {
    ContentView().environment(\.managedObjectContext, PersistenceController.preview.container.viewContext)
}
