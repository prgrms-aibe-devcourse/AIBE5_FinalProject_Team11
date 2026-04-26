package club.yogaman.api.matching;

import club.yogaman.api.pose.Pose;

public class MatchResult {

    private String poseId;
    private String canonicalName;
    private String commonName;
    private int difficultyRank;
    private String naturalDescription;
    private double score;
    private boolean blocked;
    private String reason;

    public MatchResult() {}

    /** Factory: scored (non-blocked) result with full pose metadata. */
    public static MatchResult scored(Pose pose, double score) {
        MatchResult r = new MatchResult();
        r.poseId             = pose.getPoseId();
        r.canonicalName      = pose.getCanonicalName();
        r.commonName         = pose.getCommonName();
        r.difficultyRank     = pose.getDifficultyRank();
        r.naturalDescription = pose.getNaturalDescription();
        r.score              = score;
        r.blocked            = false;
        return r;
    }

    /** Factory: kill-switched (blocked) result. */
    public static MatchResult blocked(Pose pose, String reason) {
        MatchResult r = new MatchResult();
        r.poseId         = pose.getPoseId();
        r.canonicalName  = pose.getCanonicalName();
        r.score          = 0.0;
        r.blocked        = true;
        r.reason         = reason;
        return r;
    }

    // --- Getters ---

    public String getPoseId()            { return poseId; }
    public String getCanonicalName()     { return canonicalName; }
    public String getCommonName()        { return commonName; }
    public int getDifficultyRank()       { return difficultyRank; }
    public String getNaturalDescription(){ return naturalDescription; }
    public double getScore()             { return score; }
    public boolean isBlocked()           { return blocked; }
    public String getReason()            { return reason; }
}
