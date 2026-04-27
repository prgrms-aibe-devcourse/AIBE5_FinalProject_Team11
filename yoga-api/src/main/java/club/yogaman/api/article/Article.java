package club.yogaman.api.article;

import jakarta.persistence.*;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.OffsetDateTime;

@Entity
@Table(name = "articles")
public class Article {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String slug;

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String summary;

    @Column(columnDefinition = "TEXT")
    private String body;

    @Column(nullable = false)
    private String schemaType = "Article";

    @Column(nullable = false)
    private String authorName = "elbee";

    @Column(nullable = false)
    private String authorFytCert = "FYT100";

    private OffsetDateTime publishedAt;

    @UpdateTimestamp
    private OffsetDateTime updatedAt;

    @Column(nullable = false)
    private String language = "en";

    public Long getId()                        { return id; }
    public void setId(Long id)                 { this.id = id; }

    public String getSlug()                    { return slug; }
    public void setSlug(String slug)           { this.slug = slug; }

    public String getTitle()                   { return title; }
    public void setTitle(String title)         { this.title = title; }

    public String getSummary()                 { return summary; }
    public void setSummary(String summary)     { this.summary = summary; }

    public String getBody()                    { return body; }
    public void setBody(String body)           { this.body = body; }

    public String getSchemaType()              { return schemaType; }
    public void setSchemaType(String t)        { this.schemaType = t; }

    public String getAuthorName()              { return authorName; }
    public void setAuthorName(String n)        { this.authorName = n; }

    public String getAuthorFytCert()           { return authorFytCert; }
    public void setAuthorFytCert(String c)     { this.authorFytCert = c; }

    public OffsetDateTime getPublishedAt()     { return publishedAt; }
    public void setPublishedAt(OffsetDateTime t){ this.publishedAt = t; }

    public OffsetDateTime getUpdatedAt()       { return updatedAt; }

    public String getLanguage()                { return language; }
    public void setLanguage(String l)          { this.language = l; }
}
