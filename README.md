# Clean Identity Template (.NET 8, Clean Architecture)

This repository provides a ready-to-use **Clean Architecture** template with a dedicated **Identity/Auth bounded context**.

It is designed to be cloned or used as a base template for new backend services where you want:
- A clean separation of layers (Domain, Application, Infrastructure, Api)
- A dedicated Identity context for user registration and authentication
- EF Core + SQL Server integration
- Serilog logging
- MediatR-based use case handling

---

 ##🏗 Solution structure
 
         `src/
         └─ Identity/
         ├─ Identity.Domain          → Domain entities (pure, framework-free)
         ├─ Identity.Application     → Use-cases, commands, abstractions
         ├─ Identity.Infrastructure  → EF Core, repositories, hashing, DI wiring
         └─ Identity.Api             → ASP.NET Core Web API (JWT-ready)`


  
## Features

  - `Identity.Domain` – pure domain entities (no EF / no framework dependencies)
  - `Identity.Application` – use cases, commands, handlers, abstractions (interfaces)
  - `Identity.Infrastructure` – EF Core DbContext, repositories, password hashing, DI
  - `Identity.Api` – ASP.NET Core Web API (JWT-ready, Serilog, Swagger)
  - `POST /api/Auth/register`  
    Registers a new user using:
    - Email uniqueness check
    - Password hashing (ASP.NET Identity PasswordHasher)
    - EF Core persistence

---

## ⚙ Technology Stack

- .NET 8 (or later)
- ASP.NET Core Web API
- Entity Framework Core (SQL Server)
- MediatR
- Microsoft.AspNetCore.Identity (Password Hashing)
- Serilog
- Swagger (OpenAPI)

---

### Prerequisites

- .NET SDK 8 or later
- SQL Server instance (local or remote)

## 🚀 Getting Started

1. Clone the repository:

   ```bash
  		 git clone https://github.com/Amiralisa5/clean-identity-template.git
   
2.	Update the connection string in:
      ```bash
   		src/Identity/Identity.Api/appsettings.json
   Example:
   
   `"ConnectionStrings":{"IdentityDb":"Server=.;Database=IdentityDb;Trusted_Connection=True;TrustServerCertificate=True;"`

3.	Build the solution:
     ```bash
 				dotnet build
			  dotnet run --project src/Identity/Identity.Api/Identity.Api.csproj
				
4.	Run the Identity API:
      ```bash
      dotnet run --project src/Identity/Identity.Api/Identity.Api.csproj
      dotnet run --project src/Identity/Identity.Api/Identity.Api.csproj
					
5.	Open Swagger UI:  
		•	Go to: 
		
			https://localhost:5001/swagger or http://localhost:5000/swagger 
      (depending on your launch settings)
		
6.	Test registration endpoint:
	  📩	POST /api/Auth/register

		{
		"userName": "testuser",
		"email": "test@example.com",
		"password": "P@ssw0rd123",
		"firstName": "Test",
		"lastName": "User"
		}

