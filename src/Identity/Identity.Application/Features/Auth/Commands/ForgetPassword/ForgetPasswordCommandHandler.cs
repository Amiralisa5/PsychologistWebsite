using Identity.Application.Common.Interfaces;
using Identity.Domain.Entities;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace Identity.Application.Features.Auth.Commands.ForgetPassword;

public class ForgetPasswordCommandHandler : IRequestHandler<ForgetPasswordCommand, Unit>
{
    private readonly IIdentityDbContext _context;
    private readonly IEmailService _emailService;
    private readonly ISmsService _smsService;
    private readonly IJwtTokenGenerator _jwtTokenGenerator;

    public ForgetPasswordCommandHandler(
        IIdentityDbContext context,
        IEmailService emailService,
        ISmsService smsService,
        IJwtTokenGenerator jwtTokenGenerator)
    {
        _context = context;
        _emailService = emailService;
        _smsService = smsService;
        _jwtTokenGenerator = jwtTokenGenerator;
    }

    public async Task<Unit> Handle(ForgetPasswordCommand request, CancellationToken cancellationToken)
    {
        var user = await _context.Users
            .FirstOrDefaultAsync(u => u.Email == request.Email || u.PhoneNumber == request.PhoneNumber && u.IsActive, cancellationToken);

        if (user != null)
        {
            var resetToken = _jwtTokenGenerator.GenerateRefreshToken();

            var passwordResetToken = new PasswordResetToken
            {
                Id = Guid.NewGuid(),
                UserId = user.Id,
                Token = resetToken,
                ExpiresAt = DateTime.UtcNow.AddHours(1),
                CreatedAt = DateTime.UtcNow,
                IsUsed = false
            };

            _context.PasswordResetTokens.Add(passwordResetToken);
            await _context.SaveChangesAsync(cancellationToken);

            // Send email (in production, this should be async/queued)
            await _emailService.SendPasswordResetEmailAsync(user.Email, resetToken, cancellationToken);
            await _smsService.SendPasswordResetSmsAsync(user.PhoneNumber, resetToken, cancellationToken);
        }

        // Always return success to prevent email enumeration
        return Unit.Value;
    }
}

