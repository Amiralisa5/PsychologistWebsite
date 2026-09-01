using MediatR;

namespace Identity.Application.Features.Auth.Commands.ForgetPassword;

public class ForgetPasswordCommand : IRequest<Unit>
{
    public string UserName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string PhoneNumber { get; set; } = string.Empty;
    
}

