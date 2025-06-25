import Foundation
import Combine

// MARK: - API Configuration
struct APIConfig {
    static let baseURL = "https://your-backend-api.com/api/v1"
    static let aiServiceURL = "https://your-ai-service.com/api"
    
    // 如果使用OpenAI或其他AI服务
    static let openAIKey = "your-openai-api-key"
    static let openAIURL = "https://api.openai.com/v1"
}

// MARK: - API Errors
enum APIError: Error, LocalizedError {
    case invalidURL
    case noData
    case decodingError
    case networkError(Error)
    case serverError(Int)
    case unauthorized
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "无效的URL"
        case .noData:
            return "没有数据返回"
        case .decodingError:
            return "数据解析失败"
        case .networkError(let error):
            return "网络错误: \(error.localizedDescription)"
        case .serverError(let code):
            return "服务器错误: \(code)"
        case .unauthorized:
            return "未授权访问"
        }
    }
}

// MARK: - Network Manager
class NetworkManager: ObservableObject {
    static let shared = NetworkManager()
    
    private let session = URLSession.shared
    private var cancellables = Set<AnyCancellable>()
    
    @Published var isConnected = true
    @Published var isLoading = false
    
    private init() {
        setupNetworkMonitoring()
    }
    
    private func setupNetworkMonitoring() {
        // 简单的网络监控
        // 在实际项目中可以使用Network framework
    }
    
    // MARK: - Generic Request Method
    func request<T: Codable>(
        endpoint: String,
        method: HTTPMethod = .GET,
        body: Data? = nil,
        headers: [String: String] = [:],
        responseType: T.Type
    ) -> AnyPublisher<T, APIError> {
        
        guard let url = URL(string: APIConfig.baseURL + endpoint) else {
            return Fail(error: APIError.invalidURL)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.httpBody = body
        
        // 默认headers
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        // 添加自定义headers
        for (key, value) in headers {
            request.setValue(value, forHTTPHeaderField: key)
        }
        
        return session.dataTaskPublisher(for: request)
            .map(\.data)
            .decode(type: responseType, decoder: JSONDecoder())
            .mapError { error in
                if error is DecodingError {
                    return APIError.decodingError
                } else {
                    return APIError.networkError(error)
                }
            }
            .eraseToAnyPublisher()
    }
    
    // MARK: - Upload Method (for images)
    func uploadImage(
        endpoint: String,
        imageData: Data,
        fileName: String
    ) -> AnyPublisher<UploadResponse, APIError> {
        
        guard let url = URL(string: APIConfig.baseURL + endpoint) else {
            return Fail(error: APIError.invalidURL)
                .eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        let body = createMultipartBody(boundary: boundary, imageData: imageData, fileName: fileName)
        request.httpBody = body
        
        return session.dataTaskPublisher(for: request)
            .map(\.data)
            .decode(type: UploadResponse.self, decoder: JSONDecoder())
            .mapError { error in
                if error is DecodingError {
                    return APIError.decodingError
                } else {
                    return APIError.networkError(error)
                }
            }
            .eraseToAnyPublisher()
    }
    
    private func createMultipartBody(boundary: String, imageData: Data, fileName: String) -> Data {
        var body = Data()
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"image\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        
        return body
    }
}

// MARK: - HTTP Methods
enum HTTPMethod: String {
    case GET = "GET"
    case POST = "POST"
    case PUT = "PUT"
    case DELETE = "DELETE"
    case PATCH = "PATCH"
}

// MARK: - Response Models
struct UploadResponse: Codable {
    let success: Bool
    let imageUrl: String?
    let message: String?
}

struct APIResponse<T: Codable>: Codable {
    let success: Bool
    let data: T?
    let message: String?
    let error: String?
} 