package club.yogaman.api.matching;

public class MatchResult {

    private String poseId;
    private double score;
    private boolean blocked;
    private String reason;

    public MatchResult() {
    }

    public MatchResult(String poseId, double score, boolean blocked, String reason) {
        this.poseId = poseId;
        this.score = score;
        this.blocked = blocked;
        this.reason = reason;
    }

    public String getPoseId() {
        return poseId;
    }

    public void setPoseId(String poseId) {
        this.poseId = poseId;
    }

    public double getScore() {
        return score;
    }

    public void setScore(double score) {
        this.score = score;
    }

    public boolean isBlocked() {
        return blocked;
    }

    public void setBlocked(boolean blocked) {
        this.blocked = blocked;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }
}
