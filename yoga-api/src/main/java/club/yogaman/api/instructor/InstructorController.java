package club.yogaman.api.instructor;

import club.yogaman.api.seo.SchemaOrgService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/instructors")
public class InstructorController {

    private final InstructorRepository repo;
    private final SchemaOrgService schemaOrgService;

    public InstructorController(InstructorRepository repo, SchemaOrgService schemaOrgService) {
        this.repo = repo;
        this.schemaOrgService = schemaOrgService;
    }

    @GetMapping
    public List<Instructor> list(
            @RequestParam(required = false) String city,
            @RequestParam(required = false) String specialty) {
        if (city != null)      return repo.findByCityIgnoreCase(city);
        if (specialty != null) return repo.findBySpecialtiesContaining(specialty);
        return repo.findByOrderByInstructorTrustScoreDesc();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Instructor> get(@PathVariable String id) {
        return repo.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public Instructor create(@RequestBody Instructor instructor) {
        return repo.save(instructor);
    }

    @GetMapping(value = "/{id}/jsonld", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> getJsonLd(@PathVariable String id) {
        if (!repo.existsById(id)) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(schemaOrgService.buildInstructorJsonLd(id));
    }
}
