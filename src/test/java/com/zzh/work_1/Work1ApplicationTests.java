package com.zzh.work_1;

import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jose.jws.SignatureAlgorithm;
import org.springframework.security.oauth2.jwt.*;
import org.springframework.test.web.servlet.MockMvc;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:h2:mem:work1test;DB_CLOSE_DELAY=-1",
        "spring.jpa.hibernate.ddl-auto=create-drop",
        "app.demo-password=Test-password-2026"
})
@AutoConfigureMockMvc
class Work1ApplicationTests {
    @Autowired MockMvc mvc;
    @Autowired UserAccountRepository users;
    @Autowired NoteRepository notes;
    @Autowired PasswordEncoder passwords;
    @Autowired JwtEncoder encoder;
    private final JsonMapper json = JsonMapper.builder().build();

    @BeforeEach
    void clearNotes() { notes.deleteAll(); }

    private String login(String username) throws Exception {
        String response = mvc.perform(post("/auth/login").contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsString(java.util.Map.of("login", username, "password", "Test-password-2026"))))
                .andExpect(status().isOk()).andExpect(jsonPath("$.tokenType").value("Bearer"))
                .andReturn().getResponse().getContentAsString();
        return json.readTree(response).get("token").asText();
    }

    @Test
    void passwordsAreHashedAndWrongCredentialsAreRejected() throws Exception {
        String stored = users.findByUsername("alice").orElseThrow().getPasswordHash();
        assertThat(stored).isNotEqualTo("Test-password-2026");
        assertThat(passwords.matches("Test-password-2026", stored)).isTrue();
        for (String name : List.of("alice", "unknown", "' OR '1'='1")) {
            mvc.perform(post("/auth/login").contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(java.util.Map.of("login", name, "password", "wrong"))))
                    .andExpect(status().isUnauthorized());
        }
    }

    @Test
    void protectedEndpointsRequireTokens() throws Exception {
        mvc.perform(get("/api/data")).andExpect(status().isUnauthorized());
        mvc.perform(post("/api/notes").contentType(MediaType.APPLICATION_JSON)
                .content("{\"content\":\"hello\"}"))
                .andExpect(status().isUnauthorized());
        mvc.perform(get("/api/data").header("Authorization", "Bearer broken.token.value"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void loginCreateAndReadEscapeHtmlAndIsolateOwners() throws Exception {
        String alice = login("alice");
        String bob = login("bob");
        String input = "<script>alert('x')</script> & SQL ' OR 1=1 --";
        mvc.perform(post("/api/notes").header("Authorization", "Bearer " + alice)
                .contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsString(java.util.Map.of("content", input, "ownerId", users.findByUsername("bob").orElseThrow().getId()))))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.content").value(org.springframework.web.util.HtmlUtils.htmlEscape(input)));
        assertThat(notes.findAll().get(0).getContent()).isEqualTo(input);
        mvc.perform(get("/api/data").header("Authorization", "Bearer " + alice))
                .andExpect(status().isOk()).andExpect(jsonPath("$.length()").value(1))
                .andExpect(jsonPath("$[0].content").value(org.springframework.web.util.HtmlUtils.htmlEscape(input)));
        mvc.perform(get("/api/data").header("Authorization", "Bearer " + bob))
                .andExpect(status().isOk()).andExpect(content().json("[]"));
    }

    private String signedToken(String issuer, List<String> audience, Instant expiry) {
        JwtClaimsSet claims = JwtClaimsSet.builder().issuer(issuer).audience(audience)
                .subject(users.findByUsername("alice").orElseThrow().getId().toString())
                .issuedAt(Instant.now().minusSeconds(7200)).expiresAt(expiry).build();
        return encoder.encode(JwtEncoderParameters.from(JwsHeader.with(SignatureAlgorithm.RS256).build(), claims)).getTokenValue();
    }

    @Test
    void expiredWrongIssuerAndWrongAudienceTokensAreRejected() throws Exception {
        for (String token : List.of(
                signedToken(SecurityConfig.ISSUER, List.of(SecurityConfig.AUDIENCE), Instant.now().minusSeconds(3600)),
                signedToken("other-issuer", List.of(SecurityConfig.AUDIENCE), Instant.now().plusSeconds(300)),
                signedToken(SecurityConfig.ISSUER, List.of("other-client"), Instant.now().plusSeconds(300)))) {
            mvc.perform(get("/api/data").header("Authorization", "Bearer " + token))
                    .andExpect(status().isUnauthorized());
        }
    }

    @Test
    void tamperedTokenIsRejected() throws Exception {
        String[] parts = login("alice").split("\\.");
        char changed = parts[2].charAt(0) == 'A' ? 'B' : 'A';
        String tampered = parts[0] + "." + parts[1] + "." + changed + parts[2].substring(1);
        mvc.perform(get("/api/data").header("Authorization", "Bearer " + tampered))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void invalidRequestsAreRejected() throws Exception {
        String token = login("alice");
        for (String input : List.of("", " ", "a".repeat(2001))) {
            mvc.perform(post("/api/notes").header("Authorization", "Bearer " + token)
                    .contentType(MediaType.APPLICATION_JSON)
                    .content(json.writeValueAsString(java.util.Map.of("content", input))))
                    .andExpect(status().isBadRequest());
        }
        mvc.perform(post("/auth/login").contentType(MediaType.APPLICATION_JSON).content("{broken"))
                .andExpect(status().isBadRequest());
    }
    @Test
    void cookiesAndHttpBasicDoNotAuthenticateRequests() throws Exception {
        String token = login("alice");
        mvc.perform(get("/api/data").cookie(
                new jakarta.servlet.http.Cookie("token", token),
                new jakarta.servlet.http.Cookie("JSESSIONID", "not-a-session")))
                .andExpect(status().isUnauthorized());
        String basic = java.util.Base64.getEncoder().encodeToString(
                "alice:Test-password-2026".getBytes(java.nio.charset.StandardCharsets.UTF_8));
        mvc.perform(get("/api/data").header("Authorization", "Basic " + basic))
                .andExpect(status().isUnauthorized());
        mvc.perform(get("/api/data").header("Authorization", "Bearer " + token))
                .andExpect(status().isOk()).andExpect(header().doesNotExist("Set-Cookie"));
    }

}
