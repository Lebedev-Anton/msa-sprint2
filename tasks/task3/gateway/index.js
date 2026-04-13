import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { ApolloGateway, RemoteGraphQLDataSource } from '@apollo/gateway';

class AuthDataSource extends RemoteGraphQLDataSource {
  willSendRequest({ request, context }) {
    // Forward the userid header from the original request to subgraphs
    if (context.req && context.req.headers) {
      const userId = context.req.headers['userid'];
      if (userId) {
        request.http.headers.set('userid', userId);
      }
    }
  }
}

const gateway = new ApolloGateway({
  serviceList: [
    { name: 'booking', url: 'http://booking-subgraph:4001' },
    { name: 'hotel', url: 'http://hotel-subgraph:4002' }
  ],
  buildService({ name, url }) {
    return new AuthDataSource({ url });
  },
});

const server = new ApolloServer({ gateway, subscriptions: false });

startStandaloneServer(server, {
  listen: { port: 4000 },
  context: async ({ req }) => ({ req }), // headers are available in context
}).then(({ url }) => {
  console.log(`🚀 Gateway ready at ${url}`);
});
