package club.yogaman.api.pose;

import jakarta.persistence.*;
import org.hibernate.annotations.Fetch;
import org.hibernate.annotations.FetchMode;
import java.util.List;

@Entity
@Table(name = "poses")
public class Pose {

    @Id
    private String poseId;

    private String canonicalName;
    private String commonName;
    private int difficultyRank;

    @ElementCollection
    @CollectionTable(name = "pose_focus", joinColumns = @JoinColumn(name = "pose_id"))
    @Column(name = "focus")
    @Fetch(FetchMode.SUBSELECT)
    private List<String> anatomicalFocus;

    @Embedded
    private EducationalMetadata educationalMetadata;

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "pose_id")
    @Fetch(FetchMode.SUBSELECT)
    private List<Benefit> benefits;

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "pose_id")
    @Fetch(FetchMode.SUBSELECT)
    private List<Contraindication> contraindications;

    @ElementCollection
    @CollectionTable(name = "pose_keywords", joinColumns = @JoinColumn(name = "pose_id"))
    @Column(name = "keyword")
    @Fetch(FetchMode.SUBSELECT)
    private List<String> geoKeywords;

    // Getters and setters

    public String getPoseId() {
        return poseId;
    }

    public void setPoseId(String poseId) {
        this.poseId = poseId;
    }

    public String getCanonicalName() {
        return canonicalName;
    }

    public void setCanonicalName(String canonicalName) {
        this.canonicalName = canonicalName;
    }

    public String getCommonName() {
        return commonName;
    }

    public void setCommonName(String commonName) {
        this.commonName = commonName;
    }

    public int getDifficultyRank() {
        return difficultyRank;
    }

    public void setDifficultyRank(int difficultyRank) {
        this.difficultyRank = difficultyRank;
    }

    public List<String> getAnatomicalFocus() {
        return anatomicalFocus;
    }

    public void setAnatomicalFocus(List<String> anatomicalFocus) {
        this.anatomicalFocus = anatomicalFocus;
    }

    public EducationalMetadata getEducationalMetadata() {
        return educationalMetadata;
    }

    public void setEducationalMetadata(EducationalMetadata educationalMetadata) {
        this.educationalMetadata = educationalMetadata;
    }

    public List<Benefit> getBenefits() {
        return benefits;
    }

    public void setBenefits(List<Benefit> benefits) {
        this.benefits = benefits;
    }

    public List<Contraindication> getContraindications() {
        return contraindications;
    }

    public void setContraindications(List<Contraindication> contraindications) {
        this.contraindications = contraindications;
    }

    public List<String> getGeoKeywords() {
        return geoKeywords;
    }

    public void setGeoKeywords(List<String> geoKeywords) {
        this.geoKeywords = geoKeywords;
    }
}
