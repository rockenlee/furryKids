import SwiftUI

// TabBarButton组件定义在当前文件中，使用fileprivate避免命名冲突
fileprivate struct TabBarButton: View {
    let icon: String
    let label: String
    let isActive: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.system(size: 24))
                    .foregroundColor(isActive ? Color(hex: "101618") : Color(hex: "5c7d8a"))
                
                Text(label)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(isActive ? Color(hex: "101618") : Color(hex: "5c7d8a"))
            }
            .frame(maxWidth: .infinity)
        }
    }
}

struct InteractionView: View {
    @EnvironmentObject var interactionStore: InteractionStore
    @EnvironmentObject var petStore: PetStore
    @State private var messageText = ""
    @State private var scrollProxy: ScrollViewProxy?
    
    var body: some View {
        VStack(spacing: 0) {
            // 顶部导航栏
            HStack {
                Button(action: {
                    // 返回按钮功能
                }) {
                    Image(systemName: "arrow.left")
                        .font(.system(size: 24))
                        .foregroundColor(Color(hex: "101618"))
                }
                
                Spacer()
                
                Text(petStore.currentPet.name)
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(Color(hex: "101618"))
                
                Spacer()
                
                // 占位，保持标题居中
                Color.clear
                    .frame(width: 24, height: 24)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color(hex: "F9FAFB"))
            
            // 消息列表
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(spacing: 12) {
                        ForEach(interactionStore.messages) { message in
                            MessageBubbleView(message: message, petAvatar: petStore.currentPet.avatar)
                                .id(message.id)
                        }
                        
                        // 打字指示器
                        if interactionStore.isTyping {
                            TypingIndicatorView(petAvatar: petStore.currentPet.avatar)
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.top, 16)
                }
                .background(Color(hex: "F9FAFB"))
                .onAppear {
                    scrollProxy = proxy
                }
                .onChange(of: interactionStore.messages.count) { _ in
                    scrollToBottom()
                }
                .onChange(of: interactionStore.isTyping) { _ in
                    scrollToBottom()
                }
            }
            
            // 输入区域
            VStack(spacing: 0) {
                // 消息输入框
                HStack(spacing: 12) {
                    // 文本输入框
                    HStack {
                        TextField("输入消息...", text: $messageText)
                            .padding(.horizontal, 16)
                            .font(.system(size: 16))
                            .frame(height: 48)
                        
                        // 图片按钮
                        Button(action: {
                            // 添加图片功能
                        }) {
                            Image(systemName: "photo")
                                .font(.system(size: 20))
                                .foregroundColor(Color(hex: "5c7d8a"))
                                .padding(.trailing, 8)
                        }
                    }
                    .background(Color(hex: "eaeff1"))
                    .cornerRadius(12)
                    
                    // 发送按钮
                    Button(action: sendMessage) {
                        Text("发送")
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(Color(hex: "101618"))
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(Color(hex: "dcedf3"))
                            .cornerRadius(16)
                    }
                    .opacity(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? 0.5 : 1)
                    .disabled(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
                .padding(.horizontal, 16)
                .padding(.top, 12)
                .padding(.bottom, 8)
            }
        }
        .background(Color(hex: "F9FAFB"))
    }
    
    private func sendMessage() {
        let trimmedMessage = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedMessage.isEmpty else { return }
        
        interactionStore.sendMessage(trimmedMessage)
        messageText = ""
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            scrollToBottom()
        }
    }
    
    private func scrollToBottom() {
        guard let proxy = scrollProxy else { return }
        
        if let lastMessage = interactionStore.messages.last {
            withAnimation(.easeInOut(duration: 0.3)) {
                proxy.scrollTo(lastMessage.id, anchor: .bottom)
            }
        }
    }
}

struct MessageBubbleView: View {
    let message: Message
    let petAvatar: String
    
    var body: some View {
        HStack(alignment: .bottom, spacing: 8) {
            if message.type == .pet {
                // 宠物头像
                Text(petAvatar)
                    .font(.title2)
                    .frame(width: 40, height: 40)
                    .background(Color(hex: "eaeff1").opacity(0.5))
                    .clipShape(Circle())
                
                VStack(alignment: .leading, spacing: 4) {
                    // 宠物昵称
                    Text(message.type == .pet ? "Buddy" : "")
                        .font(.system(size: 13))
                        .foregroundColor(Color(hex: "5c7d8a"))
                    
                    // 消息内容
                    Text(message.content)
                        .font(.system(size: 16))
                        .foregroundColor(Color(hex: "101618"))
                        .padding(.horizontal, 16)
                        .padding(.vertical, 12)
                        .background(Color(hex: "eaeff1"))
                        .cornerRadius(16)
                }
                
                Spacer()
            } else {
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    // 用户昵称
                    Text("Olivia")
                        .font(.system(size: 13))
                        .foregroundColor(Color(hex: "5c7d8a"))
                    
                    // 消息内容
                    Text(message.content)
                        .font(.system(size: 16))
                        .foregroundColor(Color(hex: "101618"))
                        .padding(.horizontal, 16)
                        .padding(.vertical, 12)
                        .background(Color(hex: "dcedf3"))
                        .cornerRadius(16)
                }
                
                // 用户头像
                Text("👤")
                    .font(.title2)
                    .frame(width: 40, height: 40)
                    .background(Color(hex: "dcedf3").opacity(0.5))
                    .clipShape(Circle())
            }
        }
        .padding(.vertical, 4)
    }
}

struct TypingIndicatorView: View {
    let petAvatar: String
    @State private var showDots = false
    
    var body: some View {
        HStack(alignment: .bottom, spacing: 8) {
            // 宠物头像
            Text(petAvatar)
                .font(.title2)
                .frame(width: 40, height: 40)
                .background(Color(hex: "eaeff1").opacity(0.5))
                .clipShape(Circle())
            
            // 打字指示器
            HStack(spacing: 4) {
                ForEach(0..<3) { index in
                    Circle()
                        .fill(Color(hex: "5c7d8a"))
                        .frame(width: 8, height: 8)
                        .opacity(showDots ? 1 : 0.3)
                        .animation(Animation.easeInOut(duration: 0.4).repeatForever().delay(0.2 * Double(index)), value: showDots)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color(hex: "eaeff1"))
            .cornerRadius(16)
            
            Spacer()
        }
        .padding(.vertical, 4)
        .onAppear {
            showDots = true
        }
    }
}

#Preview {
    let interactionStore: InteractionStore = InteractionStore()
    let petStore: PetStore = PetStore()
    
    return InteractionView()
        .environmentObject(interactionStore)
        .environmentObject(petStore)
} 