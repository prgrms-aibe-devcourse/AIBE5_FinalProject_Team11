package club.yogaman.api.instructor;

import jakarta.persistence.*;
import org.hibernate.annotations.UpdateTimestamp;
import java.math.BigDecimal;
import java.time.OffsetDateTime;
import java.util.List;

@Entity
@Table(name = "instructors")
public class Instructor {

    @Id
    private String instructorId;

    @Column(nullable = false)
    private String fullName;

    @Column(columnDefinition = "TEXT")
    private String bio;

    private String certificationLevel;   // RYT-200 | RYT-500 | E-RYT-200 | E-RYT-500
    private String yogaAllianceId;
    private boolean fytCertified;

    private String lineageSchool;
    private short lineageDepth;

    private String instagramHandle;
    private Integer instagramFollowers;
    private String instagramUrl;
    private String websiteUrl;

    @Column(precision = 3, scale = 2)
    private BigDecimal avgRating;
    private int reviewCount;

    @Column(nullable = false, precision = 4, scale = 3)
    private BigDecimal instructorTrustScore = BigDecimal.ZERO;

    @ElementCollection
    @CollectionTable(name = "instructor_specialties",
            joinColumns = @JoinColumn(name = "instructor_id"))
    @Column(name = "specialty")
    private List<String> specialties;

    private String city;
    private String country;

    private String dataSource = "manual";
    private OffsetDateTime scrapedAt;

    @UpdateTimestamp
    private OffsetDateTime updatedAt;

    // --- Getters / Setters ---

    public String getInstructorId()                   { return instructorId; }
    public void setInstructorId(String id)            { this.instructorId = id; }

    public String getFullName()                       { return fullName; }
    public void setFullName(String fullName)          { this.fullName = fullName; }

    public String getBio()                            { return bio; }
    public void setBio(String bio)                    { this.bio = bio; }

    public String getCertificationLevel()             { return certificationLevel; }
    public void setCertificationLevel(String l)       { this.certificationLevel = l; }

    public String getYogaAllianceId()                 { return yogaAllianceId; }
    public void setYogaAllianceId(String id)          { this.yogaAllianceId = id; }

    public boolean isFytCertified()                   { return fytCertified; }
    public void setFytCertified(boolean b)            { this.fytCertified = b; }

    public String getLineageSchool()                  { return lineageSchool; }
    public void setLineageSchool(String s)            { this.lineageSchool = s; }

    public short getLineageDepth()                    { return lineageDepth; }
    public void setLineageDepth(short d)              { this.lineageDepth = d; }

    public String getInstagramHandle()                { return instagramHandle; }
    public void setInstagramHandle(String h)          { this.instagramHandle = h; }

    public Integer getInstagramFollowers()            { return instagramFollowers; }
    public void setInstagramFollowers(Integer f)      { this.instagramFollowers = f; }

    public String getInstagramUrl()                   { return instagramUrl; }
    public void setInstagramUrl(String u)             { this.instagramUrl = u; }

    public String getWebsiteUrl()                     { return websiteUrl; }
    public void setWebsiteUrl(String u)               { this.websiteUrl = u; }

    public BigDecimal getAvgRating()                  { return avgRating; }
    public void setAvgRating(BigDecimal r)            { this.avgRating = r; }

    public int getReviewCount()                       { return reviewCount; }
    public void setReviewCount(int c)                 { this.reviewCount = c; }

    public BigDecimal getInstructorTrustScore()       { return instructorTrustScore; }
    public void setInstructorTrustScore(BigDecimal s) { this.instructorTrustScore = s; }

    public List<String> getSpecialties()              { return specialties; }
    public void setSpecialties(List<String> s)        { this.specialties = s; }

    public String getCity()                           { return city; }
    public void setCity(String city)                  { this.city = city; }

    public String getCountry()                        { return country; }
    public void setCountry(String c)                  { this.country = c; }

    public String getDataSource()                     { return dataSource; }
    public void setDataSource(String s)               { this.dataSource = s; }

    public OffsetDateTime getScrapedAt()              { return scrapedAt; }
    public void setScrapedAt(OffsetDateTime t)        { this.scrapedAt = t; }

    public OffsetDateTime getUpdatedAt()              { return updatedAt; }
}
