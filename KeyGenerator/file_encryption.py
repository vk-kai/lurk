import os
from cryptography.fernet import Fernet
from key_generator import KeyManager
from typing import Optional

FILE_KEYS_FILE = "file_keys.json"  # 保存文件与密钥的关联信息


def encrypt_file(file_path: str, key: bytes) -> None:
    """加密指定文件并保存加密后的文件."""
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # 使用真实密钥进行加密
    encrypted_data = Fernet(key).encrypt(file_data)

    # 保存加密后的文件，覆盖原文件
    with open(file_path + '_encrypted', 'wb') as f:
        f.write(encrypted_data)

    print(f"文件 {file_path} 已加密。")


def decrypt_file(file_path: str, virtual_key: str, key_manager: KeyManager) -> Optional[bytes]:
    """解密指定的加密文件."""
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()

    real_key = key_manager.validate_and_use_key(virtual_key)
    if real_key:
        fernet = Fernet(real_key)
        try:
            decrypted_data = fernet.decrypt(encrypted_data)
            return decrypted_data  # 返回解密后的数据
        except Exception:
            raise ValueError("解密失败，钥均无效。")
    else:
        return None


def get_user_input() -> tuple[str, int, str, str]:
    """获取用户输入以创建密钥."""
    # 选择要加密的文件
    while True:
        file_path = input("请输入要加密的文件路径: ")
        if not os.path.exists(file_path):
            print("文件不存在，请检查路径。")
            continue
        else:
            break
    num_keys = int(input("请输入要生成的密钥数量: "))
    expiry = input("请输入密钥的过期时间（天数，输入 'vip' 为永久有效）: ")
    reusable = input("请输入密钥可以重复使用的次数（输入 'always' 为无限次，输入 '无' 表示作废）: ")
    return file_path, num_keys, expiry, reusable


if __name__ == "__main__":
    file_path, num_keys, expiry, reusable = get_user_input()
    key_manager = KeyManager(num_keys, expiry, reusable)
    real_key = key_manager.real_key
    # 加密文件
    encrypt_file(file_path, real_key)  # 使用真实密钥加密文件
    # 输入密钥并解密文件
    selected_key = input("请输入用于解密的密钥（输入 '结束' 以结束输入）: ")
    if selected_key.lower() == '结束':
        exit()
    # 解密文件并将结果存储在 data 变量中
    try:
        data = decrypt_file(file_path + '_encrypted', selected_key, key_manager)
        if data:
            print("解密后的数据内容:")
            print(data.decode('utf-8', errors='ignore'))  # 尝试以 UTF-8 解码并处理可能的错误
    except ValueError as e:
        print(e)
