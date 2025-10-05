//
//  DashboardView.swift
//  AI Receptionist
//
//  Created by Juan Gandarillas on 10/4/25.
//

import SwiftUI

struct DashboardView: View {
    @StateObject private var configurationService = ConfigurationService.shared
    @StateObject private var callService = CallService.shared
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Dashboard Tab
            VStack(spacing: 20) {
                // Status Card
                VStack(spacing: 16) {
                    HStack {
                        Image(systemName: configurationService.isConfigured ? "checkmark.circle.fill" : "exclamationmark.triangle.fill")
                            .foregroundColor(configurationService.isConfigured ? .green : .orange)
                            .font(.title2)
                        
                        VStack(alignment: .leading) {
                            Text("AI Receptionist Status")
                                .font(.headline)
                            Text(configurationService.isConfigured ? "Configured & Ready" : "Needs Configuration")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                    }
                    
                    if configurationService.isConfigured {
                        HStack {
                            StatusIndicator(isActive: configurationService.configuration?.isActive ?? false)
                            Text(configurationService.configuration?.isActive == true ? "Active" : "Inactive")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                        }
                    }
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
                
                // Stats Cards
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 16) {
                    StatCard(
                        title: "Active Calls",
                        value: "\(callService.activeCalls.count)",
                        icon: "phone.fill",
                        color: .green
                    )
                    
                    StatCard(
                        title: "Total Calls",
                        value: "\(callService.callHistory.count)",
                        icon: "phone.arrow.up.right.fill",
                        color: .blue
                    )
                }
                
                // Quick Actions
                VStack(alignment: .leading, spacing: 12) {
                    Text("Quick Actions")
                        .font(.headline)
                    
                    HStack(spacing: 16) {
                        QuickActionButton(
                            title: "View Calls",
                            icon: "phone.fill",
                            color: .blue
                        ) {
                            selectedTab = 1
                        }
                        
                        QuickActionButton(
                            title: "Settings",
                            icon: "gear.fill",
                            color: .gray
                        ) {
                            selectedTab = 2
                        }
                    }
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
                
                Spacer()
            }
            .padding()
            .tabItem {
                Image(systemName: "house.fill")
                Text("Dashboard")
            }
            .tag(0)
            
            // Call History Tab
            CallHistoryView()
                .tabItem {
                    Image(systemName: "phone.fill")
                    Text("Calls")
                }
                .tag(1)
            
            // Configuration Tab
            ConfigurationView()
                .tabItem {
                    Image(systemName: "gearshape.fill")
                    Text("Settings")
                }
                .tag(2)
        }
        .onAppear {
            callService.loadCallHistory()
        }
    }
}

struct StatusIndicator: View {
    let isActive: Bool
    
    var body: some View {
        Circle()
            .fill(isActive ? Color.green : Color.red)
            .frame(width: 12, height: 12)
            .overlay(
                Circle()
                    .stroke(Color.white, lineWidth: 2)
            )
    }
}

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(value)
                .font(.title)
                .fontWeight(.bold)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

struct QuickActionButton: View {
    let title: String
    let icon: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Text(title)
                    .font(.caption)
                    .foregroundColor(.primary)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color(.systemGray5))
            .cornerRadius(8)
        }
    }
}

#Preview {
    DashboardView()
}
