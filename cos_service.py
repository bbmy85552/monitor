# cos_service.py
import os
import time
import base64
import uuid
from typing import Optional, Tuple
from qcloud_cos import CosConfig, CosS3Client
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from dotenv import load_dotenv
import tempfile

# 加载环境变量
load_dotenv()

class COSService:
    def __init__(self):
        # COS 配置
        self.secret_id = os.getenv('COS_SECRET_ID')
        self.secret_key = os.getenv('COS_SECRET_KEY')
        self.region = os.getenv('COS_REGION', 'ap-hongkong')
        self.bucket = os.getenv('COS_BUCKET')
        self.scheme = os.getenv('COS_SCHEME', 'https')
        
        # 初始化 COS 客户端
        config = CosConfig(
            Region=self.region,
            SecretId=self.secret_id,
            SecretKey=self.secret_key,
            Scheme=self.scheme
        )
        self.client = CosS3Client(config)
    
    def upload_base64_image(self, base64_data: str, file_name: str, 
                           asset_type: str, chatbot_id: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        上传 base64 图像到 COS
        
        Args:
            base64_data: base64 编码的图像数据 (格式: data:image/jpeg;base64,...)
            file_name: 原始文件名
            asset_type: 资产类型 (chatbot_icon 或 bubble_icon)
            chatbot_id: 聊天机器人ID
        
        Returns:
            Tuple[success: bool, cos_url: str, error_message: str]
        """
        try:
            # 解析 base64 数据
            if base64_data.startswith('data:'):
                # 移除 data:image/jpeg;base64, 前缀
                header, encoded = base64_data.split(',', 1)
            else:
                encoded = base64_data
            
            # 解码 base64 数据
            image_data = base64.b64decode(encoded)
            
            # 生成唯一的文件名
            timestamp = int(time.time())
            file_extension = file_name.split('.')[-1] if '.' in file_name else 'jpg'
            unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.{file_extension}"
            
            # 构建 COS 对象键 (路径)
            cos_object_key = f"chatbot_assets/{unique_filename}"
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
                temp_file.write(image_data)
                temp_file_path = temp_file.name
            
            try:
                # 上传到 COS
                response = self.client.upload_file(
                    Bucket=self.bucket,
                    LocalFilePath=temp_file_path,
                    Key=cos_object_key
                )
                
                # 构建访问 URL
                cos_url = f"https://{self.bucket}.cos.{self.region}.myqcloud.com/{cos_object_key}"
                
                return True, cos_url, None
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except TencentCloudSDKException as e:
            error_msg = f"COS上传失败: {str(e)}"
            return False, None, error_msg
        except Exception as e:
            error_msg = f"图像处理失败: {str(e)}"
            return False, None, error_msg
    
    def delete_file(self, cos_url: str) -> bool:
        """
        删除 COS 文件
        
        Args:
            cos_url: COS 文件的完整 URL
        
        Returns:
            bool: 删除是否成功
        """
        try:
            # 从 URL 中提取对象键
            if f"{self.bucket}.cos.{self.region}.myqcloud.com" in cos_url:
                object_key = cos_url.split(f"{self.bucket}.cos.{self.region}.myqcloud.com/")[1]
                
                self.client.delete_object(
                    Bucket=self.bucket,
                    Key=object_key
                )
                return True
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
            return False

# 全局 COS 服务实例
cos_service = COSService() 