import SwiftUI

// 导入StoreImports中的所有定义
import Foundation
import Combine
import AVFoundation

// 颜色扩展位于 Utilities/Color+Extensions.swift 文件中

// MARK: - 用户认证相关数据模型
struct User: Codable, Identifiable {
    let id: Int
    let username: String
    let provider: String // "local", "google", "facebook"
    let email: String?
    let displayName: String?
    let createdAt: String?
    let updatedAt: String?
}

struct LoginRequest: Codable {
    let username: String
    let password: String
}

struct RegisterRequest: Codable {
    let username: String
    let password: String
}

struct AuthResponse: Codable {
    let success: Bool
    let message: String
    let user: User?
}

struct UserInfoResponse: Codable {
    let user: User?
    let authType: String?
}

// MARK: - 认证服务
class AuthService: ObservableObject {
    static let shared = AuthService()
    
    private let baseURL = "http://localhost:8000"
    private let session = URLSession.shared
    
    private init() {}
    
    func register(username: String, password: String) -> AnyPublisher<AuthResponse, Error> {
        guard let url = URL(string: "\(baseURL)/auth/register") else {
            return Fail(error: URLError(.badURL)).eraseToAnyPublisher()
        }
        
        let request = RegisterRequest(username: username, password: password)
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
        } catch {
            return Fail(error: error).eraseToAnyPublisher()
        }
        
        return session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: AuthResponse.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    func login(username: String, password: String) -> AnyPublisher<AuthResponse, Error> {
        guard let url = URL(string: "\(baseURL)/auth/login") else {
            print("❌ 登录失败: 无效的URL - \(baseURL)/auth/login")
            return Fail(error: URLError(.badURL)).eraseToAnyPublisher()
        }
        
        print("🚀 开始登录请求: \(url.absoluteString)")
        print("👤 用户名: \(username)")
        
        let request = LoginRequest(username: username, password: password)
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpShouldHandleCookies = true
        
        do {
            urlRequest.httpBody = try JSONEncoder().encode(request)
            print("📦 请求体已编码")
        } catch {
            print("❌ 请求体编码失败: \(error)")
            return Fail(error: error).eraseToAnyPublisher()
        }
        
        return session.dataTaskPublisher(for: urlRequest)
            .handleEvents(
                receiveSubscription: { _ in
                    print("📡 网络请求已发送")
                },
                receiveOutput: { output in
                    print("📥 收到响应数据: \(output.data.count) bytes")
                    if let responseString = String(data: output.data, encoding: .utf8) {
                        print("📄 响应内容: \(responseString)")
                    }
                },
                receiveCompletion: { completion in
                    switch completion {
                    case .finished:
                        print("✅ 网络请求完成")
                    case .failure(let error):
                        print("❌ 网络请求失败: \(error)")
                    }
                },
                receiveCancel: {
                    print("🚫 网络请求被取消")
                }
            )
            .map(\.data)
            .decode(type: AuthResponse.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    func logout() -> AnyPublisher<AuthResponse, Error> {
        guard let url = URL(string: "\(baseURL)/auth/logout") else {
            return Fail(error: URLError(.badURL)).eraseToAnyPublisher()
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
    
    func getCurrentUser() -> AnyPublisher<UserInfoResponse, Error> {
        guard let url = URL(string: "\(baseURL)/api/user") else {
            return Fail(error: URLError(.badURL)).eraseToAnyPublisher()
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpShouldHandleCookies = true
        
        return session.dataTaskPublisher(for: urlRequest)
            .map(\.data)
            .decode(type: UserInfoResponse.self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
    
    func healthCheck() -> AnyPublisher<[String: String], Error> {
        guard let url = URL(string: "\(baseURL)/api/health") else {
            return Fail(error: URLError(.badURL)).eraseToAnyPublisher()
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
        print("🔑 AuthStore: 开始登录流程")
        isLoading = true
        errorMessage = nil
        
        authService.login(username: username, password: password)
            .sink(
                receiveCompletion: { [weak self] completion in
                    DispatchQueue.main.async {
                        self?.isLoading = false
                        if case .failure(let error) = completion {
                            print("❌ AuthStore: 登录失败 - \(error.localizedDescription)")
                            self?.errorMessage = "网络错误: \(error.localizedDescription)"
                        }
                    }
                },
                receiveValue: { [weak self] response in
                    DispatchQueue.main.async {
                        print("📋 AuthStore: 收到登录响应 - success: \(response.success), message: \(response.message)")
                        if response.success, let user = response.user {
                            print("✅ AuthStore: 登录成功 - 用户: \(user.username)")
                            self?.currentUser = user
                            self?.isAuthenticated = true
                            self?.errorMessage = nil
                        } else {
                            print("❌ AuthStore: 登录失败 - \(response.message)")
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
    @EnvironmentObject var authStore: AuthStore
    @State private var username = ""
    @State private var password = ""
    @State private var isRegistering = false
    @State private var showingAlert = false
    @State private var healthCheckResult = ""
    @State private var showingHealthCheck = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
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
                        .fill(Color.blue)
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

// 宠物相关
enum MessageType: String, Codable {
    case user
    case pet
}

struct Message: Identifiable {
    var id = UUID()
    var content: String
    var type: MessageType
    var timestamp: Date
    var mood: String?
    
    init(content: String, type: MessageType, mood: String? = nil) {
        self.content = content
        self.type = type
        self.timestamp = Date()
        self.mood = mood
    }
}

struct Pet: Identifiable {
    var id = UUID()
    var name: String
    var avatar: String
    var breed: String
    var age: Int
    var personality: [String]
    var signature: String
    var mood: String
    var status: String
    var level: Int
    var experience: Int
    var maxExperience: Int
    
    static let sample = Pet(
        name: "Buddy",
        avatar: "🐶",
        breed: "柴犬",
        age: 2,
        personality: ["活泼", "好奇", "友善"],
        signature: "我是一只可爱的柴犬，喜欢玩球和晒太阳！",
        mood: "开心",
        status: "在线",
        level: 5,
        experience: 75,
        maxExperience: 100
    )
}

struct Feed: Identifiable {
    var id = UUID()
    var petId: UUID
    var petName: String
    var petAvatar: String
    var content: String
    var images: [String]
    var likes: Int
    var comments: Int
    var shares: Int = 0
    var isLiked: Bool = false
    var mood: String?
    var topics: [String] = []
    var createdAt: Date
}

// 互动动作
enum InteractionAction: String, CaseIterable {
    case feed = "喂食"
    case pet = "抚摸"
    case play = "玩耍"
    case walk = "散步"
    case wash = "洗澡"
    case train = "训练"
    
    var emoji: String {
        switch self {
        case .feed: return "🍖"
        case .pet: return "👋"
        case .play: return "🎾"
        case .walk: return "🦮"
        case .wash: return "🛁"
        case .train: return "🎓"
        }
    }
}

// Store定义
class PetStore: ObservableObject {
    @Published var currentPet: Pet
    @Published var pets: [Pet] = []
    
    init() {
        // 初始化示例宠物
        let samplePet = Pet.sample
        self.currentPet = samplePet
        
        // 添加示例宠物到宠物列表
        self.pets = [
            samplePet,
            Pet(
                name: "Kitty",
                avatar: "🐱",
                breed: "英短猫",
                age: 3,
                personality: ["安静", "傲娇", "好奇"],
                signature: "我是一只优雅的猫咪，喜欢晒太阳和玩毛线球~",
                mood: "慵懒",
                status: "在线",
                level: 4,
                experience: 50,
                maxExperience: 100
            ),
            Pet(
                name: "Bunny",
                avatar: "🐰",
                breed: "荷兰垂耳兔",
                age: 1,
                personality: ["胆小", "可爱", "爱吃"],
                signature: "我是一只小兔子，喜欢吃胡萝卜和生菜！",
                mood: "开心",
                status: "在线",
                level: 3,
                experience: 30,
                maxExperience: 100
            )
        ]
    }
    
    // 设置当前宠物
    func setCurrentPet(_ pet: Pet) {
        currentPet = pet
    }
    
    // 更新宠物信息
    func updatePet(_ updates: [String: Any]) {
        for (key, value) in updates {
            switch key {
            case "name":
                if let name = value as? String {
                    currentPet.name = name
                }
            case "avatar":
                if let avatar = value as? String {
                    currentPet.avatar = avatar
                }
            case "signature":
                if let signature = value as? String {
                    currentPet.signature = signature
                }
            case "mood":
                if let mood = value as? String {
                    currentPet.mood = mood
                }
            case "status":
                if let status = value as? String {
                    currentPet.status = status
                }
            default:
                break
            }
        }
    }
    
    // 增加经验值
    func addExperience(_ amount: Int) {
        currentPet.experience += amount
        
        // 检查是否升级
        if currentPet.experience >= currentPet.maxExperience {
            levelUp()
        }
    }
    
    // 升级
    private func levelUp() {
        currentPet.level += 1
        currentPet.experience = currentPet.experience - currentPet.maxExperience
        currentPet.maxExperience = Int(Double(currentPet.maxExperience) * 1.5)
    }
    
    // 更新心情
    func updateMood(_ newMood: String) {
        currentPet.mood = newMood
    }
}

class FeedStore: ObservableObject {
    @Published var feeds: [Feed] = []
    @Published var isLoading = false
    @Published var error: String?
    @Published var hasMoreData = true
    
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        // 加载示例数据
        loadSampleData()
    }
    
    private func loadSampleData() {
        feeds = [
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
    
    // 添加新动态
    func addFeed(content: String, images: [String], petId: UUID, petName: String, petAvatar: String) {
        let newFeed = Feed(
            petId: petId,
            petName: petName,
            petAvatar: petAvatar,
            content: content,
            images: images,
            likes: 0,
            comments: 0,
            shares: 0,
            isLiked: false,
            mood: "开心",
            topics: [],
            createdAt: Date()
        )
        
        feeds.insert(newFeed, at: 0)
    }
    
    // 点赞动态
    func likeFeed(_ feedId: UUID) {
        if let index = feeds.firstIndex(where: { $0.id == feedId }) {
            feeds[index].likes += 1
        }
    }
    
    // 添加评论
    func addComment(_ feedId: UUID) {
        if let index = feeds.firstIndex(where: { $0.id == feedId }) {
            feeds[index].comments += 1
        }
    }
    
    // 获取时间格式化文本
    func timeString(_ date: Date) -> String {
        let minutes = Int(-date.timeIntervalSinceNow / 60)
        if minutes < 60 {
            return "\(minutes)分钟前"
        } else if minutes < 1440 {
            return "\(minutes / 60)小时前"
        } else {
            return "\(minutes / 1440)天前"
        }
    }
}

@main
struct FurryKidsApp: App {
    @StateObject private var authStore = AuthStore()
    
    var body: some Scene {
        WindowGroup {
            Group {
                if authStore.isLoading {
                    // 启动画面
                    SplashView()
                } else if authStore.isAuthenticated {
                    // 已登录，显示主应用
                    MainContentView()
                        .environmentObject(authStore)
                } else {
                    // 未登录，显示登录界面
                    LoginView()
                        .environmentObject(authStore)
                }
            }
            .onReceive(authStore.$isAuthenticated) { isAuthenticated in
                // 监听认证状态变化
                if isAuthenticated {
                    print("用户已登录")
                } else {
                    print("用户未登录或已登出")
                }
            }
        }
    }
}

// MARK: - 启动画面
struct SplashView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "pawprint.circle.fill")
                .font(.system(size: 100))
                .foregroundColor(.blue)
            
            Text("毛孩子AI")
                .font(.largeTitle)
                .fontWeight(.bold)
                .foregroundColor(Color(hex: "#101618"))
            
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: .blue))
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(hex: "#F9FAFB"))
    }
}

// MARK: - 主内容视图
struct MainContentView: View {
    @EnvironmentObject var authStore: AuthStore
    @StateObject private var petStore = PetStore()
    @StateObject private var feedStore = FeedStore()
    @StateObject private var interactionStore = InteractionStore()
    
    var body: some View {
        TabView {
            FeedView()
                .environmentObject(feedStore)
                .environmentObject(petStore)
                .tabItem {
                    Image(systemName: "house.fill")
                    Text("首页")
                }
            
            InteractionView()
                .environmentObject(interactionStore)
                .environmentObject(petStore)
                .tabItem {
                    Image(systemName: "message.fill")
                    Text("聊天")
                }
            
            ProfileView()
                .environmentObject(petStore)
                .tabItem {
                    Image(systemName: "pawprint.fill")
                    Text("宠物")
                }
            
            UserProfileView(authStore: authStore)
                .tabItem {
                    Image(systemName: "person.fill")
                    Text("我的")
                }
        }
        .accentColor(.blue)
    }
} 