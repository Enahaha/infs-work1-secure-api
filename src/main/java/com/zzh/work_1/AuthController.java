package com.zzh.work_1;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.time.Instant;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jose.jws.SignatureAlgorithm;
import org.springframework.security.oauth2.jwt.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/auth")
public class AuthController {
    private final UserAccountRepository users;
    private final PasswordEncoder passwords;
    private final JwtEncoder encoder;
    private final String dummyHash;

    public AuthController(UserAccountRepository users, PasswordEncoder passwords, JwtEncoder encoder) {
        this.users = users;
        this.passwords = passwords;
        this.encoder = encoder;
        this.dummyHash = passwords.encode(java.util.UUID.randomUUID().toString());
    }

    public record LoginRequest(
            @NotBlank @Size(max = 50) String login,
            @NotBlank @Size(max = 72) @Pattern(regexp = "[\\x20-\\x7E]+") String password) {}
    public record LoginResponse(String token, String tokenType, long expiresIn) {}

    @PostMapping("/login")
    public LoginResponse login(@Valid @RequestBody LoginRequest request) {
        var user = users.findByUsername(request.login());
        // Also verify a hash for unknown users; return the same error for both cases.
        boolean valid = passwords.matches(request.password(), user.map(UserAccount::getPasswordHash).orElse(dummyHash));
        if (user.isEmpty() || !valid) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid username or password");
        }
        Instant now = Instant.now();
        JwtClaimsSet claims = JwtClaimsSet.builder()
                .issuer(SecurityConfig.ISSUER).audience(List.of(SecurityConfig.AUDIENCE))
                .subject(user.get().getId().toString()).issuedAt(now).expiresAt(now.plusSeconds(1800)).build();
        String token = encoder.encode(JwtEncoderParameters.from(
                JwsHeader.with(SignatureAlgorithm.RS256).build(), claims)).getTokenValue();
        return new LoginResponse(token, "Bearer", 1800);
    }
}
