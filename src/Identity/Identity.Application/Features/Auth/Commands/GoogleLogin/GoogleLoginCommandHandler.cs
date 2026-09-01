using Identity.Application.Common.Interfaces;
using Identity.Application.DTOs.Auth;
using Identity.Domain.Entities;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace Identity.Application.Features.Auth.Commands.GoogleLogin;

public class GoogleLoginCommandHandler : IRequestHandler<GoogleLoginCommand, LoginResponse>
{
    private readonly IIdentityDbContext _context;
    private readonly IJwtTokenGenerator _jwtTokenGenerator;

    public GoogleLoginCommandHandler(
        IIdentityDbContext context,
        IJwtTokenGenerator jwtTokenGenerator)
    {
        _context = context;
        _jwtTokenGenerator = jwtTokenGenerator;
    }

    public async Task<LoginResponse> Handle(GoogleLoginCommand request, CancellationToken cancellationToken)
    {
        // Check if user exists by email
        var user = await _context.Users
            .FirstOrDefaultAsync(u => u.Email == request.Email, cancellationToken);

        if (user == null)
        {
            // Create new user from Google account
            user = new User
            {
                Id = Guid.NewGuid(),
                UserName = request.Email.Split('@')[0] + "_" + Guid.NewGuid().ToString("N")[..8],
                Email = request.Email,
                PasswordHash = string.Empty, // No password for Google users
                FirstName = request.FirstName,
                LastName = request.LastName,
                IsEmailConfirmed = true, // Google emails are already verified
                CreatedAt = DateTime.UtcNow,
                IsActive = true
            };

            _context.Users.Add(user);
            await _context.SaveChangesAsync(cancellationToken);
        }
        else if (!user.IsActive)
        {
            throw new UnauthorizedAccessException("User account is inactive");
        }

        // Generate tokens
        var accessToken = _jwtTokenGenerator.GenerateToken(user);
        var refreshToken = _jwtTokenGenerator.GenerateRefreshToken();

        // Save refresh token
        var refreshTokenEntity = new RefreshToken
        {
            Id = Guid.NewGuid(),
            UserId = user.Id,
            Token = refreshToken,
            ExpiresAt = DateTime.UtcNow.AddDays(7),
            CreatedAt = DateTime.UtcNow,
            IsRevoked = false
        };

        _context.RefreshTokens.Add(refreshTokenEntity);
        await _context.SaveChangesAsync(cancellationToken);

        return new LoginResponse
        {
            AccessToken = accessToken,
            RefreshToken = refreshToken,
            ExpiresAt = DateTime.UtcNow.AddHours(1),
            User = new UserDto
            {
                Id = user.Id,
                UserName = user.UserName,
                Email = user.Email,
                FirstName = user.FirstName,
                LastName = user.LastName
            }
        };
    }
}

