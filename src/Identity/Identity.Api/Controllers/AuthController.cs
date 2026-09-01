using Identity.Application.DTOs.Auth;
using Identity.Application.Features.Auth.Commands.ForgetPassword;
using Identity.Application.Features.Auth.Commands.GoogleLogin;
using Identity.Application.Features.Auth.Commands.Login;
using Identity.Application.Features.Auth.Commands.ResetPassword;
using Identity.Application.Features.Auth.Commands.Signup;
using Identity.Application.Features.Auth.Queries.GetCurrentUser;
using MediatR;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace Identity.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly IMediator _mediator;

    public AuthController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpPost("signup")]
    [ProducesResponseType(typeof(LoginResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> Signup([FromBody] SignupRequest request)
    {
        try
        {
            var command = new SignupCommand
            {
                UserName = request.UserName,
                Email = request.Email,
                PhoneNumber = request.PhoneNumber,
                Password = request.Password,
                FirstName = request.FirstName,
                LastName = request.LastName,
                Gender = request.Gender
            };

            var result = await _mediator.Send(command);
            return Ok(result);
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
    }

    [HttpPost("login")]
    [ProducesResponseType(typeof(LoginResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> Login([FromBody] LoginRequest request)
    {
        try
        {
            var command = new LoginCommand
            {
                Email = request.Email ?? string.Empty,
                PhoneNumber = request.PhoneNumber ?? string.Empty, 
                UserName = request.UserName ?? string.Empty,
                Password = request.Password
            };
            var result = await _mediator.Send(command);
            return Ok(result);
        }
        catch (UnauthorizedAccessException ex)
        {
            return Unauthorized(new { message = ex.Message });
        }
    }

    [HttpPost("forget-password")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> ForgetPassword([FromBody] ForgetPasswordRequest request)
    {
        try
        {
            var command = new ForgetPasswordCommand
            {
                Email = request.Email ?? string.Empty,
                PhoneNumber = request.PhoneNumber ?? string.Empty,
            };
            await _mediator.Send(command);
            return Ok(new { message = "If Information Correct, a password reset link has been sent." });
        }
        catch (Exception ex)
        {
            return BadRequest(new { message = ex.Message });
        }
    }

    [HttpPost("reset-password")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> ResetPassword([FromBody] ResetPasswordRequest request)
    {
        try
        {
            var command = new ResetPasswordCommand
            {
                Token = request.Token,
                Email = request.Email ?? string.Empty,
                PhoneNumber = request.PhoneNumber ?? string.Empty,
                UserName = request.UserName ?? string.Empty,
                NewPassword = request.NewPassword
            };
            await _mediator.Send(command);
            return Ok(new { message = "Password has been reset successfully." });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            return BadRequest(new { message = ex.Message });
        }
    }

    [HttpGet("google")]
    [ProducesResponseType(StatusCodes.Status302Found)]
    public IActionResult GoogleLogin()
    {
        var properties = new AuthenticationProperties { RedirectUri = "/api/Auth/google-callback" };
        return Challenge(properties, GoogleDefaults.AuthenticationScheme);
    }

    [HttpGet("google-callback")]
    [ProducesResponseType(typeof(LoginResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> GoogleCallback()
    {
        try
        {
            // Get the authentication result
            var result = await HttpContext.AuthenticateAsync(GoogleDefaults.AuthenticationScheme);
            
            if (!result.Succeeded)
            {
                return BadRequest(new { message = "Google authentication failed" });
            }

            // Extract user information from Google claims
            var email = result.Principal?.FindFirst(ClaimTypes.Email)?.Value 
                ?? result.Principal?.FindFirst("email")?.Value 
                ?? string.Empty;
            
            var firstName = result.Principal?.FindFirst(ClaimTypes.GivenName)?.Value 
                ?? result.Principal?.FindFirst("given_name")?.Value 
                ?? string.Empty;
            
            var lastName = result.Principal?.FindFirst(ClaimTypes.Surname)?.Value 
                ?? result.Principal?.FindFirst("family_name")?.Value 
                ?? string.Empty;
            
            var googleId = result.Principal?.FindFirst(ClaimTypes.NameIdentifier)?.Value 
                ?? result.Principal?.FindFirst("sub")?.Value 
                ?? string.Empty;

            if (string.IsNullOrEmpty(email))
            {
                return BadRequest(new { message = "Email not provided by Google" });
            }

            // Sign out the Google authentication scheme
            await HttpContext.SignOutAsync(GoogleDefaults.AuthenticationScheme);

            // Process Google login
            var command = new GoogleLoginCommand
            {
                Email = email,
                FirstName = firstName,
                LastName = lastName,
                GoogleId = googleId
            };

            var loginResponse = await _mediator.Send(command);
            return Ok(loginResponse);
        }
        catch (Exception ex)
        {
            return BadRequest(new { message = ex.Message });
        }
    }

    [HttpGet("me")]
    [Authorize]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> GetCurrentUser()
    {
        try
        {
            var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
            {
                return Unauthorized(new { message = "Invalid token" });
            }

            var query = new GetCurrentUserQuery
            {
                UserId = userId
            };
            var result = await _mediator.Send(query);
            return Ok(result);
        }
        catch (UnauthorizedAccessException ex)
        {
            return Unauthorized(new { message = ex.Message });
        }
    }
}

