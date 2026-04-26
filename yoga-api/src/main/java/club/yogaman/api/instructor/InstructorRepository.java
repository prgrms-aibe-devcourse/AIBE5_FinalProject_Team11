package club.yogaman.api.instructor;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface InstructorRepository extends JpaRepository<Instructor, String> {

    List<Instructor> findByOrderByInstructorTrustScoreDesc();

    List<Instructor> findByCityIgnoreCase(String city);

    List<Instructor> findBySpecialtiesContaining(String specialty);

    @Query("SELECT i FROM Instructor i WHERE i.instructorTrustScore >= :minScore ORDER BY i.instructorTrustScore DESC")
    List<Instructor> findByMinTrustScore(java.math.BigDecimal minScore);
}
