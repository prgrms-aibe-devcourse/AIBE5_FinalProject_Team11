package club.yogaman.api.studio;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.jdbc.Sql;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Integration tests for GET /api/v1/studios/nearby.
 *
 * Uses in-memory H2 (test profile) + studio-seed.sql.
 * Two studios are seeded within 5 km of central Seoul; one is ~326 km away in Busan.
 */
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
class StudioControllerIT {

    /** Central Seoul lat/lng used as the query origin. */
    private static final double SEOUL_LAT = 37.5665;
    private static final double SEOUL_LNG = 126.9780;

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    @Sql("/studio-seed.sql")
    void nearbyReturnsOnlyStudiosWithinRadius() {
        String url = "/api/v1/studios/nearby?lat=" + SEOUL_LAT + "&lng=" + SEOUL_LNG + "&radius=5";

        ResponseEntity<List<StudioDistance>> response = restTemplate.exchange(
                url, HttpMethod.GET, null,
                new ParameterizedTypeReference<List<StudioDistance>>() {});

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);

        List<StudioDistance> results = response.getBody();
        assertThat(results).isNotNull().hasSize(2);

        // Busan studio must NOT be included (well outside 5 km)
        results.forEach(r ->
                assertThat(r.getDistanceKm()).isLessThanOrEqualTo(5.0));
    }

    @Test
    @Sql("/studio-seed.sql")
    void nearbyResultsSortedByAscendingDistance() {
        String url = "/api/v1/studios/nearby?lat=" + SEOUL_LAT + "&lng=" + SEOUL_LNG + "&radius=5";

        ResponseEntity<List<StudioDistance>> response = restTemplate.exchange(
                url, HttpMethod.GET, null,
                new ParameterizedTypeReference<List<StudioDistance>>() {});

        List<StudioDistance> results = response.getBody();
        assertThat(results).isNotNull().hasSizeGreaterThan(1);

        // Each subsequent result must be >= previous distance
        for (int i = 1; i < results.size(); i++) {
            assertThat(results.get(i).getDistanceKm())
                    .isGreaterThanOrEqualTo(results.get(i - 1).getDistanceKm());
        }
    }

    @Test
    @Sql("/studio-seed.sql")
    void nearbyDefaultRadiusIs10km() {
        // No radius param → default 10 km — both Seoul studios should be returned
        String url = "/api/v1/studios/nearby?lat=" + SEOUL_LAT + "&lng=" + SEOUL_LNG;

        ResponseEntity<List<StudioDistance>> response = restTemplate.exchange(
                url, HttpMethod.GET, null,
                new ParameterizedTypeReference<List<StudioDistance>>() {});

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull().hasSize(2);
    }

    @Test
    @Sql("/studio-seed.sql")
    void nearbyEmptyWhenRadiusTooSmall() {
        // 0.1 km — no studio is that close to the exact centre point
        String url = "/api/v1/studios/nearby?lat=" + SEOUL_LAT + "&lng=" + SEOUL_LNG + "&radius=0.1";

        ResponseEntity<List<StudioDistance>> response = restTemplate.exchange(
                url, HttpMethod.GET, null,
                new ParameterizedTypeReference<List<StudioDistance>>() {});

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull().isEmpty();
    }
}
