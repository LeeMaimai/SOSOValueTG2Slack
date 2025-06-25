import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置管理类"""
    
    # Telegram配置
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')
    
    # Slack配置
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SLACK_CHANNEL_A = os.getenv('SLACK_CHANNEL_A')  # 画板频道
    SLACK_CHANNEL_B = os.getenv('SLACK_CHANNEL_B')  # 消息频道
    
    # 应用配置
    CONTENT_FILTER_KEYWORDS = os.getenv('CONTENT_FILTER_KEYWORDS', '').split(',')
    SCHEDULE_INTERVAL_MINUTES = int(os.getenv('SCHEDULE_INTERVAL_MINUTES', 30))
    
    @classmethod
    def validate(cls):
        """验证配置是否完整"""
        required_fields = [
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_GROUP_ID', 
            'SLACK_BOT_TOKEN',
            'SLACK_CHANNEL_A',
            'SLACK_CHANNEL_B'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"缺少必要的配置项: {', '.join(missing_fields)}")
        
        return True 