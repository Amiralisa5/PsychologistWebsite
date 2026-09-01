using Identity.Application.Common.Interfaces;
using Identity.Application.DTOs.Auth;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace Identity.Application.Features.Auth.Queries.GetCurrentUser;

public class GetCurrentUserQueryHandler : IRequestHandler<GetCurrentUserQuery, UserDto>
{
    private readonly IIdentityDbContext _context;

    public GetCurrentUserQueryHandler(IIdentityDbContext context)
    {
        _context = context;
    }

    public async Task<UserDto> Handle(GetCurrentUserQuery request, CancellationToken cancellationToken)
    {
        var user = await _context.Users
            .FirstOrDefaultAsync(u => u.Id == request.UserId && u.IsActive, cancellationToken);

        if (user == null)
        {
            throw new UnauthorizedAccessException("User not found");
        }

        return new UserDto
        {
            Id = user.Id,
            UserName = user.UserName,
            Email = user.Email,
            PhoneNumber = user.PhoneNumber,
            FirstName = user.FirstName,
            LastName = user.LastName,
            Gender = user.Gender,
            IsEmailConfirmed = user.IsEmailConfirmed,
            IsPhoneNumberConfirmed = user.IsPhoneNumberConfirmed,
            CreatedAt = user.CreatedAt,
            UpdatedAt = user.UpdatedAt,
            IsActive = user.IsActive
        };
    }
}

