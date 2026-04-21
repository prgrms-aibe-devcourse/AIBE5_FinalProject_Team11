package club.yogaman.api.matching;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.jdbc.Sql;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Integration tests for POST /api/v1/match.
 *
 * Uses an in-memory H2 database (MODE=PostgreSQL) with Flyway V1 only.
 * Seed data is loaded by match-seed.sql before each test method.
 */
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
@DirtiesContext(classMode = DirtiesContext.ClassMode.AFTER_EACH_TEST_METHOD)
class MatchControllerIT {

    @Autowired
    private TestRestTemplate restTemplate;

    // ── Kill-switch test ──────────────────────────────────────────────────────

    @Test
    @Sql("/match-seed.sql")
    void killSwitchBlocksLotusWhenKneeInjuryFlagged() {
        MatchRequest request = new MatchRequest();
        request.setHealthFlags(List.of("knee_injury"));
        request.setGoals(List.of("strength", "flexibility"));
        request.setTopK(10);

        ResponseEntity<MatchResponse> response =
                restTemplate.postForEntity("/api/v1/match", request, MatchResponse.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);

        List<MatchResult> results = response.getBody().getResults();
        // lotus must not appear — it is blocked by kill-switch
        assertThat(results)
                .extracting(MatchResult::getPoseId)
                .doesNotContain("lotus");
        // warrior_ii has no kill-switch and should appear
        assertThat(results)
                .extracting(MatchResult::getPoseId)
                .contains("warrior_ii");
    }

    // ── Benefit scoring test ─────────────────────────────────────────────────

    @Test
    @Sql("/match-seed.sql")
    void benefitScoringRanksHigherWeightFirst() {
        MatchRequest request = new MatchRequest();
        request.setHealthFlags(List.of());  // no health flags
        request.setGoals(List.of("flexibility"));
        request.setTopK(10);

        ResponseEntity<MatchResponse> response =
                restTemplate.postForEntity("/api/v1/match", request, MatchResponse.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);

        List<MatchResult> results = response.getBody().getResults();
        // Both poses are returned (no kill-switch triggered)
        // lotus has flexibility weight=2.0, warrior_ii has none → lotus ranks first
        assertThat(results).isNotEmpty();
        assertThat(results.get(0).getPoseId()).isEqualTo("lotus");
    }

    // ── No-goal zero-score test ───────────────────────────────────────────────

    @Test
    @Sql("/match-seed.sql")
    void noMatchingGoalReturnsZeroScorePoses() {
        MatchRequest request = new MatchRequest();
        request.setHealthFlags(List.of());
        request.setGoals(List.of("nonexistent_goal"));
        request.setTopK(5);

        ResponseEntity<MatchResponse> response =
                restTemplate.postForEntity("/api/v1/match", request, MatchResponse.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);

        List<MatchResult> results = response.getBody().getResults();
        // All poses with score 0 are still returned (not filtered out)
        assertThat(results).hasSize(2);
        results.forEach(r -> assertThat(r.getScore()).isEqualTo(0.0));
    }
}
