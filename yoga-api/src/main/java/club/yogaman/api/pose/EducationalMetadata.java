package club.yogaman.api.pose;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;

@Embeddable
public class EducationalMetadata {

    @Column(name = "instructor_cue_priority", length = 1000)
    private String instructorCuePriority;

    @Column(name = "lineage_source")
    private String lineageSource;

    @Column(name = "fyt100_session_ref")
    private String fyt100SessionRef;

    @Column(name = "aeo_summary", length = 2000)
    private String aeoSummary;

    public String getInstructorCuePriority() {
        return instructorCuePriority;
    }

    public void setInstructorCuePriority(String instructorCuePriority) {
        this.instructorCuePriority = instructorCuePriority;
    }

    public String getLineageSource() {
        return lineageSource;
    }

    public void setLineageSource(String lineageSource) {
        this.lineageSource = lineageSource;
    }

    public String getFyt100SessionRef() {
        return fyt100SessionRef;
    }

    public void setFyt100SessionRef(String fyt100SessionRef) {
        this.fyt100SessionRef = fyt100SessionRef;
    }

    public String getAeoSummary() {
        return aeoSummary;
    }

    public void setAeoSummary(String aeoSummary) {
        this.aeoSummary = aeoSummary;
    }
}
