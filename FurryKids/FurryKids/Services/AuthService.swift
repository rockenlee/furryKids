import Foundation
import Combine

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
        
        // 重要：设置Cookie支持
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
        guard let url = URL(string: "\(baseURL)/auth/user") else {
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