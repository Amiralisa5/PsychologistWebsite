namespace Identity.Application.DTOs;

public record RegisterUserDto(
    string UserName,
    string Email,
    string PhoneNumber,
    string Password,
    string FirstName,
    string LastName,
    Gender Gender
);

