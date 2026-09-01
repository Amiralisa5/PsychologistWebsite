namespace Identity.Application.DTOs;

public record AuthResponseDto(
    string Token,
    string UserName,
    string Email,
    string PhoneNumber,
    string FirstName,
    string LastName
);

