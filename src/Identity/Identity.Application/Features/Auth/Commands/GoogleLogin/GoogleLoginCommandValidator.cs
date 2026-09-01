using FluentValidation;

namespace Identity.Application.Features.Auth.Commands.GoogleLogin;

public class GoogleLoginCommandValidator : AbstractValidator<GoogleLoginCommand>
{
    public GoogleLoginCommandValidator()
    {
        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("Email is required")
            .EmailAddress().WithMessage("Invalid email format");

        RuleFor(x => x.GoogleId)
            .NotEmpty().WithMessage("Google ID is required");
    }
}

