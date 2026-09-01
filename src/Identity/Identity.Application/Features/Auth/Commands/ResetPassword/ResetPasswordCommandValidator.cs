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
            .NotEqual(x => x.Email or x.PhoneNumber or x.UserName or x.FirstName or x.LastName or "123456" or).WithMessage("Password cannot be the same as email, phone number, username, first name or last name or 123456 or password");
            .MinimumLength(6).WithMessage("Password must be at least 6 characters")
            .Matches(@"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)").WithMessage("Password must contain at least one uppercase letter, one lowercase letter, and one number");
    }
}

