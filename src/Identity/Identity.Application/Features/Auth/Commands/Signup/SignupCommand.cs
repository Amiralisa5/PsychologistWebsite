using Identity.Application.DTOs.Auth;
using Identity.Domain.Entities;
using MediatR;

namespace Identity.Application.Features.Auth.Commands.Signup;

public class SignupCommand : IRequest<LoginResponse>
{
    public string UserName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string PhoneNumber { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public Gender Gender { get; set; }
}
