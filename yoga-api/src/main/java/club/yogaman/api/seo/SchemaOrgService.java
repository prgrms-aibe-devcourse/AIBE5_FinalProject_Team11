package club.yogaman.api.seo;

import club.yogaman.api.pose.Benefit;
import club.yogaman.api.pose.Pose;
import club.yogaman.api.pose.PoseRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.stereotype.Service;

@Service
public class SchemaOrgService {

    private final PoseRepository poseRepository;
    private final ObjectMapper objectMapper;

    public SchemaOrgService(PoseRepository poseRepository, ObjectMapper objectMapper) {
        this.poseRepository = poseRepository;
        this.objectMapper = objectMapper;
    }

    public String buildPoseJsonLd(String poseId) {
        return poseRepository.findById(poseId)
                .map(this::toHowToJsonLd)
                .orElse("{\"error\": \"Pose not found\"}");
    }

    private String toHowToJsonLd(Pose pose) {
        try {
            ObjectNode root = objectMapper.createObjectNode();
            root.put("@context", "https://schema.org");
            root.put("@type", "HowTo");
            root.put("name", pose.getCanonicalName() != null ? pose.getCanonicalName() : pose.getPoseId());
            root.put("alternateName", pose.getCommonName());

            if (pose.getEducationalMetadata() != null && pose.getEducationalMetadata().getAeoSummary() != null) {
                root.put("description", pose.getEducationalMetadata().getAeoSummary());
            }

            // difficulty as educationalLevel
            if (pose.getDifficultyRank() > 0) {
                root.put("educationalLevel", difficultyLabel(pose.getDifficultyRank()));
            }

            // anatomicalFocus as about keywords
            if (pose.getAnatomicalFocus() != null && !pose.getAnatomicalFocus().isEmpty()) {
                ArrayNode focus = root.putArray("about");
                for (String part : pose.getAnatomicalFocus()) {
                    ObjectNode thing = objectMapper.createObjectNode();
                    thing.put("@type", "Thing");
                    thing.put("name", part);
                    focus.add(thing);
                }
            }

            // benefits as HowToStep list
            if (pose.getBenefits() != null && !pose.getBenefits().isEmpty()) {
                ArrayNode steps = root.putArray("step");
                for (Benefit b : pose.getBenefits()) {
                    ObjectNode step = objectMapper.createObjectNode();
                    step.put("@type", "HowToStep");
                    step.put("name", b.getTag());
                    step.put("text", "Benefit: " + b.getTag() + " (weight: " + b.getWeight() + ")");
                    steps.add(step);
                }
            }

            // lineage / instructor note
            if (pose.getEducationalMetadata() != null) {
                if (pose.getEducationalMetadata().getLineageSource() != null) {
                    root.put("teaches", pose.getEducationalMetadata().getLineageSource());
                }
                if (pose.getEducationalMetadata().getFyt100SessionRef() != null) {
                    root.put("isPartOf", pose.getEducationalMetadata().getFyt100SessionRef());
                }
            }

            // geoKeywords as keywords
            if (pose.getGeoKeywords() != null && !pose.getGeoKeywords().isEmpty()) {
                root.put("keywords", String.join(", ", pose.getGeoKeywords()));
            }

            return objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(root);
        } catch (Exception e) {
            return "{\"error\": \"JSON-LD generation failed\"}";
        }
    }

    private String difficultyLabel(int rank) {
        return switch (rank) {
            case 1 -> "Beginner";
            case 2 -> "Elementary";
            case 3 -> "Intermediate";
            case 4 -> "Advanced";
            case 5 -> "Expert";
            default -> "Unknown";
        };
    }
}
