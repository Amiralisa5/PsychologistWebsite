using FluentValidation;

namespace Identity.Application.Features.Auth.Commands.ResetPassword;

public class ResetPasswordCommandValidator : AbstractValidator<ResetPasswordCommand>
{
    public ResetPasswordCommandValidator()
    {
        RuleFor(x => x.Token)
            .NotEmpty().WithMessage("Token is required");

        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("Email is required")
            .EmailAddress().WithMessage("Invalid email format");

        RuleFor(x => x.PhoneNumber)
            .NotEmpty().WithMessage("Phone number is required")
            .Matches(@"^\+[1-9]\d{1,14}$").WithMessage("Invalid phone number format");

        RuleFor(x => x.UserName)
            .NotEmpty().WithMessage("Username is required")
            .MinimumLength(3).WithMessage("Username must be at least 3 characters");

        RuleFor(x => x.NewPassword)
            .NotEmpty().WithMessage("New password is required")
            .MinimumLength(6).WithMessage("Password must be at least 6 characters")
            .Matches(@"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)").WithMessage("Password must contain at least one uppercase letter, one lowercase letter, and one number")
            .Must((command, newPassword) =>
                !string.Equals(newPassword, command.Email, System.StringComparison.OrdinalIgnoreCase)
                && !string.Equals(newPassword, command.PhoneNumber, System.StringComparison.OrdinalIgnoreCase)
                && !string.Equals(newPassword, command.UserName, System.StringComparison.OrdinalIgnoreCase)
                && !string.Equals(newPassword, "123456", System.StringComparison.OrdinalIgnoreCase)
                && !string.Equals(newPassword, "password", System.StringComparison.OrdinalIgnoreCase)
            ).WithMessage("Password cannot be the same as email, phone number, username, '123456', or 'password'");
    }
}

