import Foundation
import Combine

// MARK: - Data Service Models
struct UserProfile: Codable {
    let id: String
    let username: String
    let email: String
    let avatar: String?
    let createdAt: Date
    let updatedAt: Date
}

struct PetProfile: Codable {
    let id: String
    let userId: String
    let name: String
    let type: String
    let breed: String?
    let personality: String
    let avatar: String?
    let birthday: Date?
    let weight: Double?
    let healthStatus: String
    let lastFeedTime: Date?
    let lastWalkTime: Date?
    let createdAt: Date
    let updatedAt: Date
}

struct FeedPost: Codable {
    let id: String
    let petId: String
    let userId: String
    let content: String
    let images: [String]
    let likes: Int
    let comments: Int
    let shares: Int
    let isLiked: Bool
    let mood: String
    let topics: [String]
    let location: String?
    let createdAt: Date
    let updatedAt: Date
}

struct ChatMessage: Codable {
    let id: String
    let petId: String
    let userId: String
    let content: String
    let type: MessageType
    let mood: String?
    let actions: [String]?
    let timestamp: Date
    let isRead: Bool
}

// MARK: - Data Service Protocol
protocol DataServiceProtocol {
    // User Management
    func loginUser(email: String, password: String) -> AnyPublisher<UserProfile, APIError>
    func registerUser(username: String, email: String, password: String) -> AnyPublisher<UserProfile, APIError>
    func updateUserProfile(_ profile: UserProfile) -> AnyPublisher<UserProfile, APIError>
    
    // Pet Management
    func getUserPets(userId: String) -> AnyPublisher<[PetProfile], APIError>
    func createPet(_ pet: PetProfile) -> AnyPublisher<PetProfile, APIError>
    func updatePet(_ pet: PetProfile) -> AnyPublisher<PetProfile, APIError>
    func deletePet(petId: String) -> AnyPublisher<Bool, APIError>
    
    // Feed Management
    func getFeeds(page: Int, limit: Int) -> AnyPublisher<[FeedPost], APIError>
    func getUserFeeds(userId: String, page: Int, limit: Int) -> AnyPublisher<[FeedPost], APIError>
    func createFeed(_ feed: FeedPost) -> AnyPublisher<FeedPost, APIError>
    func likeFeed(feedId: String) -> AnyPublisher<Bool, APIError>
    func deleteFeed(feedId: String) -> AnyPublisher<Bool, APIError>
    
    // Chat Management
    func getChatHistory(petId: String, page: Int, limit: Int) -> AnyPublisher<[ChatMessage], APIError>
    func saveChatMessage(_ message: ChatMessage) -> AnyPublisher<ChatMessage, APIError>
    func markMessagesAsRead(petId: String) -> AnyPublisher<Bool, APIError>
}

// MARK: - Data Service Implementation
class DataService: DataServiceProtocol {
    static let shared = DataService()
    
    private let networkManager = NetworkManager.shared
    private var cancellables = Set<AnyCancellable>()
    
    // Local cache
    @Published var currentUser: UserProfile?
    @Published var userPets: [PetProfile] = []
    @Published var cachedFeeds: [FeedPost] = []
    
    private init() {}
    
    // MARK: - User Management
    func loginUser(email: String, password: String) -> AnyPublisher<UserProfile, APIError> {
        let loginData = [
            "email": email,
            "password": password
        ]
        
        guard let requestData = try? JSONSerialization.data(withJSONObject: loginData) else {
            return Fail(error: APIError.decodingError)
                .eraseToAnyPublisher()
        }
        
        return networkManager.request(
            endpoint: "/auth/login",
            method: .POST,
            body: requestData,
            responseType: APIResponse<UserProfile>.self
        )
        .compactMap { $0.data }
        .handleEvents(receiveOutput: { [weak self] user in
            self?.currentUser = user
        })
        .eraseToAnyPublisher()
    }
    
    func registerUser(username: String, email: String, password: String) -> AnyPublisher<UserProfile, APIError> {
        let registerData = [
            "username": username,
            "email": email,
            "password": password
        ]
        
        guard let requestData = try? JSONSerialization.data(withJSONObject: registerData) else {
            return Fail(error: APIError.decodingError)
                .eraseToAnyPublisher()
        }
        
        return networkManager.request(
            endpoint: "/auth/register",
            method: .POST,
            body: requestData,
            responseType: APIResponse<UserProfile>.self
        )
        .compactMap { $0.data }
        .handleEvents(receiveOutput: { [weak self] user in
            self?.currentUser = user
        })
        .eraseToAnyPublisher()
    }
    
    func updateUserProfile(_ profile: UserProfile) -> AnyPublisher<UserProfile, APIError> {
        guard let requestData = try? JSONEncoder().encode(profile) else {
            return Fail(error: APIError.decodingError)
                .eraseToAnyPublisher()
        }
        
        return networkManager.request(
            endpoint: "/user/profile",
            method: .PUT,
            body: requestData,
            responseType: APIResponse<UserProfile>.self
        )
        .compactMap { $0.data }
        .handleEvents(receiveOutput: { [weak self] user in
            self?.currentUser = user
        })
        .eraseToAnyPublisher()
    }
    
    // MARK: - Pet Management
    func getUserPets(userId: String) -> AnyPublisher<[PetProfile], APIError> {
        return networkManager.request(
            endpoint: "/pets/user/\(userId)",
            method: .GET,
            responseType: APIResponse<[PetProfile]>.self
        )
        .compactMap { $0.data }
        .handleEvents(receiveOutput: { [weak self] pets in
            self?.userPets = pets
        })
        .eraseToAnyPublisher()
    }
    
    func createPet(_ pet: PetProfile) -> AnyPublisher<PetProfile, APIError> {
        guard let requestData = try? JSONEncoder().encode(pet) else {
            return Fail(error: APIError.decodingError)
                .eraseToAnyPublisher()
        }
        
        return networkManager.request(
            endpoint: "/pets",
            method: .POST,
            body: requestData,
            responseType: APIResponse<PetProfile>.self
        )
        .compactMap { $0.data }
        .handleEvents(receiveOutput: { [weak self] newPet in
            self?.userPets.append(newPet)
        })
        .eraseToAnyPublisher()
    }
    
    func updatePet(_ pet: PetProfile) -> AnyPublisher<PetProfile, APIError> {
        guard let requestData = try? JSONEncoder().encode(pet) else {
            return Fail(error: APIError.decodingError)
                .eraseToAnyPublisher()
        }
        
        return networkManager.request(
            endpoint: "/pets/\(pet.id)",
            method: .PUT,
            body: requestData,
            responseType: APIResponse<PetProfile>.self
        )
        .compactMap { $0.data }
        .handleEvents(receiveOutput: { [weak self] updatedPet in
            if let index = self?.userPets.firstIndex(where: { $0.id == updatedPet.id }) {
                self?.userPets[index] = updatedPet
            }
        })
        .eraseToAnyPublisher()
    }
    
    func deletePet(petId: String) -> AnyPublisher<Bool, APIError> {
        return networkManager.request(
            endpoint: "/pets/\(petId)",
            method: .DELETE,
            responseType: APIResponse<Bool>.self
        )
        .compactMap { $0.data }
        .handleEvents(receiveOutput: { [weak self] success in
            if success {
                self?.userPets.removeAll { $0.id == petId }
            }
        })
        .eraseToAnyPublisher()
    }
    
    // MARK: - Feed Management
    func getFeeds(page: Int, limit: Int) -> AnyPublisher<[FeedPost], APIError> {
        return networkManager.request(
            endpoint: "/feeds?page=\(page)&limit=\(limit)",
            method: .GET,
            responseType: APIResponse<[FeedPost]>.self
        )
        .compactMap { $0.data }
        .handleEvents(receiveOutput: { [weak self] feeds in
            if page == 1 {
                self?.cachedFeeds = feeds
            } else {
                self?.cachedFeeds.append(contentsOf: feeds)
            }
        })
        .eraseToAnyPublisher()
    }
    
    func getUserFeeds(userId: String, page: Int, limit: Int) -> AnyPublisher<[FeedPost], APIError> {
        return networkManager.request(
            endpoint: "/feeds/user/\(userId)?page=\(page)&limit=\(limit)",
            method: .GET,
            responseType: APIResponse<[FeedPost]>.self
        )
        .compactMap { $0.data }
        .eraseToAnyPublisher()
    }
    
    func createFeed(_ feed: FeedPost) -> AnyPublisher<FeedPost, APIError> {
        guard let requestData = try? JSONEncoder().encode(feed) else {
            return Fail(error: APIError.decodingError)
                .eraseToAnyPublisher()
        }
        
        return networkManager.request(
            endpoint: "/feeds",
            method: .POST,
            body: requestData,
            responseType: APIResponse<FeedPost>.self
        )
        .compactMap { $0.data }
        .handleEvents(receiveOutput: { [weak self] newFeed in
            self?.cachedFeeds.insert(newFeed, at: 0)
        })
        .eraseToAnyPublisher()
    }
    
    func likeFeed(feedId: String) -> AnyPublisher<Bool, APIError> {
        return networkManager.request(
            endpoint: "/feeds/\(feedId)/like",
            method: .POST,
            responseType: APIResponse<Bool>.self
        )
        .compactMap { $0.data }
        .eraseToAnyPublisher()
    }
    
    func deleteFeed(feedId: String) -> AnyPublisher<Bool, APIError> {
        return networkManager.request(
            endpoint: "/feeds/\(feedId)",
            method: .DELETE,
            responseType: APIResponse<Bool>.self
        )
        .compactMap { $0.data }
        .handleEvents(receiveOutput: { [weak self] success in
            if success {
                self?.cachedFeeds.removeAll { $0.id == feedId }
            }
        })
        .eraseToAnyPublisher()
    }
    
    // MARK: - Chat Management
    func getChatHistory(petId: String, page: Int, limit: Int) -> AnyPublisher<[ChatMessage], APIError> {
        return networkManager.request(
            endpoint: "/chat/\(petId)/history?page=\(page)&limit=\(limit)",
            method: .GET,
            responseType: APIResponse<[ChatMessage]>.self
        )
        .compactMap { $0.data }
        .eraseToAnyPublisher()
    }
    
    func saveChatMessage(_ message: ChatMessage) -> AnyPublisher<ChatMessage, APIError> {
        guard let requestData = try? JSONEncoder().encode(message) else {
            return Fail(error: APIError.decodingError)
                .eraseToAnyPublisher()
        }
        
        return networkManager.request(
            endpoint: "/chat/messages",
            method: .POST,
            body: requestData,
            responseType: APIResponse<ChatMessage>.self
        )
        .compactMap { $0.data }
        .eraseToAnyPublisher()
    }
    
    func markMessagesAsRead(petId: String) -> AnyPublisher<Bool, APIError> {
        return networkManager.request(
            endpoint: "/chat/\(petId)/read",
            method: .POST,
            responseType: APIResponse<Bool>.self
        )
        .compactMap { $0.data }
        .eraseToAnyPublisher()
    }
    
    // MARK: - Cache Management
    func clearCache() {
        currentUser = nil
        userPets.removeAll()
        cachedFeeds.removeAll()
    }
    
    func syncOfflineData() -> AnyPublisher<Bool, APIError> {
        // TODO: 实现离线数据同步逻辑
        return Just(true)
            .setFailureType(to: APIError.self)
            .eraseToAnyPublisher()
    }
} 