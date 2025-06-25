import Foundation

// 注意：Feed结构体已在FurryKidsApp.swift中定义，这里仅保留示例数据
extension Feed {
    static let sampleData = [
        Feed(
            petId: UUID(),
            petName: "Buddy",
            petAvatar: "🐶",
            content: "今天和主人去公园玩了，好开心！🌳🏃‍♂️",
            images: ["park_image1"],
            likes: 42,
            comments: 12,
            mood: "开心",
            topics: ["户外活动", "遛狗"],
            createdAt: Date().addingTimeInterval(-3600)
        ),
        Feed(
            petId: UUID(),
            petName: "Kitty",
            petAvatar: "🐱",
            content: "窗边晒太阳真舒服，这是我的最爱！☀️😌",
            images: ["sunbath_image"],
            likes: 35,
            comments: 8,
            mood: "慵懒",
            topics: ["晒太阳", "休闲"],
            createdAt: Date().addingTimeInterval(-7200)
        ),
        Feed(
            petId: UUID(),
            petName: "Fluffy",
            petAvatar: "🐰",
            content: "刚刚吃了超级好吃的胡萝卜！🥕 我的最爱！",
            images: ["carrot_image"],
            likes: 28,
            comments: 5,
            mood: "满足",
            topics: ["美食", "零食"],
            createdAt: Date().addingTimeInterval(-10800)
        )
    ]
} 