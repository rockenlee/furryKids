import Foundation

// 注意：Pet结构体已在FurryKidsApp.swift中定义，这里仅保留示例数据

// 示例数据
extension Pet {
    static let sampleData = [
        Pet(name: "小毛球", avatar: "🐕", breed: "金毛", age: 2,
            personality: ["活泼", "粘人", "聪明"],
            signature: "我是一只活泼的金毛，喜欢和主人一起玩耍！",
            mood: "开心", 
            status: "在线",
            level: 3,
            experience: 45,
            maxExperience: 100),
            
        Pet(name: "小橘猫", avatar: "🐱", breed: "橘猫", age: 1,
            personality: ["慵懒", "好奇", "独立"],
            signature: "窗边的阳光是我最爱的地方~",
            mood: "慵懒", 
            status: "离线",
            level: 2,
            experience: 30,
            maxExperience: 80),
            
        Pet(name: "旺财", avatar: "🐕‍🦺", breed: "德牧", age: 3,
            personality: ["忠诚", "警觉", "勇敢"],
            signature: "保护主人是我的责任！",
            mood: "警惕", 
            status: "在线",
            level: 4,
            experience: 60,
            maxExperience: 120),
            
        Pet(name: "咪咪", avatar: "🐱", breed: "布偶", age: 2,
            personality: ["温顺", "安静", "亲人"],
            signature: "主人的怀抱最温暖~",
            mood: "满足", 
            status: "在线",
            level: 3,
            experience: 40,
            maxExperience: 100)
    ]
} 