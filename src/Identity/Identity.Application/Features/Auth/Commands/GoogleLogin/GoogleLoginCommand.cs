using Identity.Application.DTOs.Auth;
using MediatR;

namespace Identity.Application.Features.Auth.Commands.GoogleLogin;

public class GoogleLoginCommand : IRequest<LoginResponse>
{
    public string Email { get; set; } = string.Empty;
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string GoogleId { get; set; } = string.Empty;
}

