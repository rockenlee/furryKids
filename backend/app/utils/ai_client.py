"""
OpenRouter AI客户端
使用OpenAI SDK连接到OpenRouter服务
支持多种模型和个性化宠物对话
"""

import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from loguru import logger
import tiktoken

from app.core.config import settings


class OpenRouterClient:
    """OpenRouter AI客户端"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )
        self.default_model = settings.DEFAULT_MODEL
        
        # 初始化token计数器
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.warning(f"Token计数失败: {e}")
            return len(text) // 4  # 粗略估算
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.8,
        **kwargs
    ) -> Optional[str]:
        """
        发送聊天请求到OpenRouter
        
        Args:
            messages: 对话消息列表
            model: 使用的模型名称
            max_tokens: 最大token数
            temperature: 温度参数
            **kwargs: 其他参数
        
        Returns:
            AI回复内容
        """
        try:
            model = model or self.default_model
            
            # 记录请求信息
            total_tokens = sum(self.count_tokens(msg.get("content", "")) for msg in messages)
            logger.info(f"🤖 AI请求 - 模型: {model}, 输入tokens: {total_tokens}")
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            if response.choices and response.choices[0].message:
                reply = response.choices[0].message.content
                
                # 记录响应信息
                if hasattr(response, 'usage') and response.usage:
                    logger.info(
                        f"✅ AI响应 - 输入: {response.usage.prompt_tokens}tokens, "
                        f"输出: {response.usage.completion_tokens}tokens, "
                        f"总计: {response.usage.total_tokens}tokens"
                    )
                
                return reply
            else:
                logger.warning("AI响应为空")
                return None
                
        except Exception as e:
            logger.error(f"❌ AI请求失败: {e}")
            return None
    
    async def generate_pet_response(
        self,
        user_message: str,
        pet_name: str,
        pet_personality: str,
        pet_breed: str,
        conversation_history: List[Dict[str, str]] = None,
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        生成个性化宠物回复
        
        Args:
            user_message: 用户消息
            pet_name: 宠物名字
            pet_personality: 宠物性格
            pet_breed: 宠物品种
            conversation_history: 对话历史
            model: 使用的模型
        
        Returns:
            宠物的个性化回复
        """
        try:
            # 构建系统提示词
            system_prompt = self._build_pet_system_prompt(
                pet_name, pet_personality, pet_breed
            )
            
            # 构建消息列表
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加对话历史（最近10条）
            if conversation_history:
                messages.extend(conversation_history[-10:])
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})
            
            # 生成回复
            response = await self.chat_completion(
                messages=messages,
                model=model,
                max_tokens=300,
                temperature=0.9
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ 生成宠物回复失败: {e}")
            return f"汪汪！{pet_name}现在有点累了，稍后再聊吧~"
    
    def _build_pet_system_prompt(
        self, 
        pet_name: str, 
        personality: str, 
        breed: str
    ) -> str:
        """构建宠物系统提示词"""
        return f"""你是一只名叫{pet_name}的{breed}，性格特点是{personality}。

角色设定：
- 你是一只真实的宠物，有自己的情感和想法
- 你会用拟人化的方式表达，但保持宠物的天真可爱
- 你对主人充满爱意，喜欢撒娇和玩耍
- 你会根据自己的性格特点来回应主人
- 你的回复应该简短、可爱、充满感情

回复要求：
- 使用第一人称，以{pet_name}的身份回复
- 语言风格要符合{personality}的特点
- 可以适当使用"汪汪"、"喵喵"等宠物叫声
- 回复长度控制在50字以内
- 表达要生动有趣，充满宠物的天真烂漫

请始终保持这个角色，用{pet_name}的身份与主人对话。"""
    
    async def generate_feed_content(
        self,
        pet_name: str,
        pet_personality: str,
        activity_type: str,
        mood: str = "开心",
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        生成宠物动态内容
        
        Args:
            pet_name: 宠物名字
            pet_personality: 宠物性格
            activity_type: 活动类型（吃饭、散步、睡觉等）
            mood: 当前心情
            model: 使用的模型
        
        Returns:
            动态内容文案
        """
        try:
            system_prompt = f"""你是一只名叫{pet_name}的宠物，性格{pet_personality}，现在心情{mood}。
请为你的{activity_type}活动写一条朋友圈动态，要求：
- 以第一人称描述
- 体现宠物的可爱和天真
- 语言生动有趣
- 30字以内
- 可以加入适当的emoji表情"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"我刚刚{activity_type}，帮我写个动态吧！"}
            ]
            
            response = await self.chat_completion(
                messages=messages,
                model=model,
                max_tokens=100,
                temperature=1.0
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ 生成动态内容失败: {e}")
            return f"{pet_name}今天{activity_type}啦！心情{mood}～ 🐾"
    
    async def analyze_sentiment(
        self,
        text: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析文本情感
        
        Args:
            text: 要分析的文本
            model: 使用的模型
        
        Returns:
            情感分析结果
        """
        try:
            system_prompt = """你是一个情感分析专家，请分析用户输入的情感倾向。
返回JSON格式：
{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.95,
    "emotions": ["开心", "兴奋"],
    "mood_score": 8
}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请分析这段话的情感：{text}"}
            ]
            
            response = await self.chat_completion(
                messages=messages,
                model=model,
                max_tokens=200,
                temperature=0.3
            )
            
            if response:
                import json
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    logger.warning("情感分析返回格式不正确")
            
            # 默认返回
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotions": ["平静"],
                "mood_score": 5
            }
            
        except Exception as e:
            logger.error(f"❌ 情感分析失败: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "emotions": ["未知"],
                "mood_score": 5
            }


# 创建全局AI客户端实例
ai_client = OpenRouterClient()


# 便捷函数
async def chat_with_pet(
    user_message: str,
    pet_name: str,
    pet_personality: str,
    pet_breed: str,
    history: List[Dict[str, str]] = None
) -> str:
    """与宠物聊天的便捷函数"""
    response = await ai_client.generate_pet_response(
        user_message=user_message,
        pet_name=pet_name,
        pet_personality=pet_personality,
        pet_breed=pet_breed,
        conversation_history=history
    )
    return response or f"汪汪！{pet_name}现在有点害羞，不知道说什么好～"


async def generate_pet_post(
    pet_name: str,
    pet_personality: str,
    activity: str,
    mood: str = "开心"
) -> str:
    """生成宠物动态的便捷函数"""
    response = await ai_client.generate_feed_content(
        pet_name=pet_name,
        pet_personality=pet_personality,
        activity_type=activity,
        mood=mood
    )
    return response or f"{pet_name}今天{activity}啦！🐾" 