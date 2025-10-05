//
//  APIKeys.swift
//  AI Receptionist
//
//  Created by Juan Gandarillas on 10/4/25.
//

import Foundation

struct APIKeys {
    // MARK: - Twilio Configuration
    // Get these from your Twilio Console: https://console.twilio.com/
    static let twilioAccountSid = "YOUR_TWILIO_ACCOUNT_SID"
    static let twilioAuthToken = "YOUR_TWILIO_AUTH_TOKEN"
    static let twilioPhoneNumber = "YOUR_TWILIO_PHONE_NUMBER" // Format: +1234567890
    
    // MARK: - AI Provider Configuration
    // Choose between OpenAI or Claude AI
    static let aiProvider = "openai" // "openai" or "claude"
    
    // MARK: - OpenAI Configuration
    // Get this from your OpenAI account: https://platform.openai.com/api-keys
    static let openaiApiKey = "YOUR_OPENAI_API_KEY"
    
    // MARK: - Claude AI Configuration
    // Get this from your Anthropic account: https://console.anthropic.com/
    static let claudeApiKey = "YOUR_CLAUDE_API_KEY"
    
    // MARK: - Webhook Configuration
    // This should be your server URL where the webhook will be hosted
    // For development, use ngrok: https://ngrok.com/
    // For production, use a cloud service like Heroku, Railway, or Vercel
    static let webhookBaseUrl = "https://your-ngrok-url.ngrok.io" // Replace with your ngrok URL
    
    // MARK: - Instructions
    /*
     SETUP INSTRUCTIONS:
     
     1. TWILIO SETUP:
        - Go to https://console.twilio.com/
        - Create a new account or sign in
        - Get your Account SID and Auth Token from the dashboard
        - Purchase a phone number from the Phone Numbers section
        - Update the values above
     
     2. AI PROVIDER SETUP:
        
        OPENAI SETUP:
        - Go to https://platform.openai.com/
        - Create an account or sign in
        - Go to API Keys section
        - Create a new API key
        - Update the value above
        
        CLAUDE AI SETUP (Alternative):
        - Go to https://console.anthropic.com/
        - Create an account or sign in
        - Go to API Keys section
        - Create a new API key
        - Update the value above
        - Set aiProvider to "claude"
     
     3. WEBHOOK SETUP:
        - For development: Use ngrok to expose your local server
        - For production: Deploy to a cloud service (Heroku, AWS, etc.)
        - Update the webhook URL above
     
     4. TWILIO WEBHOOK CONFIGURATION:
        - In Twilio Console, go to Phone Numbers > Manage > Active Numbers
        - Click on your phone number
        - Set the webhook URL to: {your-webhook-url}/webhook/incoming
        - Set HTTP method to POST
     */
}
