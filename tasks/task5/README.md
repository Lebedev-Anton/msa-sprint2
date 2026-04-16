# Task 5: Настройка маршрутизации трафика с Istio

## Цель задания
Настроить Istio Service Mesh для управления трафиком микросервиса booking-service с использованием:
- Canary release (90% v1, 10% v2)
- Фича-флагов через HTTP заголовки
- Fallback маршрутизации при сбоях
- Circuit Breaker и Retry политик

## Архитектура решения

### Компоненты
1. **booking-service-v1**: Стабильная версия сервиса (2 реплики)
2. **booking-service-v2**: Новая версия с фича-флагами (1 реплика)
3. **Istio Service Mesh**: Управление трафиком через sidecar-прокси (Envoy)
4. **Helm чарт**: Развертывание всей инфраструктуры

### Istio ресурсы
- **VirtualService**: Маршрутизация трафика (canary, фича-флаги)
- **DestinationRule**: Определение подмножеств, Circuit Breaker, Retry политики
- **Service**: Единая точка входа для обеих версий

## Конфигурация маршрутизации

### Canary Release
- 90% трафика → v1 (стабильная версия)
- 10% трафика → v2 (новая версия)

### Фича-флаги
- Заголовок `X-Feature-Enabled: true` → 100% трафика на v2
- Без заголовка → стандартное canary распределение

### Fallback
- При недоступности v1 → автоматический переход на v2
- Circuit Breaker: после 5 последовательных ошибок → временное исключение из пула

## Развертывание

### Предварительные требования
- Minikube
- kubectl
- Helm
- Istioctl
- Docker

### Шаги развертывания

1. **Сборка Docker образов**:
   ```bash
   make build
   ```

2. **Установка Istio**:
   ```bash
   make install-istio
   ```

3. **Развертывание сервиса**:
   ```bash
   make deploy
   ```

4. **Проброс портов для локального тестирования**:
   ```bash
   make port-forward
   ```

### Проверка работы

1. **Проверка Istio**:
   ```bash
   make check-istio
   ```

2. **Тестирование Canary release**:
   ```bash
   make check-canary
   ```

3. **Тестирование фича-флагов**:
   ```bash
   make check-feature-flag
   ```

4. **Тестирование fallback и Circuit Breaker**:
   ```bash
   make check-fallback
   ```

5. **Полный тест**:
   ```bash
   make test-all
   ```

## Тестирование вручную

### Canary распределение
```bash
for i in {1..20}; do curl -s http://localhost:9090/ping; echo; done
```

### Фича-флаги
```bash
# Запрос с фича-флагом (должен попасть на v2)
curl -H "X-Feature-Enabled: true" http://localhost:9090/ping

# Проверка feature-эндпоинта (только в v2)
curl -H "X-Feature-Enabled: true" http://localhost:9090/feature
```

### Fallback тестирование
```bash
# Погасить v1
kubectl scale deployment booking-service-v1 --replicas=0

# Подождать 30 секунд
sleep 30

# Проверить, что трафик идет на v2
for i in {1..10}; do curl -s http://localhost:9090/ping; echo; done

# Восстановить v1
kubectl scale deployment booking-service-v1 --replicas=2
```

## Очистка
```bash
make clean
```

## Структура файлов
```
task5/
├── booking-service/          # Исходный код v1
│   ├── main.go
│   └── Dockerfile
├── booking-service/v2/       # Исходный код v2
│   ├── main.go
│   └── Dockerfile
├── helm/booking-service/     # Helm чарт
│   ├── templates/
│   │   ├── deployment-v1.yaml
│   │   ├── deployment-v2.yaml
│   │   ├── service.yaml
│   │   ├── virtualservice.yaml
│   │   └── destinationrule.yaml
│   ├── Chart.yaml
│   └── values.yaml
├── check-istio.sh           # Проверка Istio
├── check-canary.sh          # Проверка canary
├── check-fallback.sh        # Проверка fallback
├── check-feature-flag.sh    # Проверка фича-флагов
├── Makefile                 # Автоматизация
└── README.md               # Документация
```

## Примечания
- Для работы скриптов проверки должен быть запущен `make port-forward`
- Istio автоматически инжектит sidecar-прокси в поды default namespace
- Circuit Breaker настроен на 5 последовательных ошибок с временем изоляции 30 секунд
- Retry политика: 3 попытки с таймаутом 2 секунды на каждую