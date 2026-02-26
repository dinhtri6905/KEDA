#!/usr/bin/env python3
import pika
import time
import sys

# ===== CẤU HÌNH KẾT NỐI ========
RABBITMQ_HOST = "127.0.0.1"
RABBITMQ_PORT = 5673
CREDENTIALS = pika.PlainCredentials('admin', 'admin')
# ===============================

# Danh sách các queue muốn phân phối
TARGET_QUEUES = ["queue1", "queue2", "queue3"]
NUM_QUEUES = len(TARGET_QUEUES)

def main():
    # 1. Nhận tham số từ dòng lệnh
    # Mặc định: 5000 message, tốc độ 1000 msg/s
    total_messages = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    rate = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    
    interval = 1.0 / rate
    url = f"amqp://admin:admin@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
    
    print(f"--- CẤU HÌNH ---")
    print(f"• Tổng message : {total_messages}")
    print(f"• Tốc độ tổng  : {rate} msg/s")
    print(f"• Phân bổ vào  : {TARGET_QUEUES}")
    print(f"• Tốc độ/Queue : ~{int(rate/NUM_QUEUES)} msg/s mỗi queue")
    print(f"----------------")

    # 2. Kết nối RabbitMQ
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=CREDENTIALS
        ))
        channel = connection.channel()

        # Khai báo tất cả các queue để đảm bảo chúng tồn tại
        for q in TARGET_QUEUES:
            channel.queue_declare(queue=q, durable=True)

        print(f"--> BẮT ĐẦU GỬI...")
        start_time = time.time()

        # 3. Vòng lặp gửi tin nhắn
        for i in range(total_messages):
            # LOGIC CHÍNH: Chọn queue dựa trên số thứ tự (Round Robin)
            # i = 0 -> queue1, i = 1 -> queue2, i = 2 -> queue3, i = 3 -> queue1...
            queue_index = i % NUM_QUEUES
            current_queue = TARGET_QUEUES[queue_index]
            
            message_body = f"Msg {i+1} -> {current_queue}"
            
            channel.basic_publish(
                exchange='',
                routing_key=current_queue,
                body=message_body,
                properties=pika.BasicProperties(delivery_mode=2)  # Persistent
            )

            # In log mỗi khi gửi được số lượng bằng đúng tốc độ (1 giây trôi qua)
            if (i + 1) % rate == 0:
                print(f"   [Sent] Đã gửi {i + 1}/{total_messages} message...")
            
            # Delay để kiểm soát tốc độ
            time.sleep(interval)

        # 4. Tổng kết
        elapsed = time.time() - start_time
        print(f"\n-----HOÀN TẤT!-----")
        print(f"• Thời gian thực tế: {elapsed:.2f} giây")
        print(f"• Tốc độ trung bình: {total_messages/elapsed:.0f} msg/s")
        
        connection.close()

    except Exception as e:
        print(f"LỖI: {e}")
        print("Gợi ý: Kiểm tra xem đã 'kubectl port-forward' chưa?")

if __name__ == "__main__":
    main()