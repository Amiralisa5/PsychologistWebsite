using Identity.Application.Abstractions;
using Identity.Application.DTOs;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace Identity.Application.Commands.Login;

public class LoginCommandHandler : IRequestHandler<LoginCommand, AuthResponseDto>
{
    private readonly IIdentityDbContext _context;
    private readonly IPasswordHasher _passwordHasher;
    private readonly IJwtTokenGenerator _jwtTokenGenerator;

    public LoginCommandHandler(
        IIdentityDbContext context,
        IPasswordHasher passwordHasher,
        IJwtTokenGenerator jwtTokenGenerator)
    {
        _context = context;
        _passwordHasher = passwordHasher;
        _jwtTokenGenerator = jwtTokenGenerator;
    }

    public async Task<AuthResponseDto> Handle(LoginCommand request, CancellationToken cancellationToken)
    {
        var user = await _context.Users
            .FirstOrDefaultAsync(u => u.Email.Value == request.Email.ToLowerInvariant(), cancellationToken);

        if (user == null || !user.IsActive)
        {
            throw new UnauthorizedAccessException("Invalid email or password");
        }
        if (user.PhoneNumber.Value == request.PhoneNumber)
        {
            throw new UnauthorizedAccessException("Invalid phone number or password");
        }
        if (user.UserName == request.UserName)
        {
            throw new UnauthorizedAccessException("Invalid username or password");
        }
        if (!_passwordHasher.VerifyPassword(user.PasswordHash, request.Password))
        {
            throw new UnauthorizedAccessException("Invalid email or password");
        }

        var token = _jwtTokenGenerator.GenerateToken(user);

        return new AuthResponseDto(
            Token: token,
            UserName: user.UserName,
            Email: user.Email.Value,
            PhoneNumber: user.PhoneNumber.Value,
            FirstName: user.FirstName,
            LastName: user.LastName
        );
    }
}

