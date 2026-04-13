import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { buildSubgraphSchema } from '@apollo/subgraph';
import gql from 'graphql-tag';

const MONOLITH_URL = process.env.MONOLITH_URL || 'http://hotelio-monolith:8080';

const typeDefs = gql`
  type Hotel @key(fields: "id") {
    id: ID!
    name: String
    city: String
    stars: Int
  }

  type Query {
    hotelsByIds(ids: [ID!]!): [Hotel]
  }
`;

async function fetchHotelById(id) {
  const res = await fetch(`${MONOLITH_URL}/api/hotels/${encodeURIComponent(id)}`);
  if (!res.ok) return null;
  const data = await res.json();
  // Map monolith fields to GraphQL schema fields
  return {
    __typename: 'Hotel',
    id: data.id,
    name: data.description || data.name,
    city: data.city,
    stars: Math.round(data.rating) || 0,
  };
}

async function fetchHotelsByIds(ids) {
  return Promise.all(ids.map((id) => fetchHotelById(id)));
}

const resolvers = {
  Hotel: {
    __resolveReference: async ({ id }) => {
      return fetchHotelById(id);
    },
  },
  Query: {
    hotelsByIds: async (_, { ids }) => {
      const hotels = await fetchHotelsByIds(ids);
      return hotels.filter(Boolean);
    },
  },
};

const server = new ApolloServer({
  schema: buildSubgraphSchema([{ typeDefs, resolvers }]),
});

startStandaloneServer(server, {
  listen: { port: 4002 },
  context: async ({ req }) => ({ req }),
}).then(() => {
  console.log('✅ Hotel subgraph ready at http://localhost:4002/');
});
