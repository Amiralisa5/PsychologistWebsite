namespace Identity.Application.DTOs;

public record LoginDto(
    string? Email,
    string?PhoneNumber,
    string UserName,
    string Password
);

