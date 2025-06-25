import SwiftUI

struct CreateFeedView: View {
    @EnvironmentObject var feedStore: FeedStore
    @EnvironmentObject var petStore: PetStore
    @Environment(\.dismiss) private var dismiss
    
    @State private var content: String = ""
    @State private var selectedImages: [String] = []
    @State private var showingImagePicker = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // 内容输入区域
                VStack(alignment: .leading, spacing: 16) {
                    // 宠物信息
                    HStack(spacing: 12) {
                        // 宠物头像
                        Text(petStore.currentPet.avatar)
                            .font(.title)
                            .frame(width: 40, height: 40)
                            .background(Color(hex: "eaeff1").opacity(0.5))
                            .clipShape(Circle())
                        
                        // 宠物名称
                        Text(petStore.currentPet.name)
                            .font(.system(size: 16, weight: .bold))
                            .foregroundColor(Color(hex: "101618"))
                    }
                    
                    // 文本输入
                    TextEditor(text: $content)
                        .placeholder(when: content.isEmpty) {
                            Text("分享你家毛孩子的日常...")
                                .foregroundColor(Color(hex: "5c7d8a").opacity(0.5))
                                .padding(.top, 8)
                                .padding(.leading, 5)
                        }
                        .font(.system(size: 16))
                        .foregroundColor(Color(hex: "101618"))
                        .frame(minHeight: 120)
                        .padding(8)
                        .background(Color(hex: "F9FAFB"))
                        .cornerRadius(12)
                    
                    // 已选图片预览
                    if !selectedImages.isEmpty {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 8) {
                                ForEach(selectedImages, id: \.self) { imageName in
                                    ZStack(alignment: .topTrailing) {
                                        // 这里应该使用真实图片，暂时用颜色块代替
                                        Rectangle()
                                            .fill(Color.gray.opacity(0.2))
                                            .frame(width: 100, height: 100)
                                            .cornerRadius(8)
                                            .overlay(
                                                Text(imageName)
                                                    .foregroundColor(Color(hex: "5c7d8a"))
                                            )
                                        
                                        // 删除按钮
                                        Button(action: {
                                            if let index = selectedImages.firstIndex(of: imageName) {
                                                selectedImages.remove(at: index)
                                            }
                                        }) {
                                            Image(systemName: "xmark.circle.fill")
                                                .foregroundColor(.white)
                                                .background(Color.black.opacity(0.6))
                                                .clipShape(Circle())
                                        }
                                        .padding(4)
                                    }
                                }
                            }
                        }
                    }
                    
                    // 功能按钮
                    HStack(spacing: 16) {
                        // 添加图片
                        Button(action: {
                            showingImagePicker = true
                            // 模拟选择图片
                            selectedImages.append("新图片\(selectedImages.count + 1)")
                        }) {
                            HStack(spacing: 8) {
                                Image(systemName: "photo")
                                    .font(.system(size: 20))
                                    .foregroundColor(Color(hex: "5c7d8a"))
                                
                                Text("添加图片")
                                    .font(.system(size: 14))
                                    .foregroundColor(Color(hex: "5c7d8a"))
                            }
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(Color(hex: "eaeff1"))
                            .cornerRadius(16)
                        }
                        
                        Spacer()
                        
                        // 发布按钮
                        Button(action: publishFeed) {
                            Text("发布")
                                .font(.system(size: 16, weight: .medium))
                                .foregroundColor(.white)
                                .padding(.horizontal, 24)
                                .padding(.vertical, 10)
                                .background(
                                    content.isEmpty ? Color(hex: "5c7d8a").opacity(0.5) : Color(hex: "5c7d8a")
                                )
                                .cornerRadius(20)
                        }
                        .disabled(content.isEmpty)
                    }
                }
                .padding(16)
                
                Spacer()
            }
            .navigationTitle("创建动态")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    private func publishFeed() {
        feedStore.addFeed(
            content: content,
            images: selectedImages,
            petId: petStore.currentPet.id,
            petName: petStore.currentPet.name,
            petAvatar: petStore.currentPet.avatar
        )
        
        dismiss()
    }
}

// 文本编辑器占位符扩展
extension View {
    func placeholder<Content: View>(
        when shouldShow: Bool,
        alignment: Alignment = .leading,
        @ViewBuilder placeholder: () -> Content
    ) -> some View {
        ZStack(alignment: alignment) {
            placeholder().opacity(shouldShow ? 1 : 0)
            self
        }
    }
}

#Preview {
    let feedStore: FeedStore = FeedStore()
    let petStore: PetStore = PetStore()
    
    return CreateFeedView()
        .environmentObject(feedStore)
        .environmentObject(petStore)
} 