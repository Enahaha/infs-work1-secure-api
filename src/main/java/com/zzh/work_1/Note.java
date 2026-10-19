package com.zzh.work_1;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "notes")
public class Note {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false)
    private Long ownerId;
    @Column(nullable = false, length = 2000)
    private String content;
    @Column(nullable = false)
    private Instant createdAt;

    protected Note() {}
    public Note(Long ownerId, String content) {
        this.ownerId = ownerId;
        this.content = content;
        this.createdAt = Instant.now();
    }
    public Long getId() { return id; }
    public String getContent() { return content; }
    public Instant getCreatedAt() { return createdAt; }
}
