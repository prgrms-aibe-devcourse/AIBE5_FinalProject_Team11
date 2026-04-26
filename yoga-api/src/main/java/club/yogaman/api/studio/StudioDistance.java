package club.yogaman.api.studio;

/**
 * Studio enriched with Haversine distance from the query point.
 * Returned by GET /api/v1/studios/nearby.
 */
public class StudioDistance {

    private final Studio studio;
    private final double distanceKm;

    public StudioDistance(Studio studio, double distanceKm) {
        this.studio = studio;
        this.distanceKm = distanceKm;
    }

    public Studio getStudio() {
        return studio;
    }

    /** Straight-line distance in kilometres (2 decimal places). */
    public double getDistanceKm() {
        return Math.round(distanceKm * 100.0) / 100.0;
    }
}
