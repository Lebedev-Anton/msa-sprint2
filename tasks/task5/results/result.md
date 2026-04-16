### Task 5

## Общая цель

Настроить в кластере Kubernetes управление трафиком для микросервиса `booking-service` с использованием **Istio Service Mesh**, реализовав:

- Canary-релиз (90% → v1, 10% → v2)
- Маршрутизацию по фича-флагу (`X-Feature-Enabled: true` → v2)
- Fallback при отказе v1
- Retry и Circuit Breaking

## Описание изменений

### 1. Подготовка окружения

- Установлен Istio, сбор образов, деплой helm и тд -  `make all`

### 2. Конфигурация Istio

#### `DestinationRule`

Создан файл [`destination-rule.yaml`], определяющий:

- Подмножества (`subsets`) `v1` и `v2` по label `version`
- Политики соединений:
  - `maxConnections: 100`
  - `http1MaxPendingRequests: 100`

#### `VirtualService`

Создан файл [`virtual-service.yaml`](../istio/virtual-service.yaml), реализующий:
- **Feature-flag маршрутизацию**:
  При наличии заголовка `X-Feature-Enabled: true` → трафик направляется на `subset: v2`
- **Canary-релиз**:  
  По умолчанию — 90% трафика на `v1`, 10% на `v2`

### 3. Тестирование

Результаты:
✅ Canary release
✅ Feature Flag
✅ Fallback
✅ проверка Istio

## Итог

Все требования задания выполнены:

- ✅ Установлен и настроен Istio
- ✅ Реализованы две версии сервиса с различным поведением
- ✅ Настроены Canary, Feature Flag, Fallback, Retry и Circuit Breaking
- ✅ Все тесты проходят успешно
