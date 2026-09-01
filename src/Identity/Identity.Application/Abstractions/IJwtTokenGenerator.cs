using Identity.Domain.Entities;

namespace Identity.Application.Abstractions;

public interface IJwtTokenGenerator
{
    string GenerateToken(User user);
}

