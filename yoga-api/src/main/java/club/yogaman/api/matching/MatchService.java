package club.yogaman.api.matching;

import club.yogaman.api.pose.Benefit;
import club.yogaman.api.pose.Contraindication;
import club.yogaman.api.pose.Pose;
import club.yogaman.api.pose.PoseRepository;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

@Service
public class MatchService {

    private final PoseRepository poseRepository;

    public MatchService(PoseRepository poseRepository) {
        this.poseRepository = poseRepository;
    }

    /**
     * Maps the UI goal vocabulary (CamelCase / underscore) to the benefit tag
     * vocabulary stored in pose_benefits.tag (lowercase, single-word).
     *
     * Goals come from the frontend MatchPanel:
     *   Spinal_Mobility, Back_Pain_Relief, Core_Strength, Hip_Flexibility,
     *   Balance, Stress_Relief, Shoulder_Opening, Strength
     *
     * Tags come from the enrichment pipeline (enrich_poses.py):
     *   flexibility, mobility, strength, balance, stability,
     *   relief, release, posture, core, stress, back, hip, shoulder, neck
     */
    private static final Map<String, List<String>> GOAL_TAG_MAP = Map.of(
        "Spinal_Mobility",  List.of("mobility", "back", "flexibility", "release", "posture"),
        "Back_Pain_Relief", List.of("back", "relief", "stress", "posture", "release"),
        "Core_Strength",    List.of("core", "strength", "stability"),
        "Hip_Flexibility",  List.of("hip", "flexibility", "mobility", "release"),
        "Balance",          List.of("balance", "stability"),
        "Stress_Relief",    List.of("stress", "relief", "release"),
        "Shoulder_Opening", List.of("shoulder", "release", "flexibility"),
        "Strength",         List.of("strength", "core", "stability")
    );

    public String matchPlaceholder() {
        return "match-service OK";
    }

    public MatchResponse match(MatchRequest request) {
        List<Pose> allPoses = poseRepository.findAll();
        List<String> healthFlags = request.getHealthFlags() != null
                ? request.getHealthFlags() : Collections.emptyList();
        List<String> goals = request.getGoals() != null
                ? request.getGoals() : Collections.emptyList();

        // Expand goals → flat set of benefit tags to match against
        Set<String> expandedTags = goals.stream()
                .flatMap(g -> GOAL_TAG_MAP
                        .getOrDefault(g, List.of(g.toLowerCase().replace(" ", "_")))
                        .stream())
                .collect(Collectors.toSet());

        List<MatchResult> results = allPoses.stream()
                .map(pose -> score(pose, healthFlags, expandedTags))
                .filter(r -> !r.isBlocked())
                .sorted(Comparator.comparingDouble(MatchResult::getScore).reversed())
                .limit(request.getTopK())
                .collect(Collectors.toList());

        return new MatchResponse(results);
    }

    private MatchResult score(Pose pose, List<String> healthFlags, Set<String> expandedTags) {
        // Kill-Switch: block pose if any CRITICAL contraindication matches a health flag
        if (pose.getContraindications() != null) {
            for (Contraindication c : pose.getContraindications()) {
                if (c.isKillSwitch() && healthFlags.stream()
                        .anyMatch(flag -> flag.equalsIgnoreCase(c.getCondition()))) {
                    return MatchResult.blocked(
                            pose,
                            "Blocked: " + c.getCondition() + " (" + c.getSeverity() + ") — " + c.getInstruction()
                    );
                }
            }
        }

        // Weighted sum of benefit tags that intersect the expanded goal tags
        double score = 0.0;
        if (pose.getBenefits() != null) {
            for (Benefit b : pose.getBenefits()) {
                if (expandedTags.stream().anyMatch(t -> t.equalsIgnoreCase(b.getTag()))) {
                    score += b.getWeight();
                }
            }
        }

        return MatchResult.scored(pose, score);
    }
}
