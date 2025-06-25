import SwiftUI

struct UserProfileView: View {
    @ObservedObject var authStore: AuthStore
    @State private var showingLogoutAlert = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // 用户头像和基本信息
                VStack(spacing: 16) {
                    // 头像
                    Circle()
                        .fill(Color.blue.gradient)
                        .frame(width: 100, height: 100)
                        .overlay(
                            Image(systemName: "person.fill")
                                .font(.system(size: 50))
                                .foregroundColor(.white)
                        )
                    
                    // 用户名
                    Text(authStore.currentUser?.displayName ?? authStore.currentUser?.username ?? "用户")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#101618"))
                    
                    // 登录方式标签
                    if let provider = authStore.currentUser?.provider {
                        HStack {
                            Image(systemName: providerIcon(provider))
                            Text(providerName(provider))
                        }
                        .font(.caption)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 4)
                        .background(Color.blue.opacity(0.1))
                        .foregroundColor(.blue)
                        .cornerRadius(12)
                    }
                }
                .padding(.top, 30)
                
                // 用户信息卡片
                if let user = authStore.currentUser {
                    VStack(spacing: 0) {
                        // 用户ID
                        ProfileInfoRow(
                            icon: "person.badge.key",
                            title: "用户ID",
                            value: "\(user.id)"
                        )
                        
                        Divider()
                        
                        // 用户名
                        ProfileInfoRow(
                            icon: "person.circle",
                            title: "用户名",
                            value: user.username
                        )
                        
                        Divider()
                        
                        // 邮箱（如果有）
                        if let email = user.email {
                            ProfileInfoRow(
                                icon: "envelope",
                                title: "邮箱",
                                value: email
                            )
                            
                            Divider()
                        }
                        
                        // 注册时间（如果有）
                        if let createdAt = user.createdAt {
                            ProfileInfoRow(
                                icon: "calendar",
                                title: "注册时间",
                                value: formatDate(createdAt)
                            )
                        }
                    }
                    .background(Color.white)
                    .cornerRadius(12)
                    .shadow(color: .gray.opacity(0.1), radius: 5, x: 0, y: 2)
                    .padding(.horizontal, 20)
                }
                
                Spacer()
                
                // 登出按钮
                Button(action: {
                    showingLogoutAlert = true
                }) {
                    HStack {
                        Image(systemName: "arrow.right.square")
                        Text("登出")
                    }
                    .foregroundColor(.red)
                    .frame(maxWidth: .infinity)
                    .frame(height: 50)
                    .background(Color.red.opacity(0.1))
                    .cornerRadius(10)
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 30)
            }
            .background(Color(hex: "#F9FAFB"))
            .navigationTitle("个人中心")
            .navigationBarTitleDisplayMode(.inline)
        }
        .alert("确认登出", isPresented: $showingLogoutAlert) {
            Button("取消", role: .cancel) { }
            Button("登出", role: .destructive) {
                authStore.logout()
            }
        } message: {
            Text("确定要登出当前账户吗？")
        }
    }
    
    // MARK: - Helper Functions
    private func providerIcon(_ provider: String) -> String {
        switch provider {
        case "google":
            return "globe"
        case "facebook":
            return "person.circle"
        default:
            return "person.badge.key"
        }
    }
    
    private func providerName(_ provider: String) -> String {
        switch provider {
        case "google":
            return "Google 账户"
        case "facebook":
            return "Facebook 账户"
        default:
            return "本地账户"
        }
    }
    
    private func formatDate(_ dateString: String) -> String {
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: dateString) {
            let displayFormatter = DateFormatter()
            displayFormatter.dateStyle = .medium
            displayFormatter.timeStyle = .none
            displayFormatter.locale = Locale(identifier: "zh_CN")
            return displayFormatter.string(from: date)
        }
        return dateString
    }
}

// MARK: - 个人信息行组件
struct ProfileInfoRow: View {
    let icon: String
    let title: String
    let value: String
    
    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: icon)
                .foregroundColor(.blue)
                .frame(width: 20)
            
            Text(title)
                .foregroundColor(Color(hex: "#5c7d8a"))
                .frame(maxWidth: .infinity, alignment: .leading)
            
            Text(value)
                .foregroundColor(Color(hex: "#101618"))
                .fontWeight(.medium)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
    }
} 