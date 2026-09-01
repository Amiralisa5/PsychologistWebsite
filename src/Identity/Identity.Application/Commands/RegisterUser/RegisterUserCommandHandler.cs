using Identity.Application.Abstractions;
using Identity.Application.DTOs;
using Identity.Domain.Entities;
using Identity.Domain.ValueObjects;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace Identity.Application.Commands.RegisterUser;

public class RegisterUserCommandHandler : IRequestHandler<RegisterUserCommand, AuthResponseDto>
{
    private readonly IIdentityDbContext _context;
    private readonly IPasswordHasher _passwordHasher;
    private readonly IJwtTokenGenerator _jwtTokenGenerator;

    public RegisterUserCommandHandler(
        IIdentityDbContext context,
        IPasswordHasher passwordHasher,
        IJwtTokenGenerator jwtTokenGenerator)
    {
        _context = context;
        _passwordHasher = passwordHasher;
        _jwtTokenGenerator = jwtTokenGenerator;
    }

    public async Task<AuthResponseDto> Handle(RegisterUserCommand request, CancellationToken cancellationToken)
    {
        // Check if email already exists
        var emailExists = await _context.Users
            .AnyAsync(u => u.Email.Value == request.Email.ToLowerInvariant(), cancellationToken);

        if (emailExists)
        {
            throw new InvalidOperationException("Email already exists");
        }
        var phoneNumberExists = await _context.Users
            .AnyAsync(u => u.PhoneNumber == request.PhoneNumber, cancellationToken);

        if (phoneNumberExists)
        {
            throw new InvalidOperationException("Phone number already exists");
        }

        // Check if username already exists
        var userNameExists = await _context.Users
            .AnyAsync(u => u.UserName == request.UserName, cancellationToken);

        if (userNameExists)
        {
            throw new InvalidOperationException("Username already exists");
        }

        // Create user
        var email = Email.Create(request.Email);
        var phoneNumber = PhoneNumber.Create(request.PhoneNumber);
        var passwordHash = _passwordHasher.HashPassword(request.Password);

        var user = new User
        {
            UserName = request.UserName,
            Email = email,
            PhoneNumber = phoneNumber,
            PasswordHash = passwordHash,
            FirstName = request.FirstName,
            LastName = request.LastName,
            IsActive = true
        };

        _context.Users.Add(user);
        await _context.SaveChangesAsync(cancellationToken);

        // Generate token
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

