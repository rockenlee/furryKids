import SwiftUI
import Combine

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
                    // 用户名输入框
                    VStack(alignment: .leading, spacing: 8) {
                        Text("用户名")
                            .font(.headline)
                            .foregroundColor(Color(hex: "#101618"))
                        
                        TextField("请输入用户名", text: $username)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .autocapitalization(.none)
                            .disableAutocorrection(true)
                    }
                    
                    // 密码输入框
                    VStack(alignment: .leading, spacing: 8) {
                        Text("密码")
                            .font(.headline)
                            .foregroundColor(Color(hex: "#101618"))
                        
                        SecureField("请输入密码", text: $password)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                    }
                    
                    // 错误信息显示
                    if let errorMessage = authStore.errorMessage {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.caption)
                            .multilineTextAlignment(.center)
                    }
                    
                    // 登录/注册按钮
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
                    
                    // 切换登录/注册模式
                    Button(action: {
                        isRegistering.toggle()
                        authStore.clearError()
                    }) {
                        Text(isRegistering ? "已有账户？点击登录" : "没有账户？点击注册")
                            .foregroundColor(.blue)
                            .font(.subheadline)
                    }
                    
                    // 测试连接按钮
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
                
                // OAuth 登录区域（预留）
                VStack(spacing: 16) {
                    Text("或使用以下方式登录")
                        .font(.caption)
                        .foregroundColor(Color(hex: "#5c7d8a"))
                    
                    HStack(spacing: 20) {
                        // Google 登录按钮
                        Button(action: {
                            // TODO: 实现 Google OAuth 登录
                        }) {
                            HStack {
                                Image(systemName: "globe")
                                Text("Google")
                            }
                            .foregroundColor(.gray)
                            .frame(width: 120, height: 40)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.gray, lineWidth: 1)
                            )
                        }
                        
                        // Facebook 登录按钮
                        Button(action: {
                            // TODO: 实现 Facebook OAuth 登录
                        }) {
                            HStack {
                                Image(systemName: "person.circle")
                                Text("Facebook")
                            }
                            .foregroundColor(.gray)
                            .frame(width: 120, height: 40)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.gray, lineWidth: 1)
                            )
                        }
                    }
                }
                .padding(.bottom, 30)
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
    
    // MARK: - 测试服务器连接
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