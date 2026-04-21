package club.yogaman.api.matching;

import java.util.List;

public class MatchResponse {

    private List<MatchResult> results;

    public MatchResponse() {
    }

    public MatchResponse(List<MatchResult> results) {
        this.results = results;
    }

    public List<MatchResult> getResults() {
        return results;
    }

    public void setResults(List<MatchResult> results) {
        this.results = results;
    }
}
