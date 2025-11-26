# Flask + MongoDB Deployment on Kubernetes using Minikube

This project demonstrates deploying a containerized Flask REST API with MongoDB using Docker and Kubernetes on a Minikube cluster.  
The Flask API exposes a `/data` endpoint that supports POST (insert document) and GET (retrieve all documents) operations.

## Author
Raj Vardhan

---

## Project Overview

The system consists of:
- Flask Application (REST API)
- MongoDB Database
- Docker for containerization
- Kubernetes for orchestration

The Flask application interacts with MongoDB inside the cluster, and both are exposed appropriately through Kubernetes Services.

---

## Architecture

Client → Flask Service → Flask Deployment → Flask Pod  
Flask Pod → MongoDB Service → MongoDB Deployment → MongoDB Pod

---

## Dockerfile (Flask Application)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Build Docker image:
```bash
docker build -t flask-mongo-app .
```

(Optional) Push image to Docker Hub:
```bash
docker tag flask-mongo-app <dockerhub-username>/flask-mongo-app:v1
docker push <dockerhub-username>/flask-mongo-app:v1
```

---

## Kubernetes YAML Files

### mongo-deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongo-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongo
  template:
    metadata:
      labels:
        app: mongo
    spec:
      containers:
      - name: mongo
        image: mongo
        ports:
        - containerPort: 27017
```

### mongo-service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mongo-service
spec:
  selector:
    app: mongo
  ports:
  - protocol: TCP
    port: 27017
    targetPort: 27017
```

### flask-deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flask
  template:
    metadata:
      labels:
        app: flask
    spec:
      containers:
      - name: flask
        image: flask-mongo-app
        env:
        - name: MONGO_HOST
          value: "mongo-service"
        ports:
        - containerPort: 5000
```

### flask-service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: flask-service
spec:
  type: NodePort
  selector:
    app: flask
  ports:
  - port: 5000
    targetPort: 5000
    nodePort: 30001
```

---

## Deploying on Minikube

Start Kubernetes:
```bash
minikube start --driver=docker
```

Load Docker image into Minikube:
```bash
minikube image load flask-mongo-app
```

Apply all Kubernetes manifests:
```bash
kubectl apply -f k8s/
```

Verify resources:
```bash
kubectl get pods
kubectl get svc
```

Access the Flask API:
```bash
minikube service flask-service
```

---

## Testing API

Insert data:
```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"name":"test"}' http://<NODE-IP>:<NODEPORT>/data
```

Retrieve data:
```bash
curl http://<NODE-IP>:<NODEPORT>/data
```

---

## DNS Resolution in Kubernetes

Kubernetes provides automatic DNS-based service discovery using CoreDNS.
Pods can communicate using service names instead of IP addresses.

Example:
```
Flask pod connects to MongoDB at:
mongodb://mongo-service:27017/
```

Even if the MongoDB pod restarts and receives a new IP, the Flask application still connects successfully because the DNS alias remains constant.

---

## Resource Requests and Limits

Kubernetes allows defining guaranteed and maximum resource allocation per container.

Example:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

Requests ensure minimum guaranteed resources.  
Limits define the maximum allowed usage to avoid overconsumption.

---

## Design Choices

| Component | Reason |
|----------|--------|
| NodePort Service | Enables external access without LoadBalancer setup |
| Separate Services for Flask & MongoDB | Decoupling provides independent scaling |
| Minikube | Best for local Kubernetes testing |
| MongoDB as Deployment | Sufficient for a single instance demo |

Alternatives considered but not used:
- StatefulSet for MongoDB (avoided for simplicity in single-pod setup)
- LoadBalancer service (not available by default on Minikube)

---

## Testing Scenarios (Autoscaling and Database Interaction)

### Autoscaling Test
```bash
kubectl autoscale deployment flask-deployment --cpu-percent=50 --min=1 --max=5
```

Simulated Heavy Load:
```bash
for i in {1..2000}; do curl http://<NODE-IP>:<NODEPORT>/data; done
```

Observed Results:
- Horizontal Pod Autoscaler gradually increased Flask replicas.
- MongoDB handled inserts and reads correctly.
- No downtime was experienced during scaling.

---

## Conclusion

The project successfully demonstrates deploying a micro-service (Flask API) with a database (MongoDB) on Kubernetes using Docker containers, Kubernetes networking, Minikube, DNS-based service discovery, and resource management.
