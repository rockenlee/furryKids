import Foundation
import Combine
import SwiftUI

class AuthStore: ObservableObject {
    @Published var currentUser: User?
    @Published var isAuthenticated = false
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    // 公开cancellables属性
    var cancellables = Set<AnyCancellable>()
    private let authService = AuthService.shared
    
    init() {
        checkAuthStatus()
    }
    
    // MARK: - 检查认证状态
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
    
    // MARK: - 用户登录
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
    
    // MARK: - 用户注册
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
    
    // MARK: - 用户登出
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
    
    // MARK: - 清除错误信息
    func clearError() {
        errorMessage = nil
    }
} 