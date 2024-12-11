import hashlib
import os
import time
import datetime
import ntplib
import logging
from hashlib import sha256
from time import sleep

logging.basicConfig(filename='password_check.log', level=logging.INFO, format='%(asctime)s - %(message)s')

EMERGENCY_PASSWORD = os.getenv('EMERGENCY_PASSWORD', 'emergency123')  # 默认紧急口令
SALT = os.getenv('PASSWORD_SALT', 'randomsalt')  # 默认盐值，可以更改为更安全的方式

stored_password_hash = "a18cf741a5f2ed83661c1a13ee35c34f9efdbd75e5eeed4640f7faebd33bfaad"  # 这个值需要动态计算或存储在安全地方

def hash_password(password):
    salted_password = password + SALT
    return sha256(salted_password.encode('utf-8')).hexdigest()

# 验证密码
def verify_password(input_password):
    return hash_password(input_password) == stored_password_hash

# 获取网络时间
def get_ntp_time():
    client = ntplib.NTPClient()
    try:
        response = client.request('pool.ntp.org', version=3)
        return datetime.datetime.utcfromtimestamp(response.tx_time).date()
    except Exception as e:
        logging.error(f"无法获取NTP时间: {e}")
        return datetime.datetime.utcnow().date()  # 如果NTP失败，使用本地时间

def main():
    current_date = get_ntp_time()

    max_attempts = 5
    attempts = 0

    print(f"今天是 {current_date}，请输入密码以解除限制。")

    while attempts < max_attempts:
        user_input = input(f"尝试次数 {attempts + 1}/{max_attempts}，请输入密码: ")

        if user_input == EMERGENCY_PASSWORD:
            print("[ALERT] 紧急口令已触发！立即告警！")
            logging.warning("紧急口令被触发，跳过密码验证。")
            break  # 紧急口令输入后直接跳出循环

        if verify_password(user_input):
            print("密码正确，解除限制成功！")
            logging.info("密码验证成功，解除限制。")
            break
        else:
            print("密码错误，请重新输入。")
            logging.warning(f"密码错误，第{attempts + 1}次尝试。")
            attempts += 1

        if attempts >= max_attempts:
            print("告警：密码输入错误超过最大次数，解除失败！五秒后重试")
            logging.error("密码尝试超过最大次数，解除失败！五秒后重试")
            sleep(5)  # 暂停 5 秒，防止暴力破解

# 定时每日轮询
if __name__ == "__main__":
    last_date = None

    while True:
        today = get_ntp_time()

        # 确保每天只执行一次
        if today != last_date:
            print(f"\n[INFO] {today}，开始检查密码输入...")
            main()
            last_date = today  # 更新最后执行日期

        # 等待直到第二天再执行
        time.sleep(86400)  # 86400 秒 = 1 天
