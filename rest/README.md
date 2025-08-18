# REST API Testing

This directory contains HTTP files for testing the Graph API endpoints.

## Files

- `entity.http` - Tests for entity endpoints (create, read, update, delete)
- `relationships.http` - Tests for relationship endpoints
- `http-client.env.json` - Environment variables for sharing values between requests

## Usage

1. Make sure the Graph API server is running on `http://localhost:8000`
2. Use an HTTP client that supports these files (like VS Code with the REST Client extension)
3. Run requests in order, as later requests depend on values from earlier ones

## Sharing Values Between Files

The `http-client.env.json` file allows sharing values between different HTTP files. When you create an entity in `entity.http`, you can manually copy its ID to the environment file to use in `relationships.http`.

Example workflow:
1. Run the "Create a new entity" request in `entity.http`
2. Copy the returned entity ID
3. Update `http-client.env.json` with the entity ID
4. Use the entity ID in `relationships.http` to create relationships

## Environment Variables

- `baseUrl` - The base URL of the API server
- `sourceEntityId` - ID of a source entity for relationship creation
- `targetEntityId` - ID of a target entity for relationship creation
- `relationshipId` - ID of a relationship for relationship operations
