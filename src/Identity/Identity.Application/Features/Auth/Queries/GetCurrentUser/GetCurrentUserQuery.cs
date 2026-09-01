using Identity.Application.DTOs.Auth;
using MediatR;

namespace Identity.Application.Features.Auth.Queries.GetCurrentUser;

public class GetCurrentUserQuery : IRequest<UserDto>
{
    public Guid UserId { get; set; }
}

