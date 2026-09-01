using Identity.Application.DTOs;
using MediatR;

namespace Identity.Application.Commands.Login;

public record LoginCommand(
    string Email,
    string PhoneNumber,
    string Password
) : IRequest<AuthResponseDto>;

