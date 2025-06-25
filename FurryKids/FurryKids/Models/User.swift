import Foundation

// MARK: - 用户数据模型
struct User: Codable, Identifiable {
    let id: Int
    let username: String
    let provider: String // "local", "google", "facebook"
    let email: String?
    let displayName: String?
    let createdAt: String?
    let updatedAt: String?
}

// MARK: - 认证请求模型
struct LoginRequest: Codable {
    let username: String
    let password: String
}

struct RegisterRequest: Codable {
    let username: String
    let password: String
}

// MARK: - 认证响应模型
struct AuthResponse: Codable {
    let success: Bool
    let message: String
    let user: User?
}

struct UserInfoResponse: Codable {
    let user: User?
    let authType: String?
}

struct ErrorResponse: Codable {
    let success: Bool
    let message: String
    let code: String?
} 