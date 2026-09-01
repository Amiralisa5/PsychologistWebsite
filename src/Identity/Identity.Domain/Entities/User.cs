namespace Identity.Domain.Entities;

public class User
{
    public Guid Id { get; set; }
    public string UserName { get; set; } ;
    public string Email { get; set; };
    public string PhoneNumber { get; set; };
    public string PasswordHash { get; set; } ;
    public string FirstName { get; set; } ;
    public string LastName { get; set; };
    public  Gender Gender { get; set; }
    public bool IsEmailConfirmed { get; set; }
    public bool IsPhoneNumberConfirmed { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
    public bool IsActive { get; set; } = true;
    
    // Navigation properties
    public ICollection<RefreshToken> RefreshTokens { get; set; } = new List<RefreshToken>();
    public ICollection<PasswordResetToken> PasswordResetTokens { get; set; } = new List<PasswordResetToken>();
}

