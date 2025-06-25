import SwiftUI

struct FeedView: View {
    @EnvironmentObject var feedStore: FeedStore
    @State private var showingCreateFeed = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // 顶部导航栏
                HStack {
                    Text("毛孩圈")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(Color(hex: "101618"))
                    
                    Spacer()
                    
                    Button(action: {
                        showingCreateFeed = true
                    }) {
                        Image(systemName: "plus.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(Color(hex: "101618"))
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 12)
                .padding(.bottom, 8)
                
                // 动态列表
                ScrollView {
                    LazyVStack(spacing: 16) {
                        ForEach(feedStore.feeds) { feed in
                            FeedCard(feed: feed)
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.top, 8)
                    .padding(.bottom, 80)
                }
                .background(Color(hex: "F9FAFB"))
            }
            .background(Color(hex: "F9FAFB"))
            .navigationBarHidden(true)
            .sheet(isPresented: $showingCreateFeed) {
                CreateFeedView()
                    .environmentObject(feedStore)
            }
        }
    }
}

struct FeedCard: View {
    let feed: Feed
    @EnvironmentObject var feedStore: FeedStore
    @State private var isLiked = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 宠物信息和时间
            HStack {
                // 宠物头像
                Text(feed.petAvatar)
                    .font(.title)
                    .frame(width: 40, height: 40)
                    .background(Color(hex: "eaeff1").opacity(0.5))
                    .clipShape(Circle())
                
                VStack(alignment: .leading, spacing: 2) {
                    // 宠物名称
                    Text(feed.petName)
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(Color(hex: "101618"))
                    
                    // 发布时间
                    Text(feedStore.timeString(feed.createdAt))
                        .font(.system(size: 12))
                        .foregroundColor(Color(hex: "5c7d8a"))
                }
                
                Spacer()
                
                // 更多选项按钮
                Button(action: {
                    // 更多选项功能
                }) {
                    Image(systemName: "ellipsis")
                        .font(.system(size: 20))
                        .foregroundColor(Color(hex: "5c7d8a"))
                }
            }
            
            // 动态内容
            Text(feed.content)
                .font(.system(size: 16))
                .foregroundColor(Color(hex: "101618"))
                .multilineTextAlignment(.leading)
                .fixedSize(horizontal: false, vertical: true)
            
            // 图片
            if !feed.images.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(feed.images, id: \.self) { imageName in
                            // 这里应该使用真实图片，暂时用颜色块代替
                            Rectangle()
                                .fill(Color.gray.opacity(0.2))
                                .frame(width: 200, height: 150)
                                .cornerRadius(12)
                                .overlay(
                                    Text(imageName)
                                        .foregroundColor(Color(hex: "5c7d8a"))
                                )
                        }
                    }
                }
            }
            
            // 互动按钮
            HStack(spacing: 16) {
                // 点赞按钮
                Button(action: {
                    isLiked.toggle()
                    if isLiked {
                        feedStore.likeFeed(feed.id)
                    }
                }) {
                    HStack(spacing: 4) {
                        Image(systemName: isLiked ? "heart.fill" : "heart")
                            .font(.system(size: 16))
                            .foregroundColor(isLiked ? .red : Color(hex: "5c7d8a"))
                        
                        Text("\(feed.likes)")
                            .font(.system(size: 14))
                            .foregroundColor(Color(hex: "5c7d8a"))
                    }
                }
                
                // 评论按钮
                Button(action: {
                    // 评论功能
                }) {
                    HStack(spacing: 4) {
                        Image(systemName: "bubble.left")
                            .font(.system(size: 16))
                            .foregroundColor(Color(hex: "5c7d8a"))
                        
                        Text("\(feed.comments)")
                            .font(.system(size: 14))
                            .foregroundColor(Color(hex: "5c7d8a"))
                    }
                }
                
                // 分享按钮
                Button(action: {
                    // 分享功能
                }) {
                    HStack(spacing: 4) {
                        Image(systemName: "square.and.arrow.up")
                            .font(.system(size: 16))
                            .foregroundColor(Color(hex: "5c7d8a"))
                    }
                }
                
                Spacer()
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(16)
    }
}

#Preview {
    let feedStore: FeedStore = FeedStore()
    
    return FeedView()
        .environmentObject(feedStore)
} 