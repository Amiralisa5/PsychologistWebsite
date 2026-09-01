using Identity.Application.Common.Interfaces;
using Microsoft.Extensions.Logging;

namespace Identity.Infrastructure.Services;

public class EmailService : IEmailService
{
    private readonly ILogger<EmailService> _logger;

    public EmailService(ILogger<EmailService> logger)
    {
        _logger = logger;
    }

    public Task SendPasswordResetEmailAsync(string email, string resetToken, CancellationToken cancellationToken = default)
    {
        // TODO: Implement actual email sending (SMTP, SendGrid, etc.)
        // For now, just log it
        _logger.LogInformation("Password reset email sent to {Email} with token: {Token}", email, resetToken);
        
        // In production, you would send an actual email here
        // Example: SendGrid, SMTP, etc.
        
        return Task.CompletedTask;
    }
}

