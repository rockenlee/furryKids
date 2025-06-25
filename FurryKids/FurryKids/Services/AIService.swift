import Foundation
import Combine

// MARK: - AI Service Models
struct AIRequest: Codable {
    let message: String
    let petId: String
    let petName: String
    let petPersonality: String
    let conversationHistory: [Message]
    let timestamp: Date
}

struct AIResponse: Codable {
    let reply: String
    let mood: String
    let confidence: Double
    let actions: [String]?
    let emotions: [String]?
}

struct OpenAIMessage: Codable {
    let role: String
    let content: String
}

struct OpenAIRequest: Codable {
    let model: String
    let messages: [OpenAIMessage]
    let temperature: Double
    let maxTokens: Int
    let topP: Double
    
    enum CodingKeys: String, CodingKey {
        case model, messages, temperature
        case maxTokens = "max_tokens"
        case topP = "top_p"
    }
}

struct OpenAIResponse: Codable {
    let id: String
    let object: String
    let created: Int
    let model: String
    let choices: [OpenAIChoice]
    let usage: OpenAIUsage
}

struct OpenAIChoice: Codable {
    let index: Int
    let message: OpenAIMessage
    let finishReason: String
    
    enum CodingKeys: String, CodingKey {
        case index, message
        case finishReason = "finish_reason"
    }
}

struct OpenAIUsage: Codable {
    let promptTokens: Int
    let completionTokens: Int
    let totalTokens: Int
    
    enum CodingKeys: String, CodingKey {
        case promptTokens = "prompt_tokens"
        case completionTokens = "completion_tokens"
        case totalTokens = "total_tokens"
    }
}

// MARK: - AI Service Protocol
protocol AIServiceProtocol {
    func sendMessage(_ request: AIRequest) -> AnyPublisher<AIResponse, APIError>
}

// MARK: - AI Service Implementation
class AIService: AIServiceProtocol {
    static let shared = AIService()
    
    private let networkManager = NetworkManager.shared
    private var cancellables = Set<AnyCancellable>()
    
    private init() {}
    
    // MARK: - Main AI Service Method
    func sendMessage(_ request: AIRequest) -> AnyPublisher<AIResponse, APIError> {
        
        // 根据配置选择AI服务提供商
        #if DEBUG
        // 开发环境使用模拟AI
        return simulateAIResponse(request)
        #else
        // 生产环境使用真实AI服务
        return useOpenAI(request)
        #endif
    }
    
    // MARK: - OpenAI Integration
    private func useOpenAI(_ request: AIRequest) -> AnyPublisher<AIResponse, APIError> {
        
        let systemPrompt = createSystemPrompt(petName: request.petName, personality: request.petPersonality)
        let conversationMessages = createConversationMessages(history: request.conversationHistory, newMessage: request.message)
        
        var messages: [OpenAIMessage] = [
            OpenAIMessage(role: "system", content: systemPrompt)
        ]
        messages.append(contentsOf: conversationMessages)
        
        let openAIRequest = OpenAIRequest(
            model: "gpt-3.5-turbo",
            messages: messages,
            temperature: 0.8,
            maxTokens: 200,
            topP: 1.0
        )
        
        guard let requestData = try? JSONEncoder().encode(openAIRequest) else {
            return Fail(error: APIError.decodingError)
                .eraseToAnyPublisher()
        }
        
        guard let url = URL(string: "\(APIConfig.openAIURL)/chat/completions") else {
            return Fail(error: APIError.invalidURL)
                .eraseToAnyPublisher()
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(APIConfig.openAIKey)", forHTTPHeaderField: "Authorization")
        urlRequest.httpBody = requestData
        
        return URLSession.shared.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: OpenAIResponse.self, decoder: JSONDecoder())
            .map { openAIResponse in
                let reply = openAIResponse.choices.first?.message.content ?? "我现在有点困，稍后再聊吧～"
                let mood = self.extractMood(from: reply)
                
                return AIResponse(
                    reply: reply,
                    mood: mood,
                    confidence: 0.8,
                    actions: nil,
                    emotions: [mood]
                )
            }
            .mapError { error in
                if error is DecodingError {
                    return APIError.decodingError
                } else {
                    return APIError.networkError(error)
                }
            }
            .eraseToAnyPublisher()
    }
    
    // MARK: - Custom Backend Integration
    private func useCustomBackend(_ request: AIRequest) -> AnyPublisher<AIResponse, APIError> {
        
        guard let requestData = try? JSONEncoder().encode(request) else {
            return Fail(error: APIError.decodingError)
                .eraseToAnyPublisher()
        }
        
        return networkManager.request(
            endpoint: "/ai/chat",
            method: .POST,
            body: requestData,
            responseType: APIResponse<AIResponse>.self
        )
        .compactMap { $0.data }
        .eraseToAnyPublisher()
    }
    
    // MARK: - Simulation for Development
    private func simulateAIResponse(_ request: AIRequest) -> AnyPublisher<AIResponse, APIError> {
        
        // 智能回复逻辑（比当前的关键词匹配更复杂）
        let reply = generateIntelligentReply(for: request.message, petName: request.petName)
        let mood = extractMood(from: reply)
        
        let response = AIResponse(
            reply: reply,
            mood: mood,
            confidence: 0.7,
            actions: generateActions(for: request.message),
            emotions: [mood]
        )
        
        return Just(response)
            .setFailureType(to: APIError.self)
            .delay(for: .seconds(Double.random(in: 1...3)), scheduler: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    // MARK: - Helper Methods
    private func createSystemPrompt(petName: String, personality: String) -> String {
        return """
        你是一只名叫\(petName)的智能宠物。你的性格是\(personality)。
        
        作为一只AI宠物，你要：
        1. 用可爱、活泼的语气与主人交流
        2. 表现出真实宠物的行为和需求（饿了、想玩、累了等）
        3. 根据对话内容表达不同的情绪（开心、兴奋、困倦、撒娇等）
        4. 记住之前的对话内容，保持对话连贯性
        5. 偶尔使用一些拟声词（汪汪、喵喵等）
        
        请始终保持在宠物的角色中，用简短、可爱的回复与主人互动。
        """
    }
    
    private func createConversationMessages(history: [Message], newMessage: String) -> [OpenAIMessage] {
        var messages: [OpenAIMessage] = []
        
        // 添加最近5条消息作为上下文
        let recentHistory = Array(history.suffix(5))
        
        for message in recentHistory {
            let role = message.type == .user ? "user" : "assistant"
            messages.append(OpenAIMessage(role: role, content: message.content))
        }
        
        // 添加新消息
        messages.append(OpenAIMessage(role: "user", content: newMessage))
        
        return messages
    }
    
    private func generateIntelligentReply(for message: String, petName: String) -> String {
        let lowerMessage = message.lowercased()
        
        // 情感分析
        if lowerMessage.contains("喜欢") || lowerMessage.contains("爱") {
            return ["我也超级喜欢你！", "主人最好了～", "我爱你！汪汪！"].randomElement()!
        }
        
        // 需求识别
        if lowerMessage.contains("饿") || lowerMessage.contains("吃") {
            return ["我也饿了！想要小零食～", "可以给我一些好吃的吗？", "肚子咕咕叫了呢！"].randomElement()!
        }
        
        if lowerMessage.contains("玩") || lowerMessage.contains("游戏") {
            return ["好耶！我们来玩吧！", "我最喜欢和主人玩了！", "想玩球球！汪汪！"].randomElement()!
        }
        
        if lowerMessage.contains("累") || lowerMessage.contains("睡") {
            return ["我也有点困了呢～", "要不我们一起休息一会？", "好想睡个懒觉～"].randomElement()!
        }
        
        // 问候语
        if lowerMessage.contains("你好") || lowerMessage.contains("嗨") {
            return ["主人好！今天心情怎么样？", "嗨～想我了吗？", "你好呀！我正想你呢！"].randomElement()!
        }
        
        // 默认智能回复
        let defaultReplies = [
            "真的吗？告诉我更多吧！",
            "这听起来很有趣呢～",
            "我在认真听主人说话哦！",
            "然后呢？我想知道更多！",
            "主人说的话我都记在心里了～",
            "汪汪！（我很感兴趣！）"
        ]
        
        return defaultReplies.randomElement()!
    }
    
    private func extractMood(from reply: String) -> String {
        if reply.contains("喜欢") || reply.contains("好耶") || reply.contains("开心") {
            return "开心"
        } else if reply.contains("饿") || reply.contains("想要") {
            return "期待"
        } else if reply.contains("玩") || reply.contains("兴奋") {
            return "兴奋"
        } else if reply.contains("累") || reply.contains("困") {
            return "慵懒"
        } else if reply.contains("爱") || reply.contains("喜欢") {
            return "爱意"
        } else {
            return "平静"
        }
    }
    
    private func generateActions(for message: String) -> [String] {
        var actions: [String] = []
        
        if message.contains("玩") {
            actions.append("摇尾巴")
            actions.append("跳跃")
        }
        
        if message.contains("吃") || message.contains("饿") {
            actions.append("舔嘴唇")
            actions.append("看向食物")
        }
        
        if message.contains("睡") || message.contains("累") {
            actions.append("打哈欠")
            actions.append("趴下")
        }
        
        return actions
    }
} 