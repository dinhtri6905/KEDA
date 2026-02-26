# KEDA + RabbitMQ Event-Driven Autoscaling Demo

Dự án minh họa cách sử dụng **KEDA** (Kubernetes Event-driven Autoscaling) để tự động scale các consumer Python dựa trên độ dài hàng đợi RabbitMQ.

Hệ thống bao gồm:
- RabbitMQ làm message broker với 3 queue (queue1, queue2, queue3)
- 3 Deployment consumer riêng biệt, mỗi cái lắng nghe 1 queue
- KEDA ScaledObject scale số lượng pod từ 0 → 20 dựa trên queue length (mỗi pod xử lý ~20 messages)
- Giám sát qua Prometheus + Grafana
- Script gửi message từ local với tốc độ kiểm soát (round-robin vào 3 queue)

## Cấu trúc thư mục
KEDA/
├── scripts/
│   ├── consumer.py                 # Consumer Python xử lý message từ queue
│   ├── Dockerfile                  # Dockerfile build image cho consumer
│   ├── send_messages.py            # Script gửi message từ local (round-robin, điều chỉnh tốc độ)
│   ├── start-port-forward.sh       # Khởi động port-forward đến RabbitMQ
│   └── stop-port-forward.sh        # Dừng port-forward
├── yaml/
│   ├── consumer-deploy.yaml        # 3 Deployment consumer (q1, q2, q3)
│   ├── rabbitmq-deploy.yaml        # Deployment RabbitMQ (rabbitmq:3-management)
│   ├── rabbitmq-svc.yaml           # Service expose RabbitMQ (AMQP + Management + Metrics)
│   ├── rabbitmq-monitor.yaml       # ServiceMonitor cho Prometheus scrape metrics RabbitMQ
│   └── scaledobject.yaml           # 3 ScaledObject KEDA cho từng queue
├── grafana-dashboard.json          # Dashboard Grafana giám sát queue length, replicas, CPU/memory...
└── README.md                       # Hướng dẫn này


## Yêu cầu trước khi bắt đầu

- Kubernetes cluster đang hoạt động (minikube, kind, EKS, GKE, v.v.)
- `kubectl` đã cấu hình đúng context
- Helm 3 đã cài đặt
- Docker đã cài đặt (để build image consumer)
- Python 3 + pip trên máy local (để chạy send_messages.py)
- Namespace `monitoring` đã có Prometheus + Grafana 

## Các bước triển khai chi tiết

### 1. Tạo namespace
```bash
kubectl create namespace messaging
```

### 2. Cài đặt KEDA
```bash
helm repo add kedacore https://kedacore.github.io/charts
helm repo update

helm install keda kedacore/keda --namespace keda --create-namespace
```
#### Kiểm tra
```bash
kubectl get pods -n keda
```

### 3. Triển khai RabbitMQ
```bash
kubectl apply -f yaml/rabbitmq-deploy.yaml
kubectl apply -f yaml/rabbitmq-svc.yaml

# Theo dõi pod
kubectl get pods -n messaging -w
```
