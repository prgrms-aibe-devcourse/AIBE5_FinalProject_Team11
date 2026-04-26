package club.yogaman.api.studio;

import org.springframework.stereotype.Service;

import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class StudioService {

    /** Earth radius in kilometres (mean radius per WGS-84). */
    private static final double EARTH_RADIUS_KM = 6371.0;

    private final StudioRepository repository;

    public StudioService(StudioRepository repository) {
        this.repository = repository;
    }

    public List<Studio> listAll() {
        return repository.findAll();
    }

    public Optional<Studio> findById(Long id) {
        return repository.findById(id);
    }

    public List<Studio> findByCity(String city) {
        return repository.findByCity(city);
    }

    public Studio create(Studio studio) {
        return repository.save(studio);
    }

    /**
     * Return all studios within {@code radiusKm} kilometres of the given point,
     * sorted by ascending distance. Studios with no coordinates are excluded.
     *
     * @param lat      query latitude  (decimal degrees, WGS-84)
     * @param lng      query longitude (decimal degrees, WGS-84)
     * @param radiusKm search radius in kilometres
     */
    public List<StudioDistance> findNearby(double lat, double lng, double radiusKm) {
        return repository.findAll().stream()
                .filter(s -> s.getLatitude() != null && s.getLongitude() != null)
                .map(s -> new StudioDistance(s, haversineKm(lat, lng, s.getLatitude(), s.getLongitude())))
                .filter(sd -> sd.getDistanceKm() <= radiusKm)
                .sorted(Comparator.comparingDouble(StudioDistance::getDistanceKm))
                .collect(Collectors.toList());
    }

    /**
     * Haversine formula — great-circle distance between two points on a sphere.
     * Returns distance in kilometres.
     */
    private double haversineKm(double lat1, double lng1, double lat2, double lng2) {
        double dLat = Math.toRadians(lat2 - lat1);
        double dLng = Math.toRadians(lng2 - lng1);
        double a = Math.sin(dLat / 2) * Math.sin(dLat / 2)
                + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2))
                * Math.sin(dLng / 2) * Math.sin(dLng / 2);
        return EARTH_RADIUS_KM * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    }
}
