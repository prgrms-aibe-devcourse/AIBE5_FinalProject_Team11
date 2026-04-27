package club.yogaman.api.pose;

import java.util.List;

import club.yogaman.api.seo.SchemaOrgService;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
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
    private final PoseQaRepository poseQaRepository;
    private final ObjectMapper objectMapper;

    public PoseController(PoseService service, SchemaOrgService schemaOrgService,
                          PoseQaRepository poseQaRepository, ObjectMapper objectMapper) {
        this.service = service;
        this.schemaOrgService = schemaOrgService;
        this.poseQaRepository = poseQaRepository;
        this.objectMapper = objectMapper;
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

    @GetMapping(value = "/{id}/faq", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> getPoseFaq(@PathVariable String id) {
        if (service.findPoseById(id).isEmpty()) return ResponseEntity.notFound().build();
        List<PoseQa> qaList = poseQaRepository.findByPoseId(id);
        try {
            ObjectNode root = objectMapper.createObjectNode();
            root.put("@context", "https://schema.org");
            root.put("@type", "FAQPage");
            root.put("url", "https://yogaman.club/poses/" + id + "/faq");
            ArrayNode mainEntity = root.putArray("mainEntity");
            for (PoseQa qa : qaList) {
                ObjectNode question = objectMapper.createObjectNode();
                question.put("@type", "Question");
                question.put("name", qa.getQuestion());
                ObjectNode acceptedAnswer = objectMapper.createObjectNode();
                acceptedAnswer.put("@type", "Answer");
                acceptedAnswer.put("text", qa.getAnswer());
                question.set("acceptedAnswer", acceptedAnswer);
                mainEntity.add(question);
            }
            return ResponseEntity.ok(
                    objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(root));
        } catch (Exception e) {
            return ResponseEntity.ok("{\"error\": \"JSON-LD generation failed\"}");
        }
    }
}
