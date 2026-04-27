package club.yogaman.api.pose;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface PoseQaRepository extends JpaRepository<PoseQa, Long> {
    List<PoseQa> findByPoseId(String poseId);
    List<PoseQa> findByPoseIdAndLanguage(String poseId, String language);
}
