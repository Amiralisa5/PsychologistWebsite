using Identity.Application.DTOs;
using MediatR;

namespace Identity.Application.Commands.RegisterUser;

public record RegisterUserCommand(
    string UserName,
    string Email,
    string PhoneNumber,
    string Password,
    string FirstName,
    string LastName
) : IRequest<AuthResponseDto>;

