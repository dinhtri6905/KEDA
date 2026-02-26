import pika, os, time

url = os.getenv("RABBITMQ_HOST")
queue = os.getenv("QUEUE_NAME", "queue1")

connection = pika.BlockingConnection(pika.URLParameters(url))
channel = connection.channel()
channel.queue_declare(queue=queue, durable=True)

def callback(ch, method, properties, body):
    print("Received message:", body.decode())
    time.sleep(0.01)  # xử lý chậm 1 giây / message
    ch.basic_ack(delivery_tag=method.delivery_tag)  # ACK sau khi xử lý

channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)

print("Consumer started. Waiting for messages...")
channel.start_consuming()