.PHONY: all build-v1 build-v2 istio-install istio-inject deploy-helm deploy-istio deploy port-forward check-istio check-canary check-fallback check-feature-flag teardown

## Сборка образов внутри Minikube
build-v1:
	eval $$(minikube docker-env) && \
	docker build -t booking-service:v1 ./booking-service

build-v2:
	eval $$(minikube docker-env) && \
	docker build -t booking-service:v2 ./booking-service

all: build-v1 build-v2 deploy

## Установка Istio
istio-install:
	istioctl install --set profile=demo -y

## Включение инъекции sidecar в default namespace
istio-inject:
	kubectl label namespace default istio-injection=enabled --overwrite

## Деплой через Helm с values-v1.yaml и values-v2.yaml
deploy-helm:
	helm upgrade --install booking-service-v1 ./helm/booking-service \
		-f results/values-v1.yaml
	helm upgrade --install booking-service-v2 ./helm/booking-service \
		-f results/values-v2.yaml
	kubectl rollout status deployment/booking-service-v1
	kubectl rollout status deployment/booking-service-v2

## Деплой Istio ресурсов
deploy-istio:
	kubectl apply -f results/gateway.yaml
	kubectl apply -f results/destination-rule.yaml
	kubectl apply -f results/virtual-service.yaml
	kubectl apply -f results/envoy-filter.yaml

## Полный деплой
deploy: istio-inject deploy-helm deploy-istio

## Port-forward для тестирования через localhost:9090
port-forward:
	kubectl port-forward svc/istio-ingressgateway -n istio-system 9090:80 &

## Проверки
check-istio:
	bash check-istio.sh

check-canary:
	bash check-canary.sh

check-fallback:
	bash check-fallback.sh

check-feature-flag:
	bash check-feature-flag.sh

## Удаление всего
teardown:
	helm uninstall booking-service-v1 --ignore-not-found 2>/dev/null || true
	helm uninstall booking-service-v2 --ignore-not-found 2>/dev/null || true
	kubectl delete -f istio/ --ignore-not-found
