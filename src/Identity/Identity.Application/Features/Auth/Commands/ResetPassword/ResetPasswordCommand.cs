using MediatR;

namespace Identity.Application.Features.Auth.Commands.ResetPassword;

public class ResetPasswordCommand : IRequest<Unit>
{
    public string Token { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string PhoneNumber { get; set; } = string.Empty;
    public string UserName { get; set; } = string.Empty;
    public string NewPassword { get; set; } = string.Empty;
}

