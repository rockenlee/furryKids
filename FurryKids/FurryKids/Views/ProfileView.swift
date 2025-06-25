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

struct ProfileView: View {
    @EnvironmentObject var petStore: PetStore
    
    var body: some View {
        VStack(spacing: 0) {
            // 用户信息
            VStack(spacing: 16) {
                // 头像
                Image(systemName: "person.circle.fill")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 80, height: 80)
                    .foregroundColor(Color(hex: "5c7d8a"))
                
                // 用户名
                Text("Olivia")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(Color(hex: "101618"))
                
                // 简介
                Text("Proud pet owner")
                    .font(.system(size: 16))
                    .foregroundColor(Color(hex: "5c7d8a"))
                    .padding(.bottom, 16)
                
                // 统计数据
                HStack(spacing: 40) {
                    VStack(spacing: 4) {
                        Text("\(petStore.pets.count)")
                            .font(.system(size: 18, weight: .bold))
                            .foregroundColor(Color(hex: "101618"))
                        
                        Text("宠物")
                            .font(.system(size: 14))
                            .foregroundColor(Color(hex: "5c7d8a"))
                    }
                    
                    VStack(spacing: 4) {
                        Text("143")
                            .font(.system(size: 18, weight: .bold))
                            .foregroundColor(Color(hex: "101618"))
                        
                        Text("动态")
                            .font(.system(size: 14))
                            .foregroundColor(Color(hex: "5c7d8a"))
                    }
                    
                    VStack(spacing: 4) {
                        Text("562")
                            .font(.system(size: 18, weight: .bold))
                            .foregroundColor(Color(hex: "101618"))
                        
                        Text("关注")
                            .font(.system(size: 14))
                            .foregroundColor(Color(hex: "5c7d8a"))
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.top, 32)
            .padding(.bottom, 32)
            .background(Color(hex: "F9FAFB"))
            
            // 我的宠物列表
            VStack(alignment: .leading, spacing: 16) {
                Text("我的宠物")
                    .font(.system(size: 18, weight: .bold))
                    .foregroundColor(Color(hex: "101618"))
                    .padding(.horizontal, 16)
                    .padding(.top, 16)
                
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 16) {
                        ForEach(petStore.pets) { pet in
                            PetCardView(pet: pet)
                                .onTapGesture {
                                    petStore.setCurrentPet(pet)
                                }
                        }
                    }
                    .padding(.horizontal, 16)
                }
                .padding(.bottom, 24)
                
                // 设置和帮助
                VStack(spacing: 0) {
                    ProfileMenuItemView(icon: "gear", title: "设置")
                    ProfileMenuItemView(icon: "questionmark.circle", title: "帮助与反馈")
                    ProfileMenuItemView(icon: "info.circle", title: "关于我们")
                }
            }
            .background(Color.white)
            
            Spacer()
            
            // 删除底部导航栏，因为已经在ContentView中有TabView了
        }
    }
}

struct PetCardView: View {
    let pet: Pet
    
    var body: some View {
        VStack(spacing: 8) {
            // 宠物头像
            Text(pet.avatar)
                .font(.system(size: 32))
                .frame(width: 80, height: 80)
                .background(Color(hex: "eaeff1").opacity(0.5))
                .clipShape(Circle())
            
            // 宠物名称
            Text(pet.name)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(Color(hex: "101618"))
                .lineLimit(1)
        }
        .frame(width: 90)
    }
}

struct ProfileMenuItemView: View {
    let icon: String
    let title: String
    
    var body: some View {
        Button(action: {
            // 菜单项点击功能
        }) {
            HStack(spacing: 12) {
                Image(systemName: icon)
                    .font(.system(size: 18))
                    .foregroundColor(Color(hex: "5c7d8a"))
                    .frame(width: 24, height: 24)
                
                Text(title)
                    .font(.system(size: 16))
                    .foregroundColor(Color(hex: "101618"))
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14))
                    .foregroundColor(Color(hex: "5c7d8a"))
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 16)
        }
        .background(Color.white)
        .overlay(
            Rectangle()
                .frame(height: 1)
                .foregroundColor(Color(hex: "eaeff1")),
            alignment: .bottom
        )
    }
}

#Preview {
    let petStore = PetStore()
    return ProfileView()
        .environmentObject(petStore)
} 