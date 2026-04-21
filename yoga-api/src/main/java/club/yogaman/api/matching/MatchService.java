package club.yogaman.api.matching;

import club.yogaman.api.pose.Benefit;
import club.yogaman.api.pose.Contraindication;
import club.yogaman.api.pose.Pose;
import club.yogaman.api.pose.PoseRepository;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class MatchService {

    private final PoseRepository poseRepository;

    public MatchService(PoseRepository poseRepository) {
        this.poseRepository = poseRepository;
    }

    public String matchPlaceholder() {
        return "Phase 2 matching service initialized.";
    }

    public MatchResponse match(MatchRequest request) {
        List<Pose> allPoses = poseRepository.findAll();
        List<String> healthFlags = request.getHealthFlags() != null ? request.getHealthFlags() : Collections.emptyList();
        List<String> goals = request.getGoals() != null ? request.getGoals() : Collections.emptyList();

        List<MatchResult> results = allPoses.stream()
                .map(pose -> score(pose, healthFlags, goals))
                .filter(r -> !r.isBlocked())
                .sorted(Comparator.comparingDouble(MatchResult::getScore).reversed())
                .limit(request.getTopK())
                .collect(Collectors.toList());

        return new MatchResponse(results);
    }

    private MatchResult score(Pose pose, List<String> healthFlags, List<String> goals) {
        // Kill-switch check: block pose if any critical contraindication matches a health flag
        if (pose.getContraindications() != null) {
            for (Contraindication c : pose.getContraindications()) {
                if (c.isKillSwitch() && healthFlags.stream()
                        .anyMatch(flag -> flag.equalsIgnoreCase(c.getCondition()))) {
                    return new MatchResult(
                            pose.getPoseId(),
                            0.0,
                            true,
                            "Blocked due to " + c.getCondition() + " (" + c.getSeverity() + "): " + c.getInstruction()
                    );
                }
            }
        }

        // Score from benefit tags matching goals (weighted sum)
        double score = 0.0;
        if (pose.getBenefits() != null) {
            for (Benefit b : pose.getBenefits()) {
                if (goals.stream().anyMatch(g -> g.equalsIgnoreCase(b.getTag()))) {
                    score += b.getWeight();
                }
            }
        }

        return new MatchResult(pose.getPoseId(), score, false, null);
    }
}
