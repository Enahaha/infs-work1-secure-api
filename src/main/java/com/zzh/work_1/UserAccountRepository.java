package com.zzh.work_1;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserAccountRepository extends JpaRepository<UserAccount, Long> {
    // Spring Data binds username as a parameter; it never becomes SQL syntax.
    Optional<UserAccount> findByUsername(String username);
}
