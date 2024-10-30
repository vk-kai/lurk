import os
import json
import time
import random
import string
from cryptography.fernet import Fernet

class KeyManager:
    def __init__(self,num_keys, expiry, reusable):
        self.KEY_INFO_FILE="key_info.json"
        self.key_info = self.load_key_info()
        self.real_key=self.create_keys(num_keys, expiry, reusable)
    def load_key_info(self):
        """加载密钥信息从 JSON 文件."""
        if os.path.exists(self.KEY_INFO_FILE):
            with open(self.KEY_INFO_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_key_info(self):
        """将密钥信息保存到 JSON 文件."""
        with open(self.KEY_INFO_FILE, "w") as f:
            json.dump(self.key_info, f, indent=4)

    def get_key_record(self, virtual_key):
        """根据虚拟密钥获取完整密钥记录."""
        for key_name, key_record in self.key_info.items():
            if key_record['virtual_key'] == virtual_key:
                return key_record, key_name
        return None, None  # 如果没有找到，则返回 None

    def validate_and_use_key(self, virtual_key):
        """校验密钥并返回真实密钥，如果可用则减掉相关字段."""
        key_record, key_name = self.get_key_record(virtual_key)
        if key_record is None:
            print('密钥不存在')
            return False
        # 检查密钥是否过期
        if key_record['expiry'] < time.time() and key_record['expiry'] != 'vip':
            print('密钥已过期')
            return False

        # 检查密钥是否可用
        if key_record['reusable'] <= 0:  # 假设 '0' 表示不可用
            print('密钥已经使用')
            return False

        # 如果可用，则减少使用次数
        key_record['reusable'] -= 1

        # 更新并保存密钥信息
        self.key_info[key_name] = key_record
        self.save_key_info()

        return key_record['real_key']

    @staticmethod
    def generate_key():
        """生成新的密钥并返回密钥."""
        return Fernet.generate_key()
    @staticmethod
    def generate_virtual_key(length=32, existing_keys=None):
        """生成一个指定长度的随机虚拟密钥."""
        characters = string.ascii_letters + string.digits  # 包含字母和数字
        while True:
            virtual_key = ''.join(random.choice(characters) for _ in range(length))
            if existing_keys is None or virtual_key not in existing_keys:
                return virtual_key

    def create_keys(self, num_keys, expiry, reusable):
        """创建指定数量的密钥，支持过期时间和使用次数."""
        existing_virtual_keys = {key['virtual_key'] for key in self.key_info.values()}  # 获取已存在的虚拟密钥
        real_key=''
        for i in range(num_keys):
            # 定义到期时间
            if expiry.lower() == "vip":
                expiry_time = "vip"  # VIP 密钥没有过期时间
            else:
                expiry_time = int(time.time()) + (int(expiry) * 86400)  # 将天数转换为秒

            # 生成唯一的虚拟密钥
            virtual_key = self.generate_virtual_key(existing_keys=existing_virtual_keys)

            # 生成真实密钥
            real_key = self.generate_key()

            # 记录密钥信息
            key_record = {
                "real_key": real_key.decode(),  # 真实密钥
                "virtual_key": virtual_key,  # 随机生成虚拟密钥
                "generated_at": int(time.time()),
                "expiry": expiry_time,
                "reusable": int(reusable),
                "create_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                "expiry_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expiry_time))
            }
            print(f"密钥：{key_record['real_key']}")
            print(f"虚拟密钥：{key_record['virtual_key']}")
            print(f"生成时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(key_record['generated_at']))}")
            print(f"过期时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(key_record['expiry']))}")
            print(f"可以使用次数：{reusable}")
            self.key_info[f"key_{len(self.key_info) + 1}"] = key_record

        # 保存密钥信息到 JSON 文件
        self.save_key_info()
        print(f"已生成 {num_keys} 个密钥，并保存到 {self.KEY_INFO_FILE} 文件中。")
        return real_key
# 示例用法
if __name__ == "__main__":
    key_manager = KeyManager()
    key_manager.create_keys(num_keys=5, expiry='30', reusable=True)
