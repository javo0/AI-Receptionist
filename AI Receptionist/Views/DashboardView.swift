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
            // Dashboard Tab - M1 Style
            ScrollView {
                VStack(spacing: 24) {
                    // Header Section - M1 Style
                    VStack(spacing: 16) {
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("M1 AI Receptionist")
                                    .font(.largeTitle)
                                    .fontWeight(.bold)
                                    .foregroundColor(.primary)
                                
                                Text("Your 24/7 AI Receptionist")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                            
                            Spacer()
                            
                            // Status Indicator
                            VStack(spacing: 4) {
                                StatusIndicator(isActive: configurationService.configuration?.isActive ?? false)
                                Text(configurationService.configuration?.isActive == true ? "Active" : "Inactive")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                        
                        // System Status Card - M1 Style
                        HStack {
                            Image(systemName: configurationService.isConfigured ? "checkmark.circle.fill" : "exclamationmark.triangle.fill")
                                .foregroundColor(configurationService.isConfigured ? .green : .orange)
                                .font(.title2)
                            
                            VStack(alignment: .leading, spacing: 2) {
                                Text("System Status")
                                    .font(.headline)
                                    .foregroundColor(.primary)
                                Text(configurationService.isConfigured ? "Configured & Ready" : "Needs Configuration")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                            
                            Spacer()
                        }
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 16)
                                .fill(Color(.systemBackground))
                                .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 2)
                        )
                    }
                
                    // Stats Section - M1 Style
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Today's Activity")
                            .font(.headline)
                            .foregroundColor(.primary)
                        
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
                    }
                
                    // Quick Actions - M1 Style
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Quick Actions")
                            .font(.headline)
                            .foregroundColor(.primary)
                        
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
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .fill(Color(.systemBackground))
                            .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 2)
                    )
                }
                .padding()
            }
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
        VStack(spacing: 12) {
            HStack {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Spacer()
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(value)
                    .font(.title)
                    .fontWeight(.bold)
                    .foregroundColor(.primary)
                
                Text(title)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color(.systemBackground))
                .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 2)
        )
    }
}

struct QuickActionButton: View {
    let title: String
    let icon: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 12) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .foregroundColor(.primary)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color(.systemGray6))
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(color.opacity(0.3), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

#Preview {
    DashboardView()
}
