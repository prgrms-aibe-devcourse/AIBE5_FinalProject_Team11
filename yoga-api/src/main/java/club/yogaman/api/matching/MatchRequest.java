package club.yogaman.api.matching;

import java.util.List;

public class MatchRequest {

    private String userId;
    private List<String> healthFlags;
    private List<String> goals;
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
}
