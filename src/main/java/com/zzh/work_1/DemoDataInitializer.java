package com.zzh.work_1;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
public class DemoDataInitializer {
    @Bean
    CommandLineRunner initializeDemoUsers(UserAccountRepository users, PasswordEncoder passwords,
            @Value("${app.demo-password:}") String password) {
        return args -> {
            if (users.findByUsername("alice").isPresent() && users.findByUsername("bob").isPresent()) return;
            // BCrypt has a 72-byte limit. ASCII keeps the character and byte limits identical.
            if (password.length() < 12 || password.length() > 72
                    || !password.chars().allMatch(c -> c >= 32 && c <= 126)) {
                throw new IllegalStateException("Set APP_DEMO_PASSWORD to 12-72 printable ASCII characters for first startup");
            }
            for (String username : new String[]{"alice", "bob"}) {
                if (users.findByUsername(username).isEmpty()) {
                    users.save(new UserAccount(username, passwords.encode(password)));
                }
            }
        };
    }
}
