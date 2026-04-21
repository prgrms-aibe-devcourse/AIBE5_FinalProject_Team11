package club.yogaman.api.session;

import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class SessionService {

    private final SessionRepository repository;

    public SessionService(SessionRepository repository) {
        this.repository = repository;
    }

    public List<Session> listAll() {
        return repository.findAll();
    }

    public List<Session> listByUser(String userId) {
        return repository.findByUserId(userId);
    }

    public Optional<Session> findById(Long id) {
        return repository.findById(id);
    }

    public Session create(Session session) {
        return repository.save(session);
    }
}
