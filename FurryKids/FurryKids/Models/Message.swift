import Foundation

// 注意：这些类型已在FurryKidsApp.swift中定义，这里保留示例数据

// 示例数据
extension Message {
    static let samples = [
        Message(
            content: "汪汪！主人你回来啦！我好想你呀~ 🐕💕",
            type: .pet,
            mood: "兴奋"
        ),
        Message(
            content: "我也很想你！今天乖不乖？",
            type: .user
        ),
        Message(
            content: "我超级乖的！一直在等你回家，还自己玩了一会儿球球。不过有点想出去散步...",
            type: .pet,
            mood: "期待"
        )
    ]
} 