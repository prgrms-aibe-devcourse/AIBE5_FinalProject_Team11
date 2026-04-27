package club.yogaman.api.pose;

import java.util.List;

import club.yogaman.api.seo.SchemaOrgService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/poses")
public class PoseController {

    private final PoseService service;
    private final SchemaOrgService schemaOrgService;

    public PoseController(PoseService service, SchemaOrgService schemaOrgService) {
        this.service = service;
        this.schemaOrgService = schemaOrgService;
    }

    @GetMapping
    public ResponseEntity<List<Pose>> listAll() {
        return ResponseEntity.ok(service.listPoses());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Pose> getById(@PathVariable String id) {
        return service.findPoseById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping(value = "/{id}.jsonld", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> getPoseJsonLd(@PathVariable String id) {
        return service.findPoseById(id)
                .map(p -> ResponseEntity.ok(schemaOrgService.buildPoseJsonLd(p.getPoseId())))
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping(value = "/{id}/jsonld", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> getPoseJsonLdAlias(@PathVariable String id) {
        return getPoseJsonLd(id);
    }
}
