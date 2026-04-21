package club.yogaman.api.pose;

import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Service;

@Service
public class PoseService {

    private final PoseRepository repository;

    public PoseService(PoseRepository repository) {
        this.repository = repository;
    }

    public List<Pose> listPoses() {
        return repository.findAll();
    }

    public Optional<Pose> findPoseById(String poseId) {
        return repository.findById(poseId);
    }
}
