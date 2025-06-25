import Foundation

// MARK: - AI请求模型
struct AIRequest: Codable {
    let message: String
    let petId: String
    let petName: String
    let petPersonality: String
    let conversationHistory: [Message]
    let timestamp: Date
}

// MARK: - AI响应模型
struct AIResponse: Codable {
    let reply: String
    let mood: String
    let actions: [String]?
    let confidence: Double?
    let timestamp: Date
    
    init(reply: String, mood: String = "开心", actions: [String]? = nil, confidence: Double? = nil) {
        self.reply = reply
        self.mood = mood
        self.actions = actions
        self.confidence = confidence
        self.timestamp = Date()
    }
}

// MARK: - 聊天消息模型（用于数据存储）
struct ChatMessage: Codable, Identifiable {
    let id: String
    let petId: String
    let userId: String
    let content: String
    let type: MessageType
    let mood: String?
    let actions: [String]?
    let timestamp: Date
    let isRead: Bool
} 