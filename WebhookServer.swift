//
//  WebhookServer.swift
//  AI Receptionist - Webhook Server
//
//  Created by Juan Gandarillas on 10/4/25.
//

import Foundation
import Network

class WebhookServer: ObservableObject {
    static let shared = WebhookServer()
    
    @Published var isRunning = false
    @Published var serverURL: String = ""
    
    private var listener: NWListener?
    private let port: UInt16 = 8080
    
    private init() {}
    
    func startServer() {
        let parameters = NWParameters.tcp
        let listener = try! NWListener(using: parameters, on: NWEndpoint.Port(integerLiteral: port))
        
        listener.newConnectionHandler = { [weak self] connection in
            self?.handleConnection(connection)
        }
        
        listener.start(queue: .global())
        self.listener = listener
        self.isRunning = true
        
        // Get local IP address
        if let localIP = getLocalIPAddress() {
            self.serverURL = "http://\(localIP):\(port)"
        }
        
        print("🚀 Webhook server started at: \(serverURL)")
    }
    
    func stopServer() {
        listener?.cancel()
        listener = nil
        isRunning = false
        serverURL = ""
    }
    
    private func handleConnection(_ connection: NWConnection) {
        connection.start(queue: .global())
        
        connection.receive(minimumIncompleteLength: 1, maximumLength: 65536) { [weak self] data, _, isComplete, error in
            if let data = data, !data.isEmpty {
                self?.processWebhookData(data)
            }
            
            if isComplete {
                connection.cancel()
            }
        }
    }
    
    private func processWebhookData(_ data: Data) {
        guard let requestString = String(data: data, encoding: .utf8) else { return }
        
        print("📞 Received webhook data: \(requestString)")
        
        // Parse Twilio webhook parameters
        let parameters = parseWebhookParameters(requestString)
        
        if let callSid = parameters["CallSid"],
           let from = parameters["From"],
           let to = parameters["To"] {
            
            print("📞 Processing call: \(callSid) from \(from) to \(to)")
            
            // Handle the incoming call
            Task {
                await WebhookHandler.shared.handleIncomingCall(
                    callSid: callSid,
                    fromNumber: from,
                    toNumber: to
                )
            }
        }
    }
    
    private func parseWebhookParameters(_ requestString: String) -> [String: String] {
        var parameters: [String: String] = [:]
        
        // Simple URL parameter parsing
        let components = requestString.components(separatedBy: "&")
        for component in components {
            let keyValue = component.components(separatedBy: "=")
            if keyValue.count == 2 {
                let key = keyValue[0].removingPercentEncoding ?? keyValue[0]
                let value = keyValue[1].removingPercentEncoding ?? keyValue[1]
                parameters[key] = value
            }
        }
        
        return parameters
    }
    
    private func getLocalIPAddress() -> String? {
        var address: String?
        var ifaddr: UnsafeMutablePointer<ifaddrs>?
        
        guard getifaddrs(&ifaddr) == 0 else { return nil }
        guard let firstAddr = ifaddr else { return nil }
        
        for ifptr in sequence(first: firstAddr, next: { $0.pointee.ifa_next }) {
            let interface = ifptr.pointee
            
            // Check for IPv4 or IPv6 interface
            let addrFamily = interface.ifa_addr.pointee.sa_family
            if addrFamily == UInt8(AF_INET) || addrFamily == UInt8(AF_INET6) {
                
                // Check interface name
                let name = String(cString: interface.ifa_name)
                if name == "en0" { // WiFi interface
                    var hostname = [CChar](repeating: 0, count: Int(NI_MAXHOST))
                    getnameinfo(interface.ifa_addr, socklen_t(interface.ifa_addr.pointee.sa_len),
                              &hostname, socklen_t(hostname.count),
                              nil, socklen_t(0), NI_NUMERICHOST)
                    address = String(cString: hostname)
                }
            }
        }
        
        freeifaddrs(ifaddr)
        return address
    }
}

// MARK: - HTTP Response
extension WebhookServer {
    func generateTwimlResponse(message: String) -> String {
        return """
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="alice" language="es-MX">\(message)</Say>
            <Record maxLength="30" action="/recording" method="POST" />
        </Response>
        """
    }
}

