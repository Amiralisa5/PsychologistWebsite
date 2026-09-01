namespace Identity.Application.DTOs.Auth;

public class ForgetPasswordRequest
{
    public string Email { get; set; } = string.Empty;
    public string PhoneNumber { get; set; } = string.Empty;
}

