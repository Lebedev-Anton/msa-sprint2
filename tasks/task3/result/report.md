# Проделанные операции

1. booking-subgraph — заменена заглушка на реальный fetch к монолиту (GET /api/bookings?userId=). Добавлен ACL: резолвер bookingsByUser проверяет req.headers['userid'] === userId, иначе возвращает []. Резолвер Booking.hotel формирует federation-ссылку { __typename: 'Hotel', id: parent.hotelId }.
2. hotel-subgraph — реализован __resolveReference и hotelsByIds с реальным вызовом GET /api/hotels/{id} к монолиту. Добавлен маппинг полей: description → name, rating → stars.
3. gateway — заменил стандартный RemoteGraphQLDataSource на кастомный AuthDataSource, который в willSendRequest проксирует заголовок userid из оригинального запроса в subgraph-сервисы.
4. docker-compose.yml — добавил MONOLITH_URL env var обоим subgraph-сервисам.
