 namespace Identity.Application.Common.Interfaces;

public interface ISmsService
{
    Task SendPasswordResetSmsAsync(string phoneNumber, string resetToken, CancellationToken cancellationToken = default);
}
