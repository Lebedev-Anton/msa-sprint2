import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { buildSubgraphSchema } from '@apollo/subgraph';
import gql from 'graphql-tag';

const MONOLITH_URL = process.env.MONOLITH_URL || 'http://hotelio-monolith:8080';

const typeDefs = gql`
  type Hotel @key(fields: "id") @external {
    id: ID!
  }

  type Booking @key(fields: "id") {
    id: ID!
    userId: String!
    hotelId: String!
    promoCode: String
    discountPercent: Int
    hotel: Hotel
  }

  type Query {
    bookingsByUser(userId: String!): [Booking]
  }
`;

async function fetchBookingsByUserId(userId) {
  const res = await fetch(`${MONOLITH_URL}/api/bookings?userId=${encodeURIComponent(userId)}`);
  if (!res.ok) return [];
  const data = await res.json();
  // Monolith returns an array of booking objects
  return Array.isArray(data) ? data : [];
}

const resolvers = {
  Query: {
    bookingsByUser: async (_, { userId }, { req }) => {
      // ACL: user can only see their own bookings
      const authenticatedUserId = req.headers['userid'];
      if (!authenticatedUserId || authenticatedUserId !== userId) {
        return [];
      }
      const bookings = await fetchBookingsByUserId(userId);
      return bookings;
    },
  },
  Booking: {
    hotel: (parent) => {
      // Return a reference for the hotel subgraph to resolve
      return { __typename: 'Hotel', id: parent.hotelId };
    },
  },
};

const server = new ApolloServer({
  schema: buildSubgraphSchema([{ typeDefs, resolvers }]),
});

startStandaloneServer(server, {
  listen: { port: 4001 },
  context: async ({ req }) => ({ req }),
}).then(() => {
  console.log('✅ Booking subgraph ready at http://localhost:4001/');
});
