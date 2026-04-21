package club.yogaman.api.studio;

import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class StudioService {

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
}
