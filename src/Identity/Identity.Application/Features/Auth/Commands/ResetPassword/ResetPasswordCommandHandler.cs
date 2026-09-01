using Identity.Application.Common.Interfaces;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace Identity.Application.Features.Auth.Commands.ResetPassword;

public class ResetPasswordCommandHandler : IRequestHandler<ResetPasswordCommand, Unit>
{
    private readonly IIdentityDbContext _context;
    private readonly IPasswordHasher _passwordHasher;

    public ResetPasswordCommandHandler(
        IIdentityDbContext context,
        IPasswordHasher passwordHasher)
    {
        _context = context;
        _passwordHasher = passwordHasher;
    }

    public async Task<Unit> Handle(ResetPasswordCommand request, CancellationToken cancellationToken)
    {
        var user = await _context.Users
            .FirstOrDefaultAsync(u => (u.Email == request.Email || u.PhoneNumber == request.PhoneNumber || u.UserName == request.UserName) && u.IsActive, cancellationToken);

        if (user == null)
        {
            throw new InvalidOperationException("Invalid reset token or email, phone number or username");
        }

        var resetToken = await _context.PasswordResetTokens
            .FirstOrDefaultAsync(
                t => t.Token == request.Token &&
                     t.UserId == user.Id &&
                     !t.IsUsed &&
                     t.ExpiresAt > DateTime.UtcNow,
                cancellationToken);

        if (resetToken == null)
        {
            throw new InvalidOperationException("Invalid or expired reset token");
        }

        // Update password
        user.PasswordHash = _passwordHasher.HashPassword(request.NewPassword);
        user.UpdatedAt = DateTime.UtcNow;

        // Mark token as used
        resetToken.IsUsed = true;

        await _context.SaveChangesAsync(cancellationToken);

        return Unit.Value;
    }
}

