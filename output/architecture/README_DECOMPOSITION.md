# Monolithic Architecture Analysis: E-Commerce App

## 1. Executive Summary
The analyzed application is a Java-based monolithic e-commerce platform built with Spring Boot. It provides core functionalities including product browsing, shopping cart management, checkout processing, and contextual advertisements/recommendations.

The architecture follows a standard Layered Pattern (Controller -> Service -> Repository/Model). However, significant coupling exists between the Cart and Order domains, primarily through shared JPA entities and direct service-to-service calls within the web layer.

## 2. Existing Architecture
### 2.1 Components
- **Controllers**: Handle HTTP requests and manage user sessions (notably for the Cart).
- **Services**: Contain business logic. `CartService` and `OrderService` are the most complex.
- **Data Access**: `CartRepository` is the sole JPA repository, indicating that Order data is currently stored as persisted Carts.
- **Infrastructure**: Configured for MySQL and potentially Redis for session management.

### 2.2 Critical Risks
- **Entity Sharing**: The `Cart` entity is used for both the active shopping session and the historical order record. This makes it difficult to evolve order processing independently of cart features.
- **Session Dependency**: Cart management is heavily reliant on `HttpSession`, which creates scaling challenges for the monolith and complicates the move to stateless microservices.
- **Product Loading**: The catalog is loaded from a static JSON file at startup into memory, which is not scalable for a production environment.

## 3. Proposed Microservices Decomposition
The strategy is to decompose by Bounded Context, isolating the high-change domains (Cart, Recommendations) from the stable ones (Product Catalog).

### 3.1 Services
1. **Product Catalog Service**: Serves product data. Ownership: ProductContext.
2. **Cart Service**: Manages temporary user selections. Uses Redis for high-performance session state. Ownership: CartContext.
3. **Order Service**: Manages the lifecycle of an order from checkout to completion. Ownership: OrderContext.
4. **Recommendation Service**: Provides product suggestions. Ownership: RecommendationContext.
5. **Ad Service**: Manages contextual advertising. Ownership: AdContext.

## 4. Migration Strategy (Strangler Fig)
We will use a phased approach, starting with the Product Catalog to reduce the load on the monolith's database and memory.

1. **Phase 1**: Extract Product Service. Redirect catalog lookups via an API Gateway.
2. **Phase 2**: Extract Recommendation and Ad Services. These are low-risk, stateless services.
3. **Phase 3**: Extract Cart Service. This involves moving session state from the monolith to a shared Redis instance.
4. **Phase 4**: Extract Order Service. This requires a database migration to separate Cart tables from Order tables.
