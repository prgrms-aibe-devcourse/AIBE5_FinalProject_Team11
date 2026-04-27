package club.yogaman.api.pose;

import jakarta.persistence.*;

@Entity
@Table(name = "pose_qa")
public class PoseQa {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String poseId;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String question;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String answer;

    @Column(nullable = false)
    private String questionType;

    @Column(nullable = false)
    private String language = "en";

    public Long getId()                    { return id; }
    public void setId(Long id)             { this.id = id; }

    public String getPoseId()              { return poseId; }
    public void setPoseId(String poseId)   { this.poseId = poseId; }

    public String getQuestion()            { return question; }
    public void setQuestion(String q)      { this.question = q; }

    public String getAnswer()              { return answer; }
    public void setAnswer(String a)        { this.answer = a; }

    public String getQuestionType()        { return questionType; }
    public void setQuestionType(String t)  { this.questionType = t; }

    public String getLanguage()            { return language; }
    public void setLanguage(String l)      { this.language = l; }
}
