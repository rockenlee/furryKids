import SwiftUI
import Foundation
import Combine

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

// MARK: - 认证服务
class AuthService: ObservableObject {
    static let shared = AuthService()
    
    private let baseURL = "http://localhost:8000"
    private let session = URLSession.shared
    
    private init() {}
    
    // MARK: - 用户注册
    func register(username: String, password: String) -> AnyPublisher<AuthResponse, Error> {
        guard let url = URL(string: "\(baseURL)/auth/register") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }
        
        let request = RegisterRequest(username: username, password: password)
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            return Fail(error: error)
                .eraseToAnyPublisher()
        }
        
        return session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: AuthResponse.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    // MARK: - 用户登录
    func login(username: String, password: String) -> AnyPublisher<AuthResponse, Error> {
        guard let url = URL(string: "\(baseURL)/auth/login") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }
        
        let request = LoginRequest(username: username, password: password)
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpShouldHandleCookies = true
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            return Fail(error: error)
                .eraseToAnyPublisher()
        }
        
        return session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: AuthResponse.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    // MARK: - 用户登出
    func logout() -> AnyPublisher<AuthResponse, Error> {
        guard let url = URL(string: "\(baseURL)/auth/logout") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.httpShouldHandleCookies = true
        
        return session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: AuthResponse.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    // MARK: - 获取当前用户信息
    func getCurrentUser() -> AnyPublisher<UserInfoResponse, Error> {
        guard let url = URL(string: "\(baseURL)/api/user") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpShouldHandleCookies = true
        
        return session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: UserInfoResponse.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    // MARK: - 健康检查
    func healthCheck() -> AnyPublisher<[String: String], Error> {
        guard let url = URL(string: "\(baseURL)/api/health") else {
            return Fail(error: URLError(.badURL))
                .eraseToAnyPublisher()
        }
        
        return session.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: [String: String].self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
}

// MARK: - 认证状态管理
class AuthStore: ObservableObject {
    @Published var currentUser: User?
    @Published var isAuthenticated = false
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    var cancellables = Set<AnyCancellable>()
    private let authService = AuthService.shared
    
    init() {
        checkAuthStatus()
    }
    
    func checkAuthStatus() {
        isLoading = true
        
        authService.getCurrentUser()
            .sink(
                receiveCompletion: { [weak self] completion in
                    DispatchQueue.main.async {
                        self?.isLoading = false
                        if case .failure = completion {
                            self?.isAuthenticated = false
                            self?.currentUser = nil
                        }
                    }
                },
                receiveValue: { [weak self] response in
                    DispatchQueue.main.async {
                        if let user = response.user {
                            self?.currentUser = user
                            self?.isAuthenticated = true
                        } else {
                            self?.isAuthenticated = false
                            self?.currentUser = nil
                        }
                    }
                }
            )
            .store(in: &cancellables)
    }
    
    func login(username: String, password: String) {
        isLoading = true
        errorMessage = nil
        
        authService.login(username: username, password: password)
            .sink(
                receiveCompletion: { [weak self] completion in
                    DispatchQueue.main.async {
                        self?.isLoading = false
                        if case .failure(let error) = completion {
                            self?.errorMessage = "网络错误: \(error.localizedDescription)"
                        }
                    }
                },
                receiveValue: { [weak self] response in
                    DispatchQueue.main.async {
                        if response.success, let user = response.user {
                            self?.currentUser = user
                            self?.isAuthenticated = true
                            self?.errorMessage = nil
                        } else {
                            self?.errorMessage = response.message
                            self?.isAuthenticated = false
                        }
                    }
                }
            )
            .store(in: &cancellables)
    }
    
    func register(username: String, password: String) {
        isLoading = true
        errorMessage = nil
        
        authService.register(username: username, password: password)
            .sink(
                receiveCompletion: { [weak self] completion in
                    DispatchQueue.main.async {
                        self?.isLoading = false
                        if case .failure(let error) = completion {
                            self?.errorMessage = "网络错误: \(error.localizedDescription)"
                        }
                    }
                },
                receiveValue: { [weak self] response in
                    DispatchQueue.main.async {
                        if response.success, let user = response.user {
                            self?.currentUser = user
                            self?.isAuthenticated = true
                            self?.errorMessage = nil
                        } else {
                            self?.errorMessage = response.message
                        }
                    }
                }
            )
            .store(in: &cancellables)
    }
    
    func logout() {
        isLoading = true
        
        authService.logout()
            .sink(
                receiveCompletion: { [weak self] completion in
                    DispatchQueue.main.async {
                        self?.isLoading = false
                        if case .failure(let error) = completion {
                            self?.errorMessage = "登出失败: \(error.localizedDescription)"
                        }
                    }
                },
                receiveValue: { [weak self] response in
                    DispatchQueue.main.async {
                        if response.success {
                            self?.currentUser = nil
                            self?.isAuthenticated = false
                            self?.errorMessage = nil
                        } else {
                            self?.errorMessage = response.message
                        }
                    }
                }
            )
            .store(in: &cancellables)
    }
    
    func clearError() {
        errorMessage = nil
    }
}

// MARK: - 登录界面
struct LoginView: View {
    @StateObject private var authStore = AuthStore()
    @State private var username = ""
    @State private var password = ""
    @State private var isRegistering = false
    @State private var showingAlert = false
    @State private var healthCheckResult = ""
    @State private var showingHealthCheck = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                // Logo 区域
                VStack(spacing: 16) {
                    Image(systemName: "pawprint.circle.fill")
                        .font(.system(size: 80))
                        .foregroundColor(.blue)
                    
                    Text("毛孩子AI")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#101618"))
                    
                    Text(isRegistering ? "注册新账户" : "欢迎回来")
                        .font(.title2)
                        .foregroundColor(Color(hex: "#5c7d8a"))
                }
                .padding(.top, 50)
                
                // 表单区域
                VStack(spacing: 20) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("用户名")
                            .font(.headline)
                            .foregroundColor(Color(hex: "#101618"))
                        
                        TextField("请输入用户名", text: $username)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .autocapitalization(.none)
                            .disableAutocorrection(true)
                    }
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("密码")
                            .font(.headline)
                            .foregroundColor(Color(hex: "#101618"))
                        
                        SecureField("请输入密码", text: $password)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                    }
                    
                    if let errorMessage = authStore.errorMessage {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.caption)
                            .multilineTextAlignment(.center)
                    }
                    
                    Button(action: {
                        if isRegistering {
                            authStore.register(username: username, password: password)
                        } else {
                            authStore.login(username: username, password: password)
                        }
                    }) {
                        HStack {
                            if authStore.isLoading {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                    .scaleEffect(0.8)
                            }
                            
                            Text(isRegistering ? "注册" : "登录")
                                .fontWeight(.semibold)
                        }
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(Color.blue)
                        .cornerRadius(10)
                    }
                    .disabled(username.isEmpty || password.isEmpty || authStore.isLoading)
                    
                    Button(action: {
                        isRegistering.toggle()
                        authStore.clearError()
                    }) {
                        Text(isRegistering ? "已有账户？点击登录" : "没有账户？点击注册")
                            .foregroundColor(.blue)
                            .font(.subheadline)
                    }
                    
                    Button(action: {
                        testServerConnection()
                    }) {
                        Text("测试服务器连接")
                            .foregroundColor(.orange)
                            .font(.caption)
                    }
                }
                .padding(.horizontal, 40)
                
                Spacer()
            }
            .background(Color(hex: "#F9FAFB"))
            .navigationBarHidden(true)
        }
        .alert("提示", isPresented: $showingAlert) {
            Button("确定") {
                authStore.clearError()
            }
        } message: {
            Text(authStore.errorMessage ?? "")
        }
        .alert("服务器连接测试", isPresented: $showingHealthCheck) {
            Button("确定") { }
        } message: {
            Text(healthCheckResult)
        }
        .onChange(of: authStore.errorMessage) { errorMessage in
            if errorMessage != nil {
                showingAlert = true
            }
        }
    }
    
    private func testServerConnection() {
        AuthService.shared.healthCheck()
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        healthCheckResult = "连接失败: \(error.localizedDescription)\n\n请确保后端服务运行在 localhost:8000"
                        showingHealthCheck = true
                    }
                },
                receiveValue: { response in
                    healthCheckResult = "连接成功!\n状态: \(response["status"] ?? "未知")\n消息: \(response["message"] ?? "无消息")"
                    showingHealthCheck = true
                }
            )
            .store(in: &authStore.cancellables)
    }
}

// MARK: - 用户个人中心
struct UserProfileView: View {
    @ObservedObject var authStore: AuthStore
    @State private var showingLogoutAlert = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                VStack(spacing: 16) {
                    Circle()
                        .fill(Color.blue.gradient)
                        .frame(width: 100, height: 100)
                        .overlay(
                            Image(systemName: "person.fill")
                                .font(.system(size: 50))
                                .foregroundColor(.white)
                        )
                    
                    Text(authStore.currentUser?.displayName ?? authStore.currentUser?.username ?? "用户")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#101618"))
                    
                    if let provider = authStore.currentUser?.provider {
                        HStack {
                            Image(systemName: provider == "local" ? "person.badge.key" : "globe")
                            Text(provider == "local" ? "本地账户" : "第三方账户")
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
                
                if let user = authStore.currentUser {
                    VStack(spacing: 0) {
                        ProfileInfoRow(icon: "person.badge.key", title: "用户ID", value: "\(user.id)")
                        Divider()
                        ProfileInfoRow(icon: "person.circle", title: "用户名", value: user.username)
                        if let email = user.email {
                            Divider()
                            ProfileInfoRow(icon: "envelope", title: "邮箱", value: email)
                        }
                    }
                    .background(Color.white)
                    .cornerRadius(12)
                    .shadow(color: .gray.opacity(0.1), radius: 5, x: 0, y: 2)
                    .padding(.horizontal, 20)
                }
                
                Spacer()
                
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
}

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