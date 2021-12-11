"""
Worker thread of OAL Management System
"""
import time
import os
from dotenv import load_dotenv

load_dotenv()

from models import Setting

UPDATE_INTERVAL = int(os.environ.get("WORKER_UPDATE_INTERVAL_SECONDS", 30))

def main():
    """Main thread of program"""

    try:
        
        next_update = time.time()

        if(Setting.get('is_setup', False, bool)):
            print("The system is not setup yet.")
            time.sleep(2) # hold for supervisor to changed into running state
            exit(0)

        while True:
            if(time.time() < next_update):
                time.sleep(1)
                continue

            try:
                
                pass

                # ดึง EC2 ทั้งหมดที่มี Tag ของเรา
                # ดึง Latest Version และ Current Version จาก Setting
                # ถ้า Version ล่าสุด กับปัจจุบันไม่ตรงกัน ให้เริม่ Progress Update EC2
                
                ## Progress Update EC2
                    # สร้าง AMI Image จาก EC2 -> User Data
                    # ใช้ AMI สร้าง EC2 ชุดใหม่ เท่าจำนวนเดิม พร้อม Tag ใหม่ + เพิ่มเข้า Target Group
                    # Terminate EC2 ชุดเก่าออกหมด

                # ตรวจสอบ EC2 ว่ามีจำนวนเท่าไหร่
                # ถ้าเกิน ลบอันเก่าสุดออก
                # ถ้าขาด สร้างเพิ่ม

            except:
                time.sleep(5)

            next_update = time.time() + UPDATE_INTERVAL

    except Exception as e:
        print("Error: ", e)
        time.sleep(5)
        
if __name__ == "__main__":
    main()
