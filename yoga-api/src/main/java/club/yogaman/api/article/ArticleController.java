package club.yogaman.api.article;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/articles")
public class ArticleController {

    private final ArticleRepository repo;
    private final ObjectMapper objectMapper;

    public ArticleController(ArticleRepository repo, ObjectMapper objectMapper) {
        this.repo = repo;
        this.objectMapper = objectMapper;
    }

    @GetMapping
    public List<Article> list() {
        return repo.findAll();
    }

    @GetMapping("/{slug}")
    public ResponseEntity<Article> get(@PathVariable String slug) {
        return repo.findBySlug(slug)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping(value = "/{slug}/jsonld", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> getJsonLd(@PathVariable String slug) {
        return repo.findBySlug(slug)
                .map(article -> {
                    try {
                        ObjectNode root = objectMapper.createObjectNode();
                        root.put("@context", "https://schema.org");
                        root.put("@type", article.getSchemaType() != null ? article.getSchemaType() : "Article");
                        root.put("@id", "https://yogaman.club/articles/" + article.getSlug());
                        root.put("headline", article.getTitle());
                        if (article.getSummary() != null) root.put("description", article.getSummary());
                        if (article.getBody() != null) root.put("articleBody", article.getBody());
                        root.put("url", "https://yogaman.club/articles/" + article.getSlug() + "/");
                        root.put("inLanguage", article.getLanguage());

                        if (article.getPublishedAt() != null) {
                            root.put("datePublished", article.getPublishedAt().toLocalDate().toString());
                        }
                        if (article.getUpdatedAt() != null) {
                            root.put("dateModified", article.getUpdatedAt().toLocalDate().toString());
                        }

                        // Author with FYT credential for E-E-A-T
                        ObjectNode author = objectMapper.createObjectNode();
                        author.put("@type", "Person");
                        author.put("name", article.getAuthorName());
                        author.put("url", "https://elbee.yogaman.club");
                        ObjectNode credential = objectMapper.createObjectNode();
                        credential.put("@type", "EducationalOccupationalCredential");
                        credential.put("name", article.getAuthorFytCert());
                        credential.put("credentialCategory", "FYT Certified");
                        author.set("hasCredential", credential);
                        root.set("author", author);

                        ObjectNode publisher = objectMapper.createObjectNode();
                        publisher.put("@type", "Organization");
                        publisher.put("name", "Yogaman");
                        publisher.put("url", "https://yogaman.club");
                        root.set("publisher", publisher);

                        return ResponseEntity.ok(
                                objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(root));
                    } catch (Exception e) {
                        return ResponseEntity.ok("{\"error\": \"JSON-LD generation failed\"}");
                    }
                })
                .orElse(ResponseEntity.notFound().build());
    }
}
