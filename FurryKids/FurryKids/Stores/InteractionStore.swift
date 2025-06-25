import Foundation
import Combine
import AVFoundation

class InteractionStore: NSObject, ObservableObject {
    @Published var messages: [Message] = []
    @Published var isLoading = false
    @Published var error: String?
    @Published var isTyping = false
    @Published var isSpeaking = false
    
    private var speechSynthesizer = AVSpeechSynthesizer()
    private var cancellables = Set<AnyCancellable>()
    
    override init() {
        super.init()
        setupAudioSession()
        setupSpeechSynthesizer()
        
        // 添加欢迎消息
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.receiveMessage("你好！很高兴见到你！今天想和我聊点什么呢？", mood: "开心")
        }
    }
    
    // MARK: - Audio Session Setup
    
    private func setupAudioSession() {
        #if !targetEnvironment(simulator)
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .default)
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("音频会话设置失败: \(error)")
        }
        #else
        // 模拟器环境下跳过音频会话配置以避免警告
        print("模拟器环境：跳过音频会话配置")
        #endif
    }
    
    // MARK: - Message Actions
    
    // 发送用户消息
    func sendMessage(_ content: String) {
        let message = Message(content: content, type: .user)
        messages.append(message)
        
        // 模拟AI回复
        self.isTyping = true
        self.isLoading = true
        
        DispatchQueue.main.asyncAfter(deadline: .now() + Double.random(in: 1...3)) {
            self.isTyping = false
            self.isLoading = false
            
            let aiReply = self.generateAIReply(for: content)
            self.receiveMessage(aiReply.reply, mood: aiReply.mood)
            
            // 自动语音播报
            self.speakMessage(aiReply.reply)
        }
    }
    
    // 接收宠物消息
    func receiveMessage(_ content: String, mood: String? = nil) {
        let message = Message(content: content, type: .pet, mood: mood)
        messages.append(message)
    }
    
    // MARK: - AI Reply Generation
    private func generateAIReply(for userMessage: String) -> (reply: String, mood: String) {
        let lowercased = userMessage.lowercased()
        
        // 关键词匹配回复
        if lowercased.contains("你好") || lowercased.contains("hi") || lowercased.contains("hello") {
            return ("你好呀！我是你的小伙伴，很高兴和你聊天！", "开心")
        } else if lowercased.contains("吃") || lowercased.contains("饿") {
            return ("哇！我也饿了呢，想吃好吃的小零食！🍖", "兴奋")
        } else if lowercased.contains("玩") || lowercased.contains("游戏") {
            return ("太好了！我们来玩游戏吧！我最喜欢玩球球了！🎾", "兴奋")
        } else if lowercased.contains("累") || lowercased.contains("困") {
            return ("那我们一起休息一下吧，我陪着你～", "温柔")
        } else if lowercased.contains("散步") || lowercased.contains("走") {
            return ("出去散步！我最喜欢出门了，可以看到好多新鲜的东西！", "兴奋")
        } else if lowercased.contains("洗澡") {
            return ("洗澡澡～虽然有点紧张，但是洗完会很香呢！", "紧张")
        } else if lowercased.contains("学习") || lowercased.contains("训练") {
            return ("好的！我会认真学习的，做一个聪明的好宝宝！", "认真")
        } else if lowercased.contains("爱") || lowercased.contains("喜欢") {
            return ("我也很爱你呢！你是世界上最好的主人！❤️", "爱意")
        } else {
            // 默认回复
            let defaultReplies = [
                ("真的吗？听起来很有趣呢！", "好奇"),
                ("嗯嗯，我在认真听你说话呢！", "专注"),
                ("哇，你说的好棒！", "开心"),
                ("我觉得你说得对呢！", "赞同"),
                ("还有吗？我想听更多！", "好奇"),
                ("你真是太聪明了！", "崇拜")
            ]
            return defaultReplies.randomElement() ?? ("我在想该怎么回答你呢～", "思考")
        }
    }
    
    // MARK: - Speech Synthesis
    
    private func setupSpeechSynthesizer() {
        speechSynthesizer.delegate = self
    }
    
    func speakMessage(_ text: String) {
        // 如果正在播放，先停止
        if speechSynthesizer.isSpeaking {
            speechSynthesizer.stopSpeaking(at: .immediate)
        }
        
        // 清理文本
        let cleanText = cleanTextForSpeech(text)
        
        let utterance = AVSpeechUtterance(string: cleanText)
        
        // 设置中文语音
        utterance.voice = getBestChineseVoice()
        utterance.rate = 0.4 // 稍微慢一点，更像宠物的语调
        utterance.pitchMultiplier = 1.1 // 稍微高一点，更可爱
        utterance.volume = 0.8
        
        isSpeaking = true
        speechSynthesizer.speak(utterance)
    }
    
    func stopSpeaking() {
        speechSynthesizer.stopSpeaking(at: .immediate)
        isSpeaking = false
    }
    
    // MARK: - Helper Methods
    private func cleanTextForSpeech(_ text: String) -> String {
        return text
            .replacingOccurrences(of: "🍖", with: "")
            .replacingOccurrences(of: "🎾", with: "")
            .replacingOccurrences(of: "❤️", with: "")
            .replacingOccurrences(of: "～", with: "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
    }
    
    private func getBestChineseVoice() -> AVSpeechSynthesisVoice? {
        let chineseVoices = AVSpeechSynthesisVoice.speechVoices().filter { voice in
            voice.language.hasPrefix("zh")
        }
        
        // 优先选择中文语音
        return chineseVoices.first ?? AVSpeechSynthesisVoice(language: "zh-CN")
    }
    
    // MARK: - 触发互动
    func triggerInteraction(_ action: InteractionAction) {
        // 发送用户行为消息
        let userActionMessages = [
            InteractionAction.feed: "我给你带来了美味的食物！",
            InteractionAction.pet: "摸摸头，做得好！",
            InteractionAction.play: "来玩球吧！",
            InteractionAction.walk: "我们去散步吧！",
            InteractionAction.wash: "该洗澡了，会很舒服的！",
            InteractionAction.train: "来学习一个新技能吧！"
        ]
        
        if let userMessage = userActionMessages[action] {
            sendMessage(userMessage)
        }
    }
    
    func clearMessages() {
        messages.removeAll()
    }
}

// MARK: - AVSpeechSynthesizerDelegate
extension InteractionStore: AVSpeechSynthesizerDelegate {
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        DispatchQueue.main.async {
            self.isSpeaking = false
        }
    }
    
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        DispatchQueue.main.async {
            self.isSpeaking = false
        }
    }
} 