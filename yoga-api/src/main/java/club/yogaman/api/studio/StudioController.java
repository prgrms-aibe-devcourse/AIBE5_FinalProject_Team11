package club.yogaman.api.studio;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/studios")
public class StudioController {

    private final StudioService service;

    public StudioController(StudioService service) {
        this.service = service;
    }

    @GetMapping
    public ResponseEntity<List<Studio>> listAll(@RequestParam(required = false) String city) {
        if (city != null) {
            return ResponseEntity.ok(service.findByCity(city));
        }
        return ResponseEntity.ok(service.listAll());
    }

    /**
     * GET /api/v1/studios/nearby?lat=37.5665&lng=126.9780&radius=5
     *
     * Returns studios within {@code radius} km of the given coordinates,
     * sorted by ascending distance. {@code radius} defaults to 10 km.
     *
     * Each result includes the full Studio object plus {@code distanceKm}.
     */
    @GetMapping("/nearby")
    public ResponseEntity<List<StudioDistance>> findNearby(
            @RequestParam double lat,
            @RequestParam double lng,
            @RequestParam(defaultValue = "10") double radius) {
        return ResponseEntity.ok(service.findNearby(lat, lng, radius));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Studio> getById(@PathVariable Long id) {
        return service.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Studio> create(@RequestBody Studio studio) {
        return ResponseEntity.ok(service.create(studio));
    }
}
