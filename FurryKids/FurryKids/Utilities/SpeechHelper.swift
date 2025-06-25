import Foundation
import AVFoundation

class SpeechHelper {
    static let shared = SpeechHelper()
    
    private init() {}
    
    // 检查语音合成是否可用（语音合成不需要麦克风权限）
    func checkSpeechSynthesisAvailability() {
        let voices = AVSpeechSynthesisVoice.speechVoices()
        if voices.isEmpty {
            print("警告：没有可用的语音合成引擎")
        } else {
            print("语音合成功能可用，共有 \(voices.count) 个语音")
        }
    }
    
    // 仅在需要录音功能时才检查麦克风权限
    func checkMicrophonePermissionIfNeeded() {
        // 目前应用只使用语音合成，不需要录音功能
        // 如果将来需要语音识别功能，再启用此方法
        print("当前应用只使用语音合成功能，无需麦克风权限")
    }
    
    // 设置音频会话
    func setupAudioSession() {
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.playback, mode: .default, options: [])
            try audioSession.setActive(true)
            print("音频会话设置成功")
        } catch {
            print("音频会话设置失败: \(error.localizedDescription)")
        }
    }
    
    // 获取可用的语音列表
    func getAvailableVoices() -> [AVSpeechSynthesisVoice] {
        let voices = AVSpeechSynthesisVoice.speechVoices()
        print("可用语音数量: \(voices.count)")
        
        for voice in voices {
            print("语音: \(voice.name), 语言: \(voice.language)")
        }
        
        return voices
    }
    
    // 获取最佳中文语音
    func getBestChineseVoice() -> AVSpeechSynthesisVoice? {
        let chineseVoices = AVSpeechSynthesisVoice.speechVoices().filter { voice in
            voice.language.hasPrefix("zh")
        }
        
        // 优先选择普通话
        for voice in chineseVoices {
            if voice.language == "zh-CN" {
                return voice
            }
        }
        
        // 如果没有找到普通话，返回第一个中文语音
        return chineseVoices.first ?? AVSpeechSynthesisVoice.speechVoices().first
    }
    
    // 清理文本，移除不适合语音合成的字符
    func cleanTextForSpeech(_ text: String) -> String {
        let cleanText = text
            .replacingOccurrences(of: "[\\p{Emoji}]", with: "", options: .regularExpression)
            .replacingOccurrences(of: "[()（）\\[\\]{}【】]", with: "", options: .regularExpression)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        
        return cleanText.isEmpty ? "空消息" : cleanText
    }
} 