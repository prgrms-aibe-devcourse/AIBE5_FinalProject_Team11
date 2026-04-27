package club.yogaman.api.matching;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import java.util.List;

public class MatchRequest {

    private String userId;
    private List<String> healthFlags;
    private List<String> goals;

    /** BEGINNER | INTERMEDIATE | ADVANCED */
    private String experienceLevel = "INTERMEDIATE";

    /** session time budget in minutes */
    private int availableMinutes = 60;

    @Min(1) @Max(100)
    private int topK = 10;

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public List<String> getHealthFlags() {
        return healthFlags;
    }

    public void setHealthFlags(List<String> healthFlags) {
        this.healthFlags = healthFlags;
    }

    public List<String> getGoals() {
        return goals;
    }

    public void setGoals(List<String> goals) {
        this.goals = goals;
    }

    public int getTopK() {
        return topK;
    }

    public void setTopK(int topK) {
        this.topK = topK;
    }

    public String getExperienceLevel() {
        return experienceLevel;
    }

    public void setExperienceLevel(String experienceLevel) {
        this.experienceLevel = experienceLevel;
    }

    public int getAvailableMinutes() {
        return availableMinutes;
    }

    public void setAvailableMinutes(int availableMinutes) {
        this.availableMinutes = availableMinutes;
    }
}
