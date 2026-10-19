package com.zzh.work_1;

import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface NoteRepository extends JpaRepository<Note, Long> {
    List<Note> findByOwnerIdOrderByIdAsc(Long ownerId);
}
