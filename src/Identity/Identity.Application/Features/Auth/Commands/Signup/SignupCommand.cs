using Identity.Application.DTOs.Auth;
using MediatR;

namespace Identity.Application.Features.Auth.Commands.Signup;

public class SignupCommand : IRequest<SignupResponse>
{
    public string UserName { get; set; };
    public string Email { get; set; };
    public string PhoneNumber { get; set; } ;
    public string Password { get; set; };
    public string FirstName { get; set; };
    public string LastName { get; set; };
    public Gender Gender { get; set; };
}

