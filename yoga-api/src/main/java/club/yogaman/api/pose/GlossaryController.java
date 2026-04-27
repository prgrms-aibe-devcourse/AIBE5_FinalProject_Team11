package club.yogaman.api.pose;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/glossary")
public class GlossaryController {

    private final PoseRepository poseRepository;
    private final ObjectMapper objectMapper;

    public GlossaryController(PoseRepository poseRepository, ObjectMapper objectMapper) {
        this.poseRepository = poseRepository;
        this.objectMapper = objectMapper;
    }

    @GetMapping(value = "/{poseId}", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> getDefinedTerm(@PathVariable String poseId) {
        return poseRepository.findById(poseId)
                .map(pose -> {
                    try {
                        ObjectNode root = objectMapper.createObjectNode();
                        root.put("@context", "https://schema.org");
                        root.put("@type", "DefinedTerm");
                        root.put("@id", "https://yogaman.club/glossary/" + pose.getPoseId());
                        root.put("name", pose.getCanonicalName() != null ? pose.getCanonicalName() : pose.getPoseId());
                        if (pose.getCommonName() != null) root.put("alternateName", pose.getCommonName());
                        if (pose.getNaturalDescription() != null) {
                            root.put("description", pose.getNaturalDescription());
                        }
                        root.put("url", "https://yogaman.club/glossary/" + pose.getPoseId() + "/");
                        ObjectNode termSet = objectMapper.createObjectNode();
                        termSet.put("@type", "DefinedTermSet");
                        termSet.put("name", "Yogaman Pose Glossary");
                        termSet.put("url", "https://yogaman.club/glossary/");
                        root.set("inDefinedTermSet", termSet);
                        return ResponseEntity.ok(
                                objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(root));
                    } catch (Exception e) {
                        return ResponseEntity.ok("{\"error\": \"JSON-LD generation failed\"}");
                    }
                })
                .orElse(ResponseEntity.notFound().build());
    }
}
