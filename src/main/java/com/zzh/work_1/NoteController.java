package com.zzh.work_1;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.time.Instant;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.util.HtmlUtils;

@RestController
@RequestMapping("/api")
public class NoteController {
    private final NoteRepository notes;
    public NoteController(NoteRepository notes) { this.notes = notes; }

    public record CreateNoteRequest(@NotBlank @Size(max = 2000) String content) {}
    // Explicit contract: content is HTML-escaped text, never raw HTML.
    public record NoteResponse(Long id, String content, Instant createdAt) {
        static NoteResponse from(Note note) {
            return new NoteResponse(note.getId(), HtmlUtils.htmlEscape(note.getContent()), note.getCreatedAt());
        }
    }

    @GetMapping("/data")
    public List<NoteResponse> data(@AuthenticationPrincipal Jwt jwt) {
        return notes.findByOwnerIdOrderByIdAsc(Long.valueOf(jwt.getSubject()))
                .stream().map(NoteResponse::from).toList();
    }

    @PostMapping("/notes")
    @ResponseStatus(HttpStatus.CREATED)
    public NoteResponse create(@AuthenticationPrincipal Jwt jwt, @Valid @RequestBody CreateNoteRequest request) {
        // Owner comes from the verified token, not a client-supplied user ID.
        return NoteResponse.from(notes.save(new Note(Long.valueOf(jwt.getSubject()), request.content())));
    }
}
