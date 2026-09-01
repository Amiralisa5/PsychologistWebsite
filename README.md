# Clean Identity Template (.NET 8, Clean Architecture)

This repository provides a ready-to-use Clean Architecture template with a dedicated Identity/Auth bounded context.

It is designed to be cloned or used as a base template for new backend services where you want:

A clean separation of layers (Domain, Application, Infrastructure, Api)
A dedicated Identity context for user registration and authentication
EF Core + SQL Server integration
Serilog logging
MediatR-based use case handling

---

##🏗 Solution structure

     `src/
     └─ Identity/
     ├─ Identity.Domain          → Domain entities (pure, framework-free)
     ├─ Identity.Application     → Use-cases, commands, abstractions
     ├─ Identity.Infrastructure  → EF Core, repositories, hashing, DI wiring
     └─ Identity.Api             → ASP.NET Core Web API (JWT-ready)`

---

Features

Identity.Domain – pure domain entities (no EF / no framework dependencies)
Identity.Application – use cases, commands, handlers, abstractions (interfaces)
Identity.Infrastructure – EF Core DbContext, repositories, password hashing, DI
Identity.Api – ASP.NET Core Web API (JWT-ready, Serilog, Swagger)
POST /api/Auth/register
Registers a new user using:
Email uniqueness check
Password hashing (ASP.NET Identity PasswordHasher)
EF Core persistence

---

⚙ Technology Stack.
- .NET SDK 8.0 (or higher)
- SQL Server (Local or Remote)

---

🚀 Getting Started

Clone the repository:

 	 git clone https://github.com/Amiralisa5/clean-identity-template.git
Update the connection string in:

  src/Identity/Identity.Api/appsettings.json
Example:

"ConnectionStrings":{"IdentityDb":"Server=.;Database=IdentityDb;Trusted_Connection=True;TrustServerCertificate=True;"

Build the solution:

   		dotnet build
   	  dotnet run --project src/Identity/Identity.Api/Identity.Api.csproj
   		
Run the Identity API:

dotnet run --project src/Identity/Identity.Api/Identity.Api.csproj
dotnet run --project src/Identity/Identity.Api/Identity.Api.csproj
  			
Open Swagger UI:
• Go to:

	https://localhost:5001/swagger or http://localhost:5000/swagger 
   (depending on your launch settings)

Test registration endpoint: 📩 POST /api/Auth/register

	{
		"userName": "testuser",
		"email": "test@example.com",
		"phoneNumber" : "09121111111",
		"password": "P@ssw0rd123",
		"firstName": "Test",
		"lastName": "User",
		"Gender": "Test"
	}

---

## 📄 License

Apache License 2.0
